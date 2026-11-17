#!/usr/bin/env python3
"""Independent TC.V entrypoint: every bad variant in a separate fresh run."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MUTATIONS=[
    ("HAR-01","wrong-status","api","test_API_UNI and trim"),
    ("HAR-01","extra-key","api","test_API_UNI and trim"),
    ("HAR-01","wrong-error","api","test_API_UNI and missing"),
    ("HAR-02","c0-accept","api","test_API_UNI and c0-sentinel"),
    ("HAR-02","reject-writes","api","test_API_UNI and c0-sentinel"),
    ("HAR-03","utf16-count","api","test_API_UNI and astral"),
    ("HAR-03","broad-trim","api","test_API_UNI and UNI-05"),
    ("HAR-04","wrong-order","api","test_DATA02"),
    ("HAR-04","replace-old","api","test_API_UNI and trim"),
    ("HAR-04","invalid-time","api","test_API_UNI and trim"),
    ("HAR-05","automatic-retry","browser","test_UI07_UI08_UI09"),
    ("HAR-05","500-definite","browser","test_UI07_UI08_UI09 and internal"),
    ("HAR-05","reenable-failed-get","browser","test_UI09_initial"),
    ("HAR-06","innerhtml","browser","test_UI10 and markup"),
    ("HAR-06","missing-label","browser","test_UI01_UI04"),
    ("HAR-06","detached-error","browser","test_UI06_UI12 and 422"),
    ("HAR-06","duplicate-form","browser","test_UI01_UI04"),
    ("HAR-06","clipped-error","browser","test_UI06_UI12 and 422"),
    ("HAR-07","lost-row","api","test_DATA04"),
    ("HAR-07","reseed-empty","api","test_DATA03 and F-EMPTY"),
    ("HAR-07","get-writes","api","test_API_UNI and trim"),
]


def main():
    destination=Path(sys.argv[1]).resolve()
    destination.mkdir(parents=True,exist_ok=False)
    receipts=[]
    def run(name,profile,mutation="good",selection=None,expected="PASS"):
        folder=destination/name
        cmd=[sys.executable,str(ROOT/"run.py"),"--kind","fixture","--profile",profile,"--mutation",mutation,"--evidence",str(folder)]
        if selection:cmd += ["--select",selection]
        with (destination/(name+".stdout.log")).open("wb") as out,(destination/(name+".stderr.log")).open("wb") as err:
            p=subprocess.run(cmd,stdout=out,stderr=err)
        summary=json.loads((folder/"summary.json").read_text()) if (folder/"summary.json").is_file() else {"outcome":"UNKNOWN"}
        ok=summary["outcome"]==expected and p.returncode==(0 if expected=="PASS" else 1)
        receipts.append({"name":name,"command":cmd,"exit":p.returncode,"expected":expected,"summary":summary,"qualified":ok})
        (destination/"qualification.json").write_text(json.dumps({"receipts":receipts,"complete":False},indent=2))
        return ok
    if not run("good-full","all"):
        print(json.dumps({"qualification":"UNAVAILABLE_OR_FAIL","evidence":str(destination),"reason":"Good full suite did not pass; no bad fixture receives credit"}));return 2
    for i,(har,mutation,profile,selection) in enumerate(MUTATIONS):
        run(f"{i:02}-{har}-{mutation}",profile,mutation,selection,"FAIL")
        run(f"{i:02}-{har}-good-restored",profile,"good",selection)
    with (destination/"vectors.stdout.log").open("wb") as out,(destination/"vectors.stderr.log").open("wb") as err:
        v=subprocess.run([sys.executable,str(ROOT/"qualification/vectors.py"),str(destination/"vectors")],stdout=out,stderr=err)
    ok=all(r["qualified"] for r in receipts) and v.returncode==0
    report={"receipts":receipts,"vectors_exit":v.returncode,"automated_qualification":"PASS" if ok else "FAIL","manual_HAR06_HAR12":"PENDING","complete":True,"source_acceptance":"NOT DECIDED"}
    (destination/"qualification.json").write_text(json.dumps(report,indent=2))
    print(json.dumps({"automated_qualification":report["automated_qualification"],"manual":"PENDING","evidence":str(destination)}))
    return 0 if ok else 1


if __name__=="__main__":sys.exit(main())
