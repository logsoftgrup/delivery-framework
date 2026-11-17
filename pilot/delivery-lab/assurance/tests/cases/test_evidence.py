import json
from pathlib import Path
import sqlite3
import pytest
from support.client import Unavailable
from support.oracles import exact
from support.evidence_oracles import package, recovery
from support.safety import digest, require


def test_PKG02_metadata_confinement(client):
    if client.identity.get("classification") == "synthetic-contract-double":
        from fixture.records import package_records
        config,runtime=package_records()
    else:
        packet=client.identity
        config=json.loads(Path(packet["image_config_path"]).read_text())
        entry=packet.get("runtime_inspect")
        if not entry:
            raise Unavailable("PKG-02 requires independent exact running-container inspect bytes")
        require(digest(entry["path"])==entry["sha256"],"Changed inspect evidence")
        runtime=json.loads(Path(entry["path"]).read_text())
        if isinstance(runtime,list):
            require(len(runtime)==1,"Inspect must contain only the authorized pilot container")
            runtime=runtime[0]
        require(runtime["Id"]==packet["qa_resources"]["container"]["id"],"Inspect names wrong container")
    client.save("package-input",{"config":config,"runtime":runtime})
    package(config,runtime)


def test_OPS06_OPS08_OPS09_backup_and_recovery(client):
    if client.identity.get("classification") == "synthetic-contract-double":
        from fixture.records import recovery_record
        record=recovery_record()
        path=client.evidence/"synthetic-backup.sqlite3"
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE items(id TEXT PRIMARY KEY,name TEXT NOT NULL,created_at TEXT NOT NULL)")
            db.executemany("INSERT INTO items VALUES(:id,:name,:created_at)",record["before"])
        record["backup_path"]=str(path)
        record["backup_sha256"]=record["observed_backup_sha256"]=digest(path)
    else:
        entry=client.identity.get("recovery_record")
        if not entry:
            raise Unavailable("OPS-06/08/09 needs exact operator records and independent recovered observations")
        require(digest(entry["path"])==entry["sha256"],"Changed recovery record")
        record=json.loads(Path(entry["path"]).read_text())
    client.save("recovery-input",record)
    require(digest(record["backup_path"])==record["backup_sha256"],"Backup checksum mismatch; never restore")
    with sqlite3.connect(Path(record["backup_path"]).resolve().as_uri()+"?mode=ro",uri=True) as db:
        exact(db.execute("PRAGMA integrity_check").fetchall(),[("ok",)])
        rows=[dict(zip(("id","name","created_at"),r)) for r in db.execute("SELECT id,name,created_at FROM items ORDER BY created_at,id")]
    exact(rows,record["before"])
    recovery(record)
