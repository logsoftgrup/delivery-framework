"""Synthetic metadata used only to qualify evidence validators."""
import copy
from .server import DATA


def package_records():
    config={"config":{"User":"10001:10001","Env":["LANG=C.UTF-8"]}}
    runtime={"HostConfig":{"ReadonlyRootfs":True,"Privileged":False,"NetworkMode":"delivery-lab-qa-net","PidMode":"","CapDrop":["ALL"],"CapAdd":[],"SecurityOpt":["no-new-privileges:true"],"Memory":268435456,"NanoCpus":1000000000,"RestartPolicy":{"Name":"unless-stopped"},"LogConfig":{"Config":{"max-size":"10m","max-file":"3"}},"Tmpfs":{"/tmp":"rw,size=16m"}},"Mounts":[{"Destination":"/data","Type":"volume","Name":"delivery-lab-qa-data"}]}
    return config,runtime


def recovery_record():
    rows=copy.deepcopy(DATA["states"]["F-SEED"]["items"])
    r={"candidate":"C1","qualifying_reports":{k:"synthetic-qualification-revision" for k in ["B1-technical","B2","T1","T2","V1-technical","A1-technical","O1-technical","accepted-TS","accepted-TC","harness","OPS-06"]},"qualification_reviewed":True,"schema_version":1,"observed_schema_version":1,"before":rows,"restored":copy.deepcopy(rows),"after_c1_restoration":copy.deepcopy(rows),"original_backup_preserved":True,"health":"ok","readiness":"ready","operator":"synthetic-operator","independent_verifier":"synthetic-independent"}
    for key in ("target_manifest_digest","target_config_digest","backup_sha256","configuration_sha256"):
        r[key]=r["observed_"+key]="synthetic-record-value"
    return r
