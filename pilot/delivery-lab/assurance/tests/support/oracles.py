"""Assertions from accepted TS-3; never import the fixture or application."""
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "spec/fixtures.json").read_text())
ERRORS = SPEC["error_oracles"] | {
    "E-HOST": {"status": 403, "body": {"error": {"code": "host_not_allowed", "message": "Host is not allowed.", "fields": []}}},
    "E-ORIGIN": {"status": 403, "body": {"error": {"code": "origin_not_allowed", "message": "Origin is not allowed.", "fields": []}}},
}


def exact(actual, expected):
    """Python's True == 1 must not let an invalid JSON type through."""
    assert type(actual) is type(expected), (type(actual).__name__, type(expected).__name__)
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), (actual, expected)
        for k in expected:
            exact(actual[k], expected[k])
    elif isinstance(expected, list):
        assert len(actual) == len(expected), (actual, expected)
        for a, e in zip(actual, expected):
            exact(a, e)
    else:
        assert actual == expected, (actual, expected)


def item(value, name=None):
    assert type(value) is dict and set(value) == {"id", "name", "created_at"}, value
    assert all(type(value[k]) is str for k in value), value
    assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", value["id"]), value
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z", value["created_at"]), value
    dt.datetime.strptime(value["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
    assert not any(0xD800 <= ord(c) <= 0xDFFF for c in value["name"])
    if name is not None:
        exact(value["name"], name)


def ordered(rows):
    assert type(rows) is list
    for row in rows:
        item(row)
    assert len({r["id"] for r in rows}) == len(rows), "duplicate ID"
    exact(rows, sorted(rows, key=lambda r: (r["created_at"], r["id"])))


def unchanged(before, after):
    exact(after, before)


def added(before, after, result, name):
    item(result, name)
    ordered(after)
    assert result["id"] not in {r["id"] for r in before}
    exact([r for r in after if r["id"] != result["id"]], before)
    exact([r for r in after if r["id"] == result["id"]], [result])


def headers(response, denial=False, json_body=True):
    h = response["headers"]
    assert "no-store" in {s.strip().lower() for s in h.get("cache-control", "").split(",")}, h
    if json_body:
        assert h.get("content-type", "").split(";")[0].strip().lower() == "application/json", h
    if denial:
        assert not any(k.lower().startswith("access-control-allow-") for k in h), h


def error(response, ref, head=False):
    oracle = ERRORS[ref]
    assert response["status"] == oracle["status"], response
    headers(response, denial=ref in ("E-HOST", "E-ORIGIN"))
    if head:
        assert response["raw_hex"] == "", response
    else:
        exact(response["json"], oracle["body"])


def method_error(response):
    error(response, "E-METHOD")
    methods = {s.strip().upper() for s in response["headers"].get("allow", "").split(",")}
    assert {"GET", "POST"} <= methods <= {"GET", "POST", "HEAD"}, methods


def version(response, identity):
    assert response["status"] == 200
    headers(response)
    body = response["json"]
    assert set(body) == {"source_commit", "build_id", "contract_version", "schema_version"}, body
    exact(body, {"source_commit": identity["app_sha"], "build_id": identity["build_id"], "contract_version": "1", "schema_version": 1})
