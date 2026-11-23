"""Offline byte/graph verifier. Does not install, launch, or accept a dependency bundle."""
import argparse
import hashlib
import json
import re
import tarfile
from pathlib import Path


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def verify(archive, expected_sha, source, kind, destination):
    require(re.fullmatch(r"[0-9a-f]{64}", expected_sha), "invalid archive hash")
    require(re.fullmatch(r"[0-9a-f]{40}", source), "invalid source SHA")
    require(sha(archive) == expected_sha, "archive checksum mismatch")
    require(not destination.exists(), "destination must be new")
    root_name = kind.upper()
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        require(len(members) <= 100_000 and sum(x.size for x in members) <= 4 * 1024**3, "archive bounds exceeded")
        names = set()
        for member in members:
            name = Path(member.name)
            require(not name.is_absolute() and ".." not in name.parts and name.parts[0] == root_name,
                    "archive path escaped bundle")
            require(member.name not in names and (member.isdir() or member.isfile()), "duplicate or unsafe archive member")
            require(not member.mode & ~0o777, "special permission bits rejected")
            names.add(member.name)
        destination.mkdir(parents=True)
        for member in members:
            path = destination / member.name
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source_file, path.open("wb") as target:
                    for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
                        target.write(chunk)
            path.chmod(member.mode)
    root = destination / root_name
    manifest = read(root / "bundle-manifest.json")
    require(manifest["schema"] == "delivery-lab.dependency-bundle.v1" and manifest["kind"] == kind, "bundle identity mismatch")
    expected = {}
    for row in manifest["files"]:
        path = root / row["path"]
        require(path.resolve().is_relative_to(root.resolve()) and row["path"] not in expected, "unsafe manifest path")
        require(path.is_file() and path.stat().st_size == row["bytes"] and sha(path) == row["sha256"], "payload checksum mismatch")
        require(oct(path.stat().st_mode & 0o777) == row["mode"], "payload mode mismatch")
        expected[row["path"]] = row
    actual = {x.relative_to(root).as_posix() for x in root.rglob("*") if x.is_file()}
    require(actual == set(expected) | {"bundle-manifest.json"}, "payload inventory is incomplete")
    require(read(root / "provenance.json")["source_commit"] == source, "source provenance mismatch")
    for lock in ("requirements.lock", "toolchain.lock"):
        for line in (root / lock).read_text().splitlines():
            require(re.fullmatch(r"[A-Za-z0-9_.-]+==[A-Za-z0-9_.+!-]+ --hash=sha256:[0-9a-f]{64}", line), "unsafe or unhashed lock entry")
    if kind == "app":
        image = read(root / "base-image.json")
        require("sha256:" + sha(root / "registry-index.json") == image["registry_index_digest"], "registry index mismatch")
        blobs = root / "base-oci/blobs/sha256"
        platform_manifest = blobs / image["platform_manifest_digest"].split(":")[1]
        require("sha256:" + sha(platform_manifest) == image["platform_manifest_digest"], "image manifest mismatch")
        child = read(platform_manifest)
        require(child["config"]["digest"] == image["config_digest"], "image config reference mismatch")
        for row in [child["config"], *child["layers"]]:
            blob = blobs / row["digest"].split(":")[1]
            require(blob.stat().st_size == row["size"] and "sha256:" + sha(blob) == row["digest"], "OCI blob mismatch")
    return {"kind": kind, "payload_files_verified": len(expected), "archive_sha256": expected_sha,
            "source_commit": source, "result": "BYTES_VERIFIED; independent target/offline/runtime/retention verification still required"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--kind", choices=("app", "test"), required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive, args.sha256, args.source, args.kind, args.destination)))
