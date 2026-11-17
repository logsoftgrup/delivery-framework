"""Suite-owned synthetic contract double, NOT Delivery Lab application code.

No deployment, Docker socket, production endpoint, or external data. Control is an
in-process Python interface; the HTTP surface has no reset/fault endpoint.
"""
import copy
import datetime as dt
import json
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE.parent / "spec/fixtures.json").read_text())
TRIM = "".join(chr(int(x.replace("U+", ""), 16)) for x in DATA["trim_codepoints"])


class DuplicateKey(ValueError):
    pass


def pairs(values):
    result = {}
    for k, v in values:
        if k in result:
            raise DuplicateKey(k)
        result[k] = v
    return result


class Controller:
    def __init__(self, mutation="good"):
        self.mutation = mutation
        self.lock = threading.RLock()
        self.identity = {"app_sha": "f" * 40, "build_id": "synthetic-contract-fixture-TC1"}
        self.rows = []
        self.config = {}
        self.events = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.fixture = self
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.perform("reset", state="F-SEED", config={})

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def add(self, name):
        result = {"id": str(uuid.uuid4()), "name": name, "created_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
        self.rows.append(result)
        return copy.deepcopy(result)

    def perform(self, operation, **args):
        with self.lock:
            if operation == "reset":
                state = copy.deepcopy(DATA["states"][args["state"]])
                self.rows = state.get("installation_order", state.get("items", []))
                self.initialized = state.get("initialized", False)
                self.config = {"port": 18081, "environment": "qa", "alias": None, "fault": None} | args.get("config", {})
                self.events = []
                if not self.initialized and not self.rows:
                    for name in ("Sample notebook", "Sample cable", "Sample adapter"):
                        self.add(name)
                    self.initialized = True
            elif operation == "configure":
                self.config.update(args)
            elif operation in ("process_restart", "container_restart"):
                # Logical durability double only; actual process/container evidence is O/M.
                if self.mutation == "lost-row" and self.rows:
                    self.rows.pop()
                if self.mutation == "reseed-empty" and not self.rows:
                    self.add("Sample notebook")
                self.events.append({"event": operation, "kind": "synthetic-logical-restart"})
            elif operation == "observe":
                pass
            elif operation == "dispatch":
                # Named received-request seam for headers refused by real HTTP parsers.
                result = self.respond(args["method"], args["path"], args["headers"], bytes.fromhex(args.get("body_hex", "")))
                return {"status": result[0], "headers": result[1], "raw_hex": result[2].hex(), "json": json.loads(result[2]) if result[2] else None, "seam": "synthetic-received-request"}
            else:
                raise ValueError(operation)
            return {"kind": "synthetic-contract-fixture", "operation": operation, "config": copy.deepcopy(self.config), "rows": copy.deepcopy(sorted(self.rows, key=lambda r: (r["created_at"], r["id"]))), "initialized": self.initialized, "events": copy.deepcopy(self.events)}

    def respond(self, method, path, raw_headers, body):
        with self.lock:
            hs = {}
            for k, v in raw_headers:
                hs.setdefault(k.lower(), []).append(v)
            self.events.append({"event": "dispatch", "method": method, "path": path})
            headers = {"content-type": "application/json", "cache-control": "no-store"}

            def reply(status, value):
                return status, headers, b"" if method == "HEAD" else json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode()

            def err(key):
                if key in ("E-HOST", "E-ORIGIN"):
                    code = "host" if key == "E-HOST" else "origin"
                    return reply(403, {"error": {"code": code + "_not_allowed", "message": code.capitalize() + " is not allowed.", "fields": []}})
                data = copy.deepcopy(DATA["error_oracles"][key])
                if self.mutation == "wrong-error":
                    data["body"]["error"]["message"] += " wrong"
                return reply(data["status"], data["body"])

            def authority(value):
                if not isinstance(value, str) or any(x in value for x in ("/", "@", ",", " ")) or value.count(":") != 1:
                    return None
                host, port = value.split(":")
                if not port.isascii() or not port.isdecimal() or not 0 < int(port) <= 65535:
                    return None
                return host.lower(), int(port)

            allowed = {("localhost", self.config["port"]), ("127.0.0.1", self.config["port"])}
            # Extra authority is ONLY the suite's ephemeral loopback browser fixture.
            allowed.add(("127.0.0.1", self.server.server_port))
            if self.config["environment"] == "qa" and self.config.get("alias"):
                allowed.add((self.config["alias"], 8000))
            host = authority(hs["host"][0]) if len(hs.get("host", [])) == 1 else None
            if host not in allowed:
                return err("E-HOST")
            if "origin" in hs:
                try:
                    o = hs["origin"][0]
                    parsed = urlsplit(o)
                    valid = len(hs["origin"]) == 1 and parsed.scheme == "http" and not parsed.path and not parsed.query and not parsed.fragment and not parsed.username and authority(parsed.netloc) == host
                except ValueError:
                    valid = False
                if not valid:
                    return err("E-ORIGIN")
            if path == "/" and method == "GET":
                headers["content-type"] = "text/html; charset=utf-8"
                html = (HERE / "page.html").read_text().replace("__MUTATION__", json.dumps(self.mutation))
                return 200, headers, html.encode()
            if path == "/fixture.js" and method == "GET":
                headers["content-type"] = "text/javascript"
                return 200, headers, (HERE / "page.js").read_bytes()
            if path == "/healthz" and method == "GET":
                return reply(200, {"status": "ok"})
            if path == "/readyz" and method == "GET":
                self.events.append({"event": "storage-probe"})
                bad = self.config["fault"] in ("storage", "schema", "identity")
                return reply(503 if bad else 200, {"status": "not_ready" if bad else "ready"})
            if path == "/api/version" and method == "GET":
                return reply(200, {"source_commit": self.identity["app_sha"], "build_id": self.identity["build_id"], "contract_version": "1", "schema_version": 1})
            if path == "/openapi.json" and method == "GET":
                return reply(200, json.loads((HERE / "openapi.json").read_text()))
            if path != "/api/items":
                return err("E-NOTFOUND")
            if method not in ("GET", "POST"):
                headers["allow"] = "GET, POST"
                return err("E-METHOD")
            if method == "GET":
                self.events.append({"event": "storage-read"})
                if self.config["fault"] == "storage":
                    return err("E-STORAGE")
                rows = sorted(copy.deepcopy(self.rows), key=lambda r: (r["created_at"], r["id"]))
                if self.mutation == "wrong-order":
                    rows.reverse()
                if self.mutation == "get-writes":
                    self.add("Unwanted probe")
                return reply(200, {"items": rows})
            if len(body) > 16384:
                return err("E-SIZE")
            if hs.get("content-type", [""])[0].split(";")[0].lower() != "application/json":
                return err("E-MEDIA")
            self.events.append({"event": "body-parse"})
            try:
                data = json.loads(body.decode("utf-8"), object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
            except (ValueError, UnicodeError):
                return err("E-JSON")
            if type(data) is not dict:
                return err("E-OBJECT")
            if set(data) - {"name"}:
                return err("E-UNKNOWN")
            if "name" not in data:
                return err("E-REQUIRED")
            if type(data["name"]) is not str:
                return err("E-TYPE")
            name = data["name"]
            if any(0xD800 <= ord(c) <= 0xDFFF for c in name):
                return err("E-UNICODE")
            name = name.strip(TRIM)
            if self.mutation == "broad-trim":
                name = name.strip("\u200b\ufeff\x1c")
            length = len(name.encode("utf-16-le")) // 2 if self.mutation == "utf16-count" else len(name)
            if not 1 <= length <= 80:
                if self.mutation == "c0-accept" and not name:
                    return reply(201, self.add(name))
                if self.mutation == "reject-writes":
                    self.add("Rejected write")
                return err("E-LENGTH")
            if self.config["fault"] == "storage":
                self.events.append({"event": "no-transaction-started"})
                return err("E-STORAGE")
            if self.config["fault"] == "internal-pre":
                self.events.append({"event": "internal-before-commit"})
                return err("E-INTERNAL")
            result = self.add(name)
            self.events.append({"event": "committed", "id": result["id"]})
            if self.config["fault"] == "internal-post":
                return err("E-INTERNAL")
            if self.mutation == "replace-old" and len(self.rows) > 1:
                self.rows[0]["name"] = "Changed old tuple"
            if self.mutation == "extra-key":
                result["extra"] = True
            if self.mutation == "invalid-time":
                result["created_at"] = "2026-02-30T12:00:00.000000Z"
            return reply(200 if self.mutation == "wrong-status" else 201, result)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_):
        pass

    def handle_request(self):
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length)
        status, headers, data = self.server.fixture.respond(self.command, self.path, list(self.headers.raw_items()), body)
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST = do_PUT = do_OPTIONS = do_HEAD = handle_request
