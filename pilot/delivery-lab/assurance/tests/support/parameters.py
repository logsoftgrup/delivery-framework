"""Explicit TS-3 parameter expansion, independent of fixture implementation."""
import json
from dataclasses import dataclass, field
from .oracles import SPEC


@dataclass
class Case:
    key: str
    body: object = field(default_factory=lambda: {"name": "Pilot notebook"})
    error: str | None = None
    name: str | None = "Pilot notebook"
    headers: list | None = None
    method: str = "POST"
    path: str = "/api/items"
    config: dict = field(default_factory=dict)
    default_host: bool = True
    seam: bool = False


def pad(prefix, length):
    raw = prefix.encode() if isinstance(prefix, str) else prefix
    assert len(raw) <= length
    return raw + b" " * (length - len(raw))


def api_cases():
    out = [Case("API-01/trim", {"name": "  Pilot notebook  "}), Case("API-05/c0-sentinel", {"name": " \t\r\n "}, "E-LENGTH")]
    for f in SPEC["name_cases"]:
        tags = "API-02" if f["expected_status"] == 201 else "API-04"
        if f["error_ref"] == "E-LENGTH" and not f.get("expected_stored_name") and "trim" in f["key"]:
            tags = "API-05"
        out.append(Case(f"{tags}/{f['scenario']}/{f['key']}/api", {"name": f["request_name"]}, f["error_ref"], f.get("expected_stored_name")))
    out.append(Case("API-03/missing", {}, "E-REQUIRED"))
    for i, v in enumerate([None, False, True, 0, 1.5, [], {}]):
        out.append(Case(f"API-03/type-{i}", {"name": v}, "E-TYPE"))
    for i, v in enumerate([None, True, 1, "text", []]):
        out.append(Case(f"API-06/object-{i}", json.dumps(v).encode(), "E-OBJECT"))
    for i, v in enumerate([{"extra": 1}, {"name": "valid", "extra": 1}, {"name": None, "extra": 1}, {"name": " ", "extra": 1}]):
        out.append(Case(f"API-07/API-13/extra-{i}", v, "E-UNKNOWN"))
    for f in SPEC["raw_request_cases"]:
        raw = bytes.fromhex(f["wire_utf8_hex"])
        name = json.loads(raw)["name"] if f["expected_status"] == 201 else None
        out.append(Case(f"API-08/API-09/{f['key']}", raw, f["error_ref"], name))
    for media in [None, "text/plain", "application/x-www-form-urlencoded", "application/xml"]:
        out.append(Case(f"API-10/media-{media}", headers=[] if media is None else [("Content-Type", media)], error="E-MEDIA"))
    for media in ["application/json", "application/json;charset=utf-8"]:
        out.append(Case(f"API-10/media-{media}", headers=[("Content-Type", media)]))
    for f in SPEC["size_constructions"]:
        out.append(Case(f"API-11/API-12/{f['key']}", pad(f["prefix_utf8"], f["target_utf8_bytes"]), f.get("error_ref"), f.get("stored_name")))
    out += [Case("API-12/size-before-media", pad("{", 16385), "E-SIZE", headers=[]),
            Case("API-12/media-before-json", b"{", "E-MEDIA", headers=[]),
            Case("API-13/duplicate-before-extra", b'{"name":"A","name":"B","extra":1}', "E-JSON"),
            Case("API-09/API-13/surrogate-before-length", {"name": "\ud800" + "a" * 81}, "E-UNICODE")]
    return out


