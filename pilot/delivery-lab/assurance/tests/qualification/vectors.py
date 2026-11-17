#!/usr/bin/env python3
"""HAR-04/08–12 offline discriminator vectors. No service/Docker mutations.

Synthetic records prove assertion behavior only. The independent verifier must
run these in TC.V; an author run remains a producer check.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from support.client import Unavailable
from support.oracles import SPEC, added, item, unchanged
from support.results import classify
from support.safety import validate_packet
from support.evidence_oracles import recovery, evidence_roles, package


def execute(destination):
    destination.mkdir(parents=True, exist_ok=False)
    outcomes = []

    def vector(key, function, should_reject):
        caught = None
        try:
            function()
        except (AssertionError, Unavailable, ValueError) as exc:
            caught = {"type": type(exc).__name__, "reason": str(exc)}
        good = (caught is not None) == should_reject
        outcomes.append({"id": key, "expected": "reject" if should_reject else "accept", "observed": caught or "accepted", "qualification": "PASS" if good else "FAIL", "writes_to_services": 0})

    rows = copy.deepcopy(SPEC["states"]["F-SEED"]["items"])
    vector("HAR-04/good-tuples", lambda: unchanged(rows, copy.deepcopy(rows)), False)
    for key, mutate in [("replace-same-count", lambda r: r[0].update(name="wrong")), ("lost-row", lambda r: r.pop()), ("regenerated-id", lambda r: r[0].update(id="00000000-0000-4000-8000-999999999999"))]:
        bad = copy.deepcopy(rows); mutate(bad)
        vector("HAR-04/" + key, lambda b=bad: unchanged(rows, b), True)
    for value in ["2026-02-30T12:00:00.000000Z", "2026-11-17T12:00:00Z"]:
        vector("HAR-04/invalid-time/" + value, lambda v=value: item(rows[0] | {"created_at": v}), True)

    files = {}
    for name in ("archive", "configuration", "operator", "manifest", "image_config"):
        path = destination / (name + ".synthetic")
        path.write_bytes(("synthetic-" + name).encode())
        files[name] = (str(path), hashlib.sha256(path.read_bytes()).hexdigest())
    resources = lambda env: {k: {"id": env + "-" + k, "name": "delivery-lab-" + env + "-" + {"container":"app","network":"net","volume":"data"}[k], "labels": {"com.logsoftgrup.pilot":"delivery-lab","com.logsoftgrup.environment":env}} for k in ("container","volume","network")}
    p = {"kind":"delivery-lab-qa-execution-v1","environment":"qa","project":"delivery-lab-qa","scenario_sha":"de46dadeb45c76280b0a99630303fb7666798789","suite_sha":"a"*40,"app_sha":"b"*40,"exclusive_synthetic_writer":True,"base_url":"http://127.0.0.1:18081","published_host":"127.0.0.1","published_port":18081,"qa_resources":resources("qa"),"review_resources":resources("review")}
    for name in ("authorization_ref","route_evidence_ref","independent_identity_ref","fixture_method_review_ref"):
        p[name] = "synthetic-record-not-real-authorization"
    for name, (path, sha) in files.items():
        p[name+"_path"] = path
        if name in ("archive","configuration","operator"):
            p[name+"_sha256"] = sha
    p["image_manifest_digest"]="sha256:"+files["manifest"][1]
    p["image_config_digest"]="sha256:"+files["image_config"][1]
    p["observed_image_config_digest"]=p["image_config_digest"]
    p["observed_configuration_sha256"]=p["configuration_sha256"]
    vector("HAR-08/HAR-09/good-record", lambda: validate_packet(p,"a"*40), False)
    mutations = {
        "review":lambda p:p.update(environment="review"),
        "unknown-url":lambda p:p.update(base_url=""),
        "wrong-label":lambda p:p["qa_resources"]["container"]["labels"].update({"com.logsoftgrup.environment":"review"}),
        "shared-volume":lambda p:p["qa_resources"]["volume"].update(id=p["review_resources"]["volume"]["id"]),
        "shared-network":lambda p:p["qa_resources"]["network"].update(id=p["review_resources"]["network"]["id"]),
        "mutable-tag":lambda p:p.update(image_manifest_digest="delivery-lab:latest"),
        "other-image-same-version":lambda p:p.update(observed_image_config_digest="sha256:"+"0"*64),
        "archive-corruption":lambda p:p.update(archive_sha256="0"*64),
        "stale-suite":lambda p:p.update(suite_sha="c"*40),
    }
    for key, mutate in mutations.items():
        bad=copy.deepcopy(p); mutate(bad)
        vector("HAR-08/HAR-09/"+key, lambda b=bad: validate_packet(b,"a"*40), True)

    from fixture.records import package_records
    config,runtime=package_records()
    vector("HAR-08/good-package-record",lambda:package(config,runtime),False)
    for key,mutate in [
        ("root-user",lambda c,r:c["config"].update(User="0:0")),
        ("socket-mount",lambda c,r:r["Mounts"].append({"Type":"bind","Destination":"/var/run/docker.sock"})),
        ("host-network",lambda c,r:r["HostConfig"].update(NetworkMode="host")),
        ("other-container-network",lambda c,r:r["HostConfig"].update(NetworkMode="container:unrelated")),
        ("credential-env",lambda c,r:c["config"]["Env"].append("SYNTHETIC_TOKEN=not-a-real-secret")),
    ]:
        c,r=copy.deepcopy(config),copy.deepcopy(runtime);mutate(c,r)
        vector("HAR-08/"+key,lambda c=c,r=r:package(c,r),True)

    good_report={"attempt_id":"current","collected":1,"results":[{"id":"API-05/c0-sentinel","phase":"call","outcome":"passed"}]}
    def result(expected, code, report, ids, attempt="current"):
        assert classify(code, report, ids, attempt)==expected
    vector("HAR-10/good-result",lambda:result("PASS",0,good_report,["API-05/c0-sentinel"]),False)
    for key, report, ids, code in [
        ("zero-collected",{"attempt_id":"current","collected":0,"results":[]},[],0),
        ("stale-report",good_report|{"attempt_id":"old"},["API-05/c0-sentinel"],0),
        ("omitted-required",good_report,["API-05/c0-sentinel","required-extra"],0),
        ("missing-artifact",{},["API-05/c0-sentinel"],0),
        ("crash",good_report,["API-05/c0-sentinel"],-9),
        ("skip",good_report|{"results":[{"id":"API-05/c0-sentinel","phase":"call","outcome":"skipped"}]},["API-05/c0-sentinel"],0),
    ]:
        vector("HAR-10/"+key,lambda r=report,i=ids,c=code:result("PASS",c,r,i),True)
    for category in ("FAIL","UNAVAILABLE","UNKNOWN"):
        report=good_report|{"results":[{"id":"API-05/c0-sentinel","phase":"call","outcome":"failed","classification":category}]}
        vector("HAR-10/swallowed-"+category,lambda r=report:result("PASS",0,r,["API-05/c0-sentinel"]),True)

    rec={"candidate":"C1","qualifying_reports":{k:"synthetic-revision" for k in ["B1-technical","B2","T1","T2","V1-technical","A1-technical","O1-technical","accepted-TS","accepted-TC","harness","OPS-06"]},"qualification_reviewed":True,"schema_version":1,"observed_schema_version":1,"before":rows,"restored":copy.deepcopy(rows),"after_c1_restoration":copy.deepcopy(rows),"original_backup_preserved":True,"health":"ok","readiness":"ready","operator":"synthetic-operator","independent_verifier":"synthetic-observer"}
    for k in ("target_manifest_digest","target_config_digest","backup_sha256","configuration_sha256"):
        rec[k]=rec["observed_"+k]="synthetic-matching-digest"
    vector("HAR-11/good-record",lambda:recovery(rec),False)
    for k,v in [("candidate","C0"),("qualifying_reports",{}),("observed_schema_version",2),("observed_backup_sha256","mismatch"),("restored",rows[:-1])]:
        vector("HAR-11/"+k,lambda k=k,v=v:recovery(rec|{k:v}),True)
    roles={"suite_author":"assurance","suite_acceptor":"engineer","independent_actor":"assurance","producer_actor":"engineer","human_actor":"aF9BHPX4C09h2VUawmZCQ2fRaahri14d","human_interaction_id":"synthetic","screen_reader_method":"real-observation","screen_reader_artifact":"synthetic-reference-only","fresh_session_before":"s1","fresh_session_after":"s2","native_return_assignee":"engineer","original_producer":"engineer"}
    vector("HAR-12/good-record-shape",lambda:evidence_roles(roles),False)
    for k,v in [("suite_acceptor","assurance"),("independent_actor","engineer"),("human_actor","agent"),("screen_reader_method","dom-inference"),("fresh_session_after","s1"),("native_return_assignee","wrong")]:
        vector("HAR-12/"+k,lambda k=k,v=v:evidence_roles(roles|{k:v}),True)
    report={"kind":"offline-synthetic-harness-vectors","vectors":outcomes,"source_acceptance":"NOT DECIDED","manual":"PENDING"}
    (destination/"vectors.json").write_text(json.dumps(report,indent=2))
    failed=[x["id"] for x in outcomes if x["qualification"]!="PASS"]
    print(json.dumps({"vectors":len(outcomes),"failed":failed,"evidence":str(destination)}))
    return 1 if failed else 0


if __name__=="__main__":
    sys.exit(execute(Path(sys.argv[1]).resolve()))
