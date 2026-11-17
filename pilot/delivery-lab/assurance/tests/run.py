#!/usr/bin/env python3
"""File-backed runner. Exit 0 automated PASS; 1 assertion FAIL; 2 unavailable;
3 interrupted/unknown. Manual/source acceptance never follows exit 0.
"""
import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from support.results import classify

ROOT = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=("fixture", "qa"), required=True)
    ap.add_argument("--profile", choices=("api", "browser", "all"), default="all")
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--packet", type=Path)
    ap.add_argument("--mutation", default="good")
    ap.add_argument("--select", help="Qualification only: exact pytest node selector or -k expression")
    a = ap.parse_args()
    evidence = a.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)  # Never reuse a stale run.
    if a.kind == "qa" and (a.mutation != "good" or a.select):
        raise SystemExit("QA cannot use mutation/partial qualification selectors")
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    files = {}
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and not any(x in ("__pycache__", ".venv", "artifacts", ".pytest_cache") for x in p.relative_to(ROOT).parts):
            files[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    run = {"state": "prepared", "attempt_id": str(uuid.uuid4()), "kind": a.kind, "profile": a.profile, "mutation": a.mutation, "selection": a.select,
           "suite_sha": git.stdout.strip(), "file_sha256": files, "scenario_sha": "de46dadeb45c76280b0a99630303fb7666798789",
           "actor": os.environ.get("PAPERCLIP_AGENT_ID", "record-required"), "task": os.environ.get("PAPERCLIP_TASK_ID", "record-required"),
           "run": os.environ.get("PAPERCLIP_RUN_ID", "record-required"), "session": os.environ.get("TC_SESSION_ID", "UNKNOWN"),
           "utc": dt.datetime.now(dt.timezone.utc).isoformat(), "python": sys.version, "manual": "PENDING", "acceptance": "NOT DECIDED"}
    (evidence / "run.json").write_text(json.dumps(run, indent=2))
    try:
        for name, version in (("pytest", "8.4.2"), ("playwright", "1.56.0")):
            if a.profile == "api" and name == "playwright":
                continue
            if importlib.metadata.version(name) != version:
                raise RuntimeError("Pinned version missing: " + name)
    except (importlib.metadata.PackageNotFoundError, RuntimeError) as exc:
        result = {"outcome": "UNAVAILABLE", "reason": str(exc), "evidence": str(evidence), "executed": 0}
        (evidence / "summary.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result)[:3000])
        return 2
    tests = ["cases/test_api.py", "cases/test_security.py"] if a.profile == "api" else ["cases/test_browser.py"] if a.profile == "browser" else ["cases"]
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=short", "--strict-markers", *tests, "--kind", a.kind, "--mutation", a.mutation, "--evidence", str(evidence)]
    if a.packet:
        cmd += ["--packet", str(a.packet.resolve())]
    if a.select:
        cmd += ["-k", a.select]
    run["state"] = "dispatch-started"
    run["command"] = cmd
    (evidence / "run.json").write_text(json.dumps(run, indent=2))
    with (evidence / "stdout.log").open("wb") as out, (evidence / "stderr.log").open("wb") as err:
        result = subprocess.run(cmd, cwd=ROOT, stdout=out, stderr=err)
    run["state"] = "response-confirmed"
    run["exit"] = result.returncode
    (evidence / "run.json").write_text(json.dumps(run, indent=2))
    report_path = evidence / "results.json"
    report = json.loads(report_path.read_text()) if report_path.is_file() else {}
    called = [r for r in report.get("results", []) if r.get("phase") == "call"]
    collected_path = evidence / "collected.json"
    collected = json.loads(collected_path.read_text()) if collected_path.is_file() else []
    outcome = classify(result.returncode, report, collected, run["attempt_id"])
    summary = {"outcome": outcome, "kind": a.kind, "collected": report.get("collected", 0), "calls": len(called), "manual": "PENDING", "acceptance": "NOT DECIDED", "evidence": str(evidence)}
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2))
    run["state"] = "evidence-saved"
    (evidence / "run.json").write_text(json.dumps(run, indent=2))
    print(json.dumps(summary))
    return {"PASS": 0, "FAIL": 1, "UNAVAILABLE": 2, "UNKNOWN": 3}[outcome]


if __name__ == "__main__":
    sys.exit(main())
