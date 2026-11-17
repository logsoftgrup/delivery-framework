#!/usr/bin/env python3
"""Record exact suite file identities; publication commit is recorded externally."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
EXCLUDED={".venv","__pycache__",".pytest_cache","artifacts"}
files={}
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or p.name=="manifest.json" or EXCLUDED.intersection(p.relative_to(ROOT).parts):
        continue
    if p.is_symlink():
        raise SystemExit("Suite input symlink forbidden: "+str(p))
    data=p.read_bytes()
    files[str(p.relative_to(ROOT))]={"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
manifest={"schema":"delivery-lab-test-suite.v1","candidate":"TC-D1","status":"DRAFT_NOT_RELEASED","original_producer":"ce8e0a2f-a532-45cb-abeb-a3937e9be71e","source_task":"LOGA-23","independent_examinations":["LOGA-28","LOGA-29"],"repository":"https://github.com/logsoftgrup/delivery-framework.git","branch_locator_only":"assurance/phase-b","baseline_commit":"a76f458655c9bd2a8ef95562651e0c9155f6a878","scenario_commit":"de46dadeb45c76280b0a99630303fb7666798789","input_packet_revision":"ea3ef167-8a13-4cd6-80f2-a3d88cf0d0e8","runtime":{"python":"3.12.3","platform":"linux-x86_64","pytest":"8.4.2","playwright":"1.56.0","dependency_lock":"UNAVAILABLE: permitted wheel/browser retrieval required","browser_revision":"UNVERIFIED"},"acceptance":"NOT_DECIDED","required_c0_sentinel":"API-05: 422 E-LENGTH and unchanged complete tuple snapshot; ordinary failure if violated","files":files}
(ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({"files":len(files),"status":manifest["status"],"manifest_sha256":hashlib.sha256((ROOT/"manifest.json").read_bytes()).hexdigest()}))
