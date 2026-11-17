"""Delivery Lab contract and SQLite operations; synthetic data only."""

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


TRIM = "\u0009\u000a\u000b\u000c\u000d\u0020\u0085\u00a0\u1680" + "".join(
    chr(n) for n in range(0x2000, 0x200B)
) + "\u2028\u2029\u202f\u205f\u3000"
MAX_BODY = 16_384
SEEDS = ("Sample notebook", "Sample cable", "Sample adapter")
ERRORS = {
    "host_not_allowed": (403, "Host is not allowed."),
    "origin_not_allowed": (403, "Origin is not allowed."),
    "request_too_large": (413, "Request body is too large."),
    "unsupported_media_type": (415, "Use application/json."),
    "invalid_json": (400, "Send a valid JSON object."),
    "validation_error": (422, "Check the request fields."),
    "storage_unavailable": (503, "Items are temporarily unavailable. Try again."),
    "internal_error": (500, "Something went wrong. Check the list before trying again."),
    "not_found": (404, "This route does not exist."),
    "method_not_allowed": (405, "This method is not supported."),
}
FIELD_ERRORS = {
    "object_required": ("$", "Send an object with a name field."),
    "unknown_fields": ("$", "Only the name field is allowed."),
    "name_required": ("name", "Enter a name."),
    "name_type": ("name", "Name must be text."),
    "name_unicode": ("name", "Use valid Unicode text."),
    "name_length": ("name", "Enter 1–80 characters after trimming surrounding whitespace."),
}


class ContractError(Exception):
    def __init__(self, code, field_code=None):
        self.code = code
        self.status, message = ERRORS[code]
        fields = []
        if field_code:
            field, field_message = FIELD_ERRORS[field_code]
            fields = [{"field": field, "code": field_code, "message": field_message}]
        self.body = {"error": {"code": code, "message": message, "fields": fields}}
        super().__init__(code)


def authority(value):
    """Only explicit ASCII host:port; no aliases, userinfo or forwarded headers."""
    match = re.fullmatch(r"([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*):([0-9]{1,5})", value)
    if not match:
        return None
    host, port = match.groups()
    port = int(port)
    return (host.lower(), port) if 1 <= port <= 65535 else None


def admit(headers, allowed):
    hosts = [value.decode("latin-1") for name, value in headers if name.lower() == b"host"]
    host = authority(hosts[0]) if len(hosts) == 1 else None
    if host not in allowed:
        raise ContractError("host_not_allowed")
    origins = [value.decode("latin-1") for name, value in headers if name.lower() == b"origin"]
    if not origins:
        return
    if len(origins) != 1:
        raise ContractError("origin_not_allowed")
    # A serialized HTTP origin has no path (including trailing slash), query or fragment.
    match = re.fullmatch(r"(https?)://([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*)(?::([0-9]{1,5}))?", origins[0], re.ASCII | re.IGNORECASE)
    if not match:
        raise ContractError("origin_not_allowed")
    scheme, hostname, port = match.groups()
    scheme = scheme.lower()
    port = int(port) if port is not None else (80 if scheme == "http" else 443)
    if scheme != "http" or (hostname.lower(), port) != host:
        raise ContractError("origin_not_allowed")


def parse_name(raw, media_types):
    if len(raw) > MAX_BODY:
        raise ContractError("request_too_large")
    if len(media_types) != 1 or not re.fullmatch(
        r'application/json(?:\s*;\s*charset\s*=\s*(?:utf-8|"utf-8"))?\s*',
        media_types[0], re.IGNORECASE | re.ASCII,
    ):
        raise ContractError("unsupported_media_type")

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    def invalid_constant(_):
        raise ValueError("non-JSON number")

    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                         parse_constant=invalid_constant)
    except (UnicodeError, ValueError, RecursionError):
        raise ContractError("invalid_json") from None
    if not isinstance(obj, dict):
        raise ContractError("validation_error", "object_required")
    if set(obj) - {"name"}:
        raise ContractError("validation_error", "unknown_fields")
    if "name" not in obj:
        raise ContractError("validation_error", "name_required")
    raw_name = obj["name"]
    if not isinstance(raw_name, str):
        raise ContractError("validation_error", "name_type")
    if any(0xD800 <= ord(c) <= 0xDFFF for c in raw_name):
        raise ContractError("validation_error", "name_unicode")
    name = raw_name.strip(TRIM)
    # C0-API-05: sole authorized deliberate defect. A nonempty all-trim input
    # reaches storage as an empty name. The UI and accepted oracle stay strict.
    # After native original-producer return, C1 removes this exception.
    whitespace_only_c0 = bool(raw_name) and not name
    if not 1 <= len(name) <= 80 and not whitespace_only_c0:
        raise ContractError("validation_error", "name_length")
    return name