def security_cases():
    out = []
    for port in (18081, 18080):
        other = 18080 if port == 18081 else 18081
        for host in ("localhost", "127.0.0.1"):
            authority = f"{host}:{port}"
            origin = "http://" + authority
            prefix = f"{port}/{host}"
            config = {"port": port, "environment": "qa" if port == 18081 else "review"}

            def add(key, hosts=None, origins=None, error=None, body=None, media="application/json", method="POST", path="/api/items", extra=(), seam=False, conf=None):
                hs = [("Host", x) for x in (hosts if hosts is not None else [authority])]
                if origins is not None:
                    hs += [("Origin", x) for x in origins]
                if media is not None:
                    hs.append(("Content-Type", media))
                hs += list(extra)
                out.append(Case(f"{key}/{prefix}", {"name": "Pilot notebook"} if body is None else body, error, "Pilot notebook", hs, method, path, config | (conf or {}), False, seam))

            add("SEC-01/O01", origins=[origin])
            add("SEC-01/O02")
            other_host = "127.0.0.1" if host == "localhost" else "localhost"
            groups = {
                "O03": [f"http://{other_host}:{port}"],
                "O04": [f"http://{host}:{other}", f"http://{host}:8000", f"http://{host}", f"http://{host}:80"],
                "O05": [f"https://{host}:{port}", f"https://{host}", f"ftp://{host}:{port}"],
                "O06": ["", "null"],
                "O07": ["not-an-origin", "http://", origin + "/path", origin + "?x=1", f"http://user@{authority}"],
                "O08": [origin + ", http://example.invalid", origin + " http://example.invalid"],
                "O09": [f"http://{h}:{port}" for h in ["localhost.evil.invalid", "sub.localhost", "localhost.", "127.0.0.2", "[::1]"]],
            }
            for key, values in groups.items():
                for n, value in enumerate(values):
                    add(f"SEC-01/{key}/{n}", origins=[value], error="E-ORIGIN")
            for n, origins in enumerate([[origin, origin], [origin, "http://example.invalid"]]):
                add(f"SEC-01/O08/duplicate-{n}", origins=origins, error="E-ORIGIN")
            if host == "localhost":
                add("SEC-01/O10/host-case", hosts=[f"LoCaLhOsT:{port}"], origins=[origin])
                add("SEC-01/O10/origin-case", origins=[f"http://LOCALHOST:{port}"])
            admitted_forward = [("Forwarded", f"host={authority};proto=http"), ("X-Forwarded-Host", authority), ("X-Forwarded-Proto", "http")]
            bad_forward = [("Forwarded", "host=example.invalid;proto=https"), ("X-Forwarded-Host", "example.invalid"), ("X-Forwarded-Proto", "https")]
            add("SEC-01/O11", origins=["http://example.invalid"], error="E-ORIGIN", extra=admitted_forward)
            for n, origins in enumerate([[origin], None]):
                add(f"SEC-01/O12/{n}", origins=origins, extra=bad_forward)
                add(f"SEC-02/H01/{n}", origins=origins)
            for n, authority2 in enumerate([f"LoCaLhOsT:{port}", f"localhost:0{port}"]):
                add(f"SEC-02/H02/{n}", hosts=[authority2], origins=[f"http://localhost:{port}"])
            for n, hosts in enumerate([[], [""]]):
                add(f"SEC-02/H03/{n}", hosts=hosts, error="E-HOST", seam=True)
            hg = {
                "H04": [host, f"{host}:{other}", f"{host}:8000", f"{host}:80", f"{host}:0"],
                "H05": [f"{host}:abc", f"{host}:65536", authority + ":extra", "user@" + authority, "http://" + authority, host + ":"],
                "H06": [authority + ",example.invalid:" + str(port)],
                "H07": [f"{h}:{port}" for h in ["localhost.", "sub.localhost", "localhost.evil.invalid", "evil-localhost", "127.0.0.2", "[::1]", "example.invalid"]],
                "H09": ["unverified-pilot.invalid:8000"],
            }
            for key, values in hg.items():
                for n, value in enumerate(values):
                    add(f"SEC-02/{key}/{n}", hosts=[value], error="E-HOST", seam=key in ("H05", "H06"))
            for n, hosts in enumerate([[authority, authority], [authority, f"example.invalid:{port}"]]):
                add(f"SEC-02/H06/duplicate-{n}", hosts=hosts, error="E-HOST", seam=True)
            add("SEC-02/H08", hosts=[f"example.invalid:{port}"], origins=[origin], error="E-HOST", extra=admitted_forward)
            for n, path in enumerate(["/healthz", "/readyz"]):
                add(f"SEC-01/O02/probe-{n}", body=b"", method="GET", path=path)
            add("SEC-02/H13/allowed", body=b"", method="GET", path="/healthz")
            add("SEC-02/H13/denied", hosts=[f"example.invalid:{port}"], body=b"", method="GET", path="/healthz", error="E-HOST")
            bodies = [({"name": "Pilot notebook"}, "application/json"), (pad('{"name":"Pilot notebook"}', 16385), "application/json"), (pad("{", 16385), "application/json"), (b"{", "application/json"), ({"name": "Pilot notebook"}, "text/plain"), ({}, "application/json"), ({"name": " "}, "application/json"), (pad("{", 16385), "text/plain")]
            for n, (body, media) in enumerate(bodies):
                for sub, origins in [("P01", ["http://example.invalid"]), ("P02/matching", [origin]), ("P02/absent", None)]:
                    add(f"SEC-03/{sub}/{n}", hosts=[f"example.invalid:{port}"], origins=origins, error="E-HOST", body=body, media=media)
                add(f"SEC-03/P03/{n}", origins=["http://example.invalid"], error="E-ORIGIN", body=body, media=media)
            for n, origins in enumerate([[origin], None]):
                add(f"SEC-03/P04/{n}", origins=origins, body=pad("{", 16385), media="text/plain", error="E-SIZE")
            priority = [("P05/boundary", pad("{", 16384), "text/plain", "E-MEDIA"), ("P05/missing", b"{", None, "E-MEDIA"), ("P06/boundary", pad("{", 16384), "application/json", "E-JSON"), ("P06/duplicate", b'{"name":" ","name":null,"extra":1}', "application/json", "E-JSON"), ("P07", [], "application/json", "E-OBJECT"), ("P08/missing", {"extra": 1}, "application/json", "E-UNKNOWN"), ("P08/type", {"extra": 1, "name": None}, "application/json", "E-UNKNOWN"), ("P08/length", {"extra": 1, "name": " "}, "application/json", "E-UNKNOWN"), ("P09/missing", {}, "application/json", "E-REQUIRED"), ("P09/type", {"name": None}, "application/json", "E-TYPE"), ("P09/unicode", {"name": "\ud800" + "a" * 81}, "application/json", "E-UNICODE"), ("P09/length", {"name": " "}, "application/json", "E-LENGTH"), ("P10", pad('{"name":"Pilot notebook"}', 16384), "application/json", None)]
            for key, body, media, err in priority:
                add(f"SEC-03/{key}", origins=[origin], body=body, media=media, error=err)
    # A concrete synthetic alias is confined to the fixture. Real runtime tests
    # replace this only with an independently verified packet alias, never enable it.
    return out


API_CASES = api_cases()
SECURITY_CASES = security_cases()
