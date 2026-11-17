import json
import pytest
from support.oracles import SPEC, added, error, exact, headers, method_error, unchanged, version
from support.parameters import API_CASES


@pytest.mark.parametrize("case", API_CASES, ids=lambda c: c.key)
def test_API_UNI(client, case):
    client.reset()
    before = client.snapshot()
    r = client.request(case.method, case.path, case.body, case.headers)
    after = client.snapshot()  # Retain changes even when status assertion fails.
    if case.error:
        error(r, case.error)
        unchanged(before, after)
    else:
        assert r["status"] == 201, r
        headers(r)
        added(before, after, r["json"], case.name)
        unchanged(after, client.snapshot())


def test_API14_DATA01_duplicates(client):
    client.reset()
    s0 = client.snapshot()
    responses = []
    for _ in range(2):
        r = client.request("POST", body={"name": "Pilot notebook"})
        s1 = client.snapshot()
        assert r["status"] == 201
        added(s0, s1, r["json"], "Pilot notebook")
        responses.append(r["json"])
        s0 = s1
    assert responses[0]["id"] != responses[1]["id"]
    exact(responses[0], next(x for x in client.snapshot() if x["id"] == responses[0]["id"]))


def test_API15_readonly(client):
    client.reset()
    before = client.snapshot()
    error(client.request(path="/api/no-such-route"), "E-NOTFOUND")
    for method in ("PUT", "OPTIONS"):
        method_error(client.request(method, body={"name": "A"}))
    unchanged(before, client.snapshot())


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_API16_storage(client, method):
    client.reset()
    before = client.snapshot()
    client.control("configure", fault="storage")
    r = client.request(method, body={"name": "Pilot notebook"} if method == "POST" else None)
    proof = client.control("observe")
    client.control("configure", fault=None)
    after = client.snapshot()
    error(r, "E-STORAGE")
    unchanged(before, after)
    assert proof.get("events") is not None, "Missing fault causality evidence"


@pytest.mark.parametrize("fault,delta", [("internal-pre", 0), ("internal-post", 1)])
def test_API17_internal(client, fault, delta):
    client.reset()
    before = client.snapshot()
    client.control("configure", fault=fault)
    r = client.request("POST", body={"name": "Pilot notebook"})
    proof = client.control("observe")
    client.control("configure", fault=None)
    after = client.snapshot()
    error(r, "E-INTERNAL")
    if delta:
        new = [x for x in after if x["id"] not in {a["id"] for a in before}]
        assert len(new) == 1
        added(before, after, new[0], "Pilot notebook")
        assert any(x["event"] == "committed" and x["id"] == new[0]["id"] for x in proof["events"])
    else:
        unchanged(before, after)
        assert any(x["event"] == "internal-before-commit" for x in proof["events"])


def test_DATA02_equal_time(client):
    client.reset("F-ORDER")
    rows = client.snapshot()
    exact(rows, SPEC["states"]["F-ORDER"]["expected_items"])
    unchanged(rows, client.snapshot())


@pytest.mark.parametrize("state", ["F-UNINITIALIZED", "F-EMPTY", "F-NONEMPTY"])
def test_DATA03_seed(client, state):
    proof = client.reset(state)
    before = client.snapshot()
    if state == "F-UNINITIALIZED":
        assert [x["name"] for x in before] == ["Sample notebook", "Sample cable", "Sample adapter"]
        assert proof["initialized"] is True
    else:
        exact(before, SPEC["states"][state]["items"])
    unchanged(before, client.snapshot())
    for kind in ("process_restart", "container_restart"):
        client.control(kind)
        unchanged(before, client.snapshot())


@pytest.mark.parametrize("kind", ["process_restart", "container_restart"])
def test_DATA04_acknowledged_restart(client, kind):
    client.reset()
    old = client.snapshot()
    r = client.request("POST", body={"name": "Pilot notebook"})
    before = client.snapshot()
    assert r["status"] == 201
    added(old, before, r["json"], "Pilot notebook")
    client.control(kind)
    exact(client.request(path="/healthz")["json"], {"status": "ok"})
    exact(client.request(path="/readyz")["json"], {"status": "ready"})
    unchanged(before, client.snapshot())


@pytest.mark.parametrize("fault", [None, "storage", "schema", "identity"])
def test_DATA05_probes(client, fault):
    client.reset()
    before = client.snapshot()
    client.control("configure", fault=fault)
    for _ in range(2):
        live = client.request(path="/healthz")
        assert live["status"] == 200
        exact(live["json"], {"status": "ok"})
        ready = client.request(path="/readyz")
        assert ready["status"] == (200 if fault is None else 503)
        exact(ready["json"], {"status": "ready" if fault is None else "not_ready"})
        headers(live)
        headers(ready)
    version(client.request(path="/api/version"), client.identity)
    client.control("configure", fault=None)
    unchanged(before, client.snapshot())


def test_API18_public_schema(client):
    client.reset()
    headers(client.request(path="/"), json_body=False)
    r = client.request(path="/openapi.json")
    assert r["status"] == 200, "Published OpenAPI unavailable"
    schema = r["json"]
    operation = schema["paths"]["/api/items"]["post"]
    assert {"201", "400", "422"} <= operation["responses"].keys()
    # Inspect complete public schema manually too; this checks required exact
    # record keys and explicit response schema links, not generator naming.
    def resolve(s):
        if "$ref" in s:
            value = schema
            for key in s["$ref"][2:].split("/"):
                value = value[key]
            return value
        return s
    record = resolve(operation["responses"]["201"]["content"]["application/json"]["schema"])
    assert set(record["properties"]) == {"id", "name", "created_at"}
    assert set(record["required"]) == {"id", "name", "created_at"}
    for code in ("400", "422"):
        err = resolve(operation["responses"][code]["content"]["application/json"]["schema"])
        assert set(err["properties"]) == {"error"}, "Default framework error substituted"