def item(name):
    return {"id": str(uuid4()), "name": name,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}


class Store:
    def __init__(self, path):
        self.path = str(path)
        self.initialized = False

    def connect(self, create=False):
        target = Path(self.path).resolve().as_uri() + ("?mode=rwc" if create else "?mode=rw")
        db = sqlite3.connect(target, timeout=5, isolation_level=None, uri=True)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=5000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def initialize(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        db = self.connect(create=True)
        try:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("BEGIN IMMEDIATE")
            db.execute("CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            version = db.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
            if version and version[0] != "1":
                raise ValueError("unsupported schema")
            seeded = db.execute("SELECT value FROM metadata WHERE key='initialized'").fetchone()
            if not seeded and not db.execute("SELECT 1 FROM items LIMIT 1").fetchone():
                for name in SEEDS:
                    db.execute("INSERT INTO items (id,name,created_at) VALUES (:id,:name,:created_at)", item(name))
            db.execute("INSERT OR IGNORE INTO metadata VALUES ('initialized','1')")
            db.execute("INSERT OR IGNORE INTO metadata VALUES ('schema_version','1')")
            db.commit()
            self.initialized = True
        finally:
            if db.in_transaction:
                db.rollback()
            db.close()

    def ready(self):
        if not self.initialized:
            return False
        db = None
        try:
            db = self.connect()
            db.execute("BEGIN IMMEDIATE")
            columns = db.execute("PRAGMA table_info(items)").fetchall()
            expected = [("id", "TEXT", 0, 1), ("name", "TEXT", 1, 0), ("created_at", "TEXT", 1, 0)]
            if [(r["name"], r["type"], r["notnull"], r["pk"]) for r in columns] != expected:
                return False
            metadata = dict(db.execute("SELECT key,value FROM metadata").fetchall())
            if metadata.get("schema_version") != "1" or metadata.get("initialized") != "1":
                return False
            db.execute("SELECT id,name,created_at FROM items LIMIT 1").fetchall()
            db.execute("INSERT INTO items (id,name,created_at) VALUES (:id,:name,:created_at)", item("Readiness sample"))
            db.rollback()
            return True
        except (sqlite3.Error, OSError):
            return False
        finally:
            if db:
                if db.in_transaction:
                    db.rollback()
                db.close()

    def list(self):
        if not self.initialized:
            raise ContractError("storage_unavailable")
        db = None
        try:
            db = self.connect()
            rows = db.execute("SELECT id,name,created_at FROM items ORDER BY created_at ASC, id COLLATE BINARY ASC").fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error:
            raise ContractError("storage_unavailable") from None
        finally:
            if db:
                db.close()

    def create(self, name):
        if not self.initialized:
            raise ContractError("storage_unavailable")
        db = None
        began = False
        try:
            db = self.connect()
            db.execute("BEGIN IMMEDIATE")
            began = True
            value = item(name)
            db.execute("INSERT INTO items (id,name,created_at) VALUES (:id,:name,:created_at)", value)
            db.commit()
            return value
        except sqlite3.Error:
            # 503 is only a definite no-write result. A commit exception with
            # no active transaction is ambiguous and must remain a 500.
            certain = not began
            if db is not None and db.in_transaction:
                try:
                    db.rollback()
                    certain = not db.in_transaction
                except sqlite3.Error:
                    certain = False
            raise ContractError("storage_unavailable" if certain else "internal_error") from None
        finally:
            if db:
                db.close()
