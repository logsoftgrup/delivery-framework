"""Raw HTTP with duplicate/missing headers preserved, durable request receipts."""
import hashlib
import http.client
import json
import time
from pathlib import Path
from urllib.parse import urlsplit


class Unavailable(RuntimeError):
    pass


class Client:
    def __init__(self, base_url, authority, evidence, controller, identity):
        self.base_url = base_url.rstrip("/")
        self.authority = authority
        self.evidence = Path(evidence)
        self.evidence.mkdir(parents=True, exist_ok=True)
        self.controller = controller
        self.identity = identity
        self.n = 0

    def save(self, kind, obj):
        self.n += 1
        path = self.evidence / f"{self.n:05}-{kind}.json"
        path.write_text(json.dumps(obj, ensure_ascii=True, indent=2) + "\n")
        return path

    def request(self, method="GET", path="/api/items", body=None, headers=None, default_host=True):
        raw = body if isinstance(body, bytes) else b"" if body is None else json.dumps(body, ensure_ascii=True, separators=(",", ":")).encode()
        hs = list(headers) if headers is not None else ([("Content-Type", "application/json")] if method == "POST" else [])
        if default_host and not any(k.lower() == "host" for k, _ in hs):
            hs.insert(0, ("Host", self.authority))
        if not any(k.lower() == "content-length" for k, _ in hs):
            hs.append(("Content-Length", str(len(raw))))
        req = {"method": method, "path": path, "headers": hs, "body_hex": raw.hex(), "body_sha256": hashlib.sha256(raw).hexdigest(), "route": self.base_url, "started_ns": time.time_ns()}
        self.save("request-prepared", req)
        target = urlsplit(self.base_url)
        if target.scheme != "http":
            raise Unavailable("Only the admitted HTTP QA route is supported")
        conn = http.client.HTTPConnection(target.hostname, target.port, timeout=20)
        self.save("request-dispatch-started", {"request": self.n})
        try:
            conn.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
            for k, v in hs:
                conn.putheader(k, v)
            conn.endheaders(raw)
            response = conn.getresponse()
            data = response.read()
            try:
                parsed = json.loads(data)
            except (ValueError, UnicodeError):
                parsed = None
            result = {"status": response.status, "headers": {k.lower(): v for k, v in response.getheaders()}, "raw_headers": response.getheaders(), "raw_hex": data.hex(), "json": parsed, "ended_ns": time.time_ns()}
            self.save("response-confirmed", result)
            return result
        except (OSError, http.client.HTTPException) as exc:
            self.save("transport-unknown", {"type": type(exc).__name__, "message": str(exc)})
            raise Unavailable("Transport outcome UNKNOWN; inspect saved request/response evidence") from exc
        finally:
            conn.close()

    def snapshot(self):
        from .oracles import exact, headers, ordered
        r = self.request()
        assert r["status"] == 200, r
        headers(r)
        assert type(r["json"]) is dict and set(r["json"]) == {"items"}
        rows = r["json"]["items"]
        ordered(rows)
        self.save("snapshot", rows)
        return rows

    def control(self, operation, **kwargs):
        self.save("control-prepared", {"operation": operation, "arguments": kwargs})
        result = self.controller.perform(operation, **kwargs)
        self.save("control-response", result)
        return result

    def reset(self, state="F-SEED", **config):
        self.authority = f"127.0.0.1:{config.get('port', 18081)}"
        return self.control("reset", state=state, config=config)
