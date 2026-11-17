import json
import pytest
from support.client import Unavailable
from support.oracles import added, error, exact, headers, method_error, unchanged, version
from support.parameters import SECURITY_CASES


@pytest.mark.parametrize("case", SECURITY_CASES, ids=lambda c: c.key)
def test_SEC_matrix(client, case):
    client.reset(**case.config)
    before = client.snapshot()
    events = client.control("observe")["events"]
    r = client.request(case.method, case.path, case.body, case.headers, case.default_host)
    proof = client.control("observe")["events"][len(events):]
    after = client.snapshot()
    if case.error:
        # Actual transport rejection cannot masquerade as application denial.
        if case.seam and not any(e["event"] == "dispatch" for e in proof):
            client.save("parser-boundary", {"wire": r, "proof": proof})
            raise Unavailable("HTTP parser refused dispatch; separate named received-request seam required")
        error(r, case.error)
        unchanged(before, after)
        if case.error in ("E-HOST", "E-ORIGIN"):
            assert not any(e["event"] in ("body-parse", "storage-probe", "storage-read", "committed") for e in proof), proof
    elif case.method == "POST":
        assert r["status"] == 201, r
        added(before, after, r["json"], case.name)
    else:
        assert r["status"] == 200
        exact(r["json"], {"status": "ok" if case.path == "/healthz" else "ready"})
        unchanged(before, after)


@pytest.mark.parametrize("environment", ["qa", "review"])
def test_SEC02_H10_H11_H12_verified_alias(client, environment):
    alias = client.identity.get("verified_qa_alias")
    if not alias:
        raise Unavailable("Conditional QA alias branch requires separately verified route and isolation")
    client.reset(environment=environment, port=18081 if environment == "qa" else 18080, alias=alias)
    a = f"{alias}:8000"
    before = client.snapshot()
    for origin in (None, f"http://{a}"):
        hs = [("Host", a), ("Content-Type", "application/json")]
        if origin is not None:
            hs += [("Origin", origin)]
        r = client.request("POST", body={"name": "Pilot notebook"}, headers=hs)
        after = client.snapshot()
        if environment == "qa":
            assert r["status"] == 201
            added(before, after, r["json"], "Pilot notebook")
        else:
            error(r, "E-HOST")
            unchanged(before, after)
        before = after
    if environment == "qa":
        for h in (f"{alias}:8001", f"other-{alias}:8000", f"{alias}.evil.invalid:8000"):
            error(client.request("POST", body={"name": "A"}, headers=[("Host", h)]), "E-HOST")
        for o in ("http://127.0.0.1:18081", f"http://{alias}:18081", f"https://{alias}:8000"):
            error(client.request("POST", body={"name": "A"}, headers=[("Host", a), ("Origin", o)]), "E-ORIGIN")
        r = client.request(path="/healthz", headers=[("Host", a)])
        assert r["status"] == 200
        exact(r["json"], {"status": "ok"})
        unchanged(before, client.snapshot())


@pytest.mark.parametrize("fault", ["storage", "internal-pre", "internal-post"])
def test_SEC03_P11_P12_fault_priority(client, fault):
    client.reset()
    before = client.snapshot()
    client.control("configure", fault=fault)
    for hs, body, ref in [
        ([("Host", "example.invalid:18081"), ("Origin", "http://example.invalid")], {"name": "A"}, "E-HOST"),
        ([("Host", "127.0.0.1:18081"), ("Origin", "http://example.invalid")], {"name": "A"}, "E-ORIGIN"),
        ([("Host", "127.0.0.1:18081"), ("Origin", "http://127.0.0.1:18081")], {"name": " "}, "E-LENGTH"),
    ]:
        old = client.control("observe")["events"]
        r = client.request("POST", body=body, headers=hs + [("Content-Type", "application/json")])
        proof = client.control("observe")["events"][len(old):]
        error(r, ref)
        assert not any(e["event"] in ("storage-read", "storage-probe", "committed") for e in proof)
    client.control("configure", fault=None)
    unchanged(before, client.snapshot())
    client.control("configure", fault=fault)
    r = client.request("POST", body={"name": "Pilot notebook"})
    client.control("configure", fault=None)
    after = client.snapshot()
    error(r, "E-STORAGE" if fault == "storage" else "E-INTERNAL")
    if fault == "internal-post":
        new = [x for x in after if x["id"] not in {a["id"] for a in before}]
        assert len(new) == 1
        added(before, after, new[0], "Pilot notebook")
    else:
        unchanged(before, after)


@pytest.mark.parametrize("fault", [None, "storage"])
def test_SEC03_P13_P14_P15_route_matrix(client, fault):
    client.reset()
    before = client.snapshot()
    paths = ["/", *client.identity["static_assets"], "/api/items", "/healthz", "/readyz", "/api/version", "/api/no-such-route"]
    routes = [("GET", p) for p in paths] + [("PUT", "/api/items"), ("OPTIONS", "/api/items")]
    for method, path in routes:
        for denial in ("E-HOST", "E-ORIGIN"):
            client.control("configure", fault=fault)
            hs = [("Host", "example.invalid:18081" if denial == "E-HOST" else "127.0.0.1:18081"), ("Origin", "http://example.invalid")]
            old = client.control("observe")["events"]
            r = client.request(method, path, headers=hs)
            proof = client.control("observe")["events"][len(old):]
            error(r, denial)
            assert not any(x["event"] in ("body-parse", "storage-probe", "storage-read", "committed") for x in proof)
        client.control("configure", fault=None)
        for origin in (None, "http://127.0.0.1:18081"):
            r = client.request(method, path, headers=[] if origin is None else [("Origin", origin)])
            headers(r, json_body=path not in ["/", *client.identity["static_assets"]])
            assert not any(k.startswith("access-control-allow-") for k in r["headers"])
            if method in ("PUT", "OPTIONS"):
                method_error(r)
            elif path == "/api/no-such-route":
                error(r, "E-NOTFOUND")
            elif path == "/api/items":
                exact(r["json"], {"items": before})
            elif path == "/api/version":
                version(r, client.identity)
            elif path in ("/healthz", "/readyz"):
                exact(r["json"], {"status": "ok" if path == "/healthz" else "ready"})
            else:
                assert r["status"] == 200
    for denial in ("E-HOST", "E-ORIGIN"):
        hs = [("Host", "example.invalid:18081" if denial == "E-HOST" else "127.0.0.1:18081"), ("Origin", "http://example.invalid")]
        error(client.request("HEAD", "/api/items", headers=hs), denial, head=True)
    unchanged(before, client.snapshot())
