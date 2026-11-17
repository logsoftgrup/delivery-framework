"""Fail closed before a real QA request or fixture operation."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit
from .client import Unavailable


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def require(condition, why):
    if not condition:
        raise Unavailable(why)


def validate_packet(packet, suite_sha):
    require(packet.get("kind") == "delivery-lab-qa-execution-v1", "Not an authorized QA packet")
    require(packet.get("environment") == "qa", "Review/unknown target forbidden")
    require(packet.get("project") == "delivery-lab-qa", "Unexpected QA project")
    require(packet.get("scenario_sha") == "de46dadeb45c76280b0a99630303fb7666798789", "Stale scenario")
    require(packet.get("suite_sha") == suite_sha, "Stale suite")
    for key in ("app_sha", "suite_sha"):
        require(re.fullmatch(r"[0-9a-f]{40}", packet.get(key, "")), "Full commit required: " + key)
    for key in ("image_manifest_digest", "image_config_digest"):
        require(re.fullmatch(r"sha256:[0-9a-f]{64}", packet.get(key, "")), "Immutable OCI digest required: " + key)
    for key in ("archive_sha256", "configuration_sha256", "operator_sha256"):
        require(re.fullmatch(r"[0-9a-f]{64}", packet.get(key, "")), "SHA-256 required: " + key)
    require(packet.get("exclusive_synthetic_writer") is True, "Exclusive synthetic fixture control missing")
    for key in ("authorization_ref", "route_evidence_ref", "independent_identity_ref", "fixture_method_review_ref"):
        require(bool(packet.get(key)), "Missing reviewed prerequisite: " + key)
    url = urlsplit(packet.get("base_url", ""))
    require(url.scheme == "http" and url.hostname is not None and url.username is None and url.password is None and url.path in ("", "/") and not url.query and not url.fragment, "Invalid actual QA URL")
    route_allowed = url.hostname in ("127.0.0.1", "localhost") and url.port == 18081
    if packet.get("verified_qa_alias"):
        route_allowed |= url.hostname == packet["verified_qa_alias"] and url.port == 8000
    require(route_allowed, "Actual route is neither published QA nor a verified single QA alias")
    require(packet.get("published_host") == "127.0.0.1" and packet.get("published_port") == 18081, "Unapproved publication")
    qa, review = packet.get("qa_resources", {}), packet.get("review_resources", {})
    for kind in ("container", "volume", "network"):
        q, r = qa.get(kind, {}), review.get(kind, {})
        require(q.get("id") and r.get("id") and q["id"] != r["id"], "QA/review identity or isolation gap: " + kind)
        require(q.get("name") == "delivery-lab-qa-" + {"container":"app", "volume":"data", "network":"net"}[kind], "Unexpected QA resource name")
        require(q.get("labels", {}).get("com.logsoftgrup.pilot") == "delivery-lab" and q.get("labels", {}).get("com.logsoftgrup.environment") == "qa", "Wrong QA owner/environment labels")
    # Verify the exact observed input files before invoking any operator hook.
    for field, hashfield in (("archive_path", "archive_sha256"), ("configuration_path", "configuration_sha256"), ("operator_path", "operator_sha256")):
        require(Path(packet.get(field, "")).is_file(), "Missing input: " + field)
        require(digest(packet[field]) == packet[hashfield], "Changed input: " + field)
    for field, expected in (("manifest_path", packet["image_manifest_digest"]), ("image_config_path", packet["image_config_digest"])):
        require(Path(packet.get(field, "")).is_file() and "sha256:" + digest(packet[field]) == expected, "OCI bytes do not match: " + field)
    require(packet.get("observed_image_config_digest") == packet["image_config_digest"], "Running image differs")
    require(packet.get("observed_configuration_sha256") == packet["configuration_sha256"], "Running configuration differs")
    return packet


class OperatorController:
    """Reviewed external operator adapter; no shell evaluation or automatic install.

    The task packet must identify/hash an approved adapter before this is usable.
    It owns actual DB fixtures, causal faults, restart and dispatch instrumentation.
    This interface alone is NOT evidence that an app adapter exists or is accepted.
    """
    def __init__(self, packet, evidence):
        self.packet = packet
        self.evidence = Path(evidence)
        self.counter = 0

    def perform(self, operation, **args):
        require(operation in {"reset", "configure", "observe", "process_restart", "container_restart", "dispatch"}, "Unknown operator operation")
        self.counter += 1
        prefix = self.evidence / f"operator-{self.counter:05}"
        request = {"operation": operation, "arguments": args, "packet": self.packet}
        request_path = prefix.with_suffix(".request.json")
        request_path.write_text(json.dumps(request, ensure_ascii=True))
        require(digest(self.packet["operator_path"]) == self.packet["operator_sha256"], "Operator changed after gate")
        with prefix.with_suffix(".stdout.json").open("wb") as out, prefix.with_suffix(".stderr.log").open("wb") as err:
            try:
                result = subprocess.run([self.packet["operator_path"], str(request_path)], stdout=out, stderr=err, timeout=120)
            except subprocess.TimeoutExpired as exc:
                raise Unavailable("Operator dispatch started; outcome UNKNOWN. Reconcile before retry.") from exc
        require(result.returncode == 0, "Operator failed; reconcile saved receipts before retry")
        receipt = json.loads(prefix.with_suffix(".stdout.json").read_text())
        require(receipt.get("operation") == operation and receipt.get("kind") == "delivery-lab-qa-operation-v1", "Unbound operator receipt")
        require(receipt.get("qa_resources") == self.packet["qa_resources"], "Operator resource identity changed")
        return receipt
