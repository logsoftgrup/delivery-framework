"""Automated checks over captured operational evidence; no operator actions."""
from .oracles import exact, ordered
from .safety import require


def package(config, runtime):
    user = config["config"]["User"]
    assert user and user.split(":")[0] not in ("0", "root"), "root image user"
    hc = runtime["HostConfig"]
    assert hc["ReadonlyRootfs"] is True and hc["Privileged"] is False
    assert hc["NetworkMode"] not in ("host", "container")
    assert not hc["NetworkMode"].startswith("container:")
    assert hc.get("PidMode", "") != "host"
    assert "ALL" in hc["CapDrop"] and not hc.get("CapAdd")
    assert any(x.startswith("no-new-privileges") for x in hc["SecurityOpt"])
    assert hc["Memory"] > 0 and (hc.get("NanoCpus", 0) > 0 or hc.get("CpuQuota", 0) > 0)
    assert hc["RestartPolicy"]["Name"] in ("always", "unless-stopped")
    assert hc["LogConfig"]["Config"].get("max-size") and hc["LogConfig"]["Config"].get("max-file")
    assert "/tmp" in hc["Tmpfs"] and "size=" in hc["Tmpfs"]["/tmp"]
    assert runtime["Mounts"], "No persistent data volume"
    for m in runtime["Mounts"]:
        assert m["Destination"] == "/data" and m["Type"] == "volume", "Unexpected persistent mount"
        assert "docker.sock" not in str(m)
    for env in config["config"].get("Env", []):
        key = env.split("=", 1)[0].upper()
        assert not any(s in key for s in ("PASSWORD", "TOKEN", "SECRET", "PRIVATE_KEY")), "Credential-like environment variable"


def recovery(record):
    require(record.get("candidate") == "C1", "C0/unknown recovery target forbidden")
    required = {"B1-technical", "B2", "T1", "T2", "V1-technical", "A1-technical", "O1-technical", "accepted-TS", "accepted-TC", "harness", "OPS-06"}
    require(required <= record.get("qualifying_reports", {}).keys(), "Incomplete OBS-02 qualifying reports")
    require(all(record["qualifying_reports"][k] for k in required), "Missing report revision")
    require(record.get("qualification_reviewed") is True, "Qualifying subset not independently reviewed")
    require(record.get("schema_version") == record.get("observed_schema_version") == 1, "Incompatible restore schema")
    for k in ("target_manifest_digest", "target_config_digest", "backup_sha256", "configuration_sha256"):
        require(record.get(k) == record.get("observed_" + k) and bool(record.get(k)), "Recovery identity mismatch: " + k)
    for key in ("before", "restored", "after_c1_restoration"):
        ordered(record[key])
    exact(record["restored"], record["before"])
    exact(record["after_c1_restoration"], record["before"])
    require(record.get("original_backup_preserved") is True, "Original backup lost")
    require(record.get("health") == "ok" and record.get("readiness") == "ready", "Recovered service not ready")
    require(record.get("operator") != record.get("independent_verifier"), "Recovery lacks independent verification")


def evidence_roles(record):
    require(record.get("suite_author") != record.get("suite_acceptor"), "Self-authored suite acceptance")
    require(record.get("independent_actor") != record.get("producer_actor"), "Producer evidence relabelled independent")
    require(record.get("human_actor") == "aF9BHPX4C09h2VUawmZCQ2fRaahri14d", "Human verdict lacks authorized actor")
    require(bool(record.get("human_interaction_id")), "No native human verdict")
    require(record.get("screen_reader_method") == "real-observation" and bool(record.get("screen_reader_artifact")), "No real AT evidence")
    require(record.get("fresh_session_before") and record.get("fresh_session_after") and record["fresh_session_before"] != record["fresh_session_after"], "Fresh-session reset unproved")
    require(record.get("native_return_assignee") == record.get("original_producer"), "Original-producer return lost")
