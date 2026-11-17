"""One FastAPI/Uvicorn worker, without proxy-header trust or access-body logging."""

import json
import logging
import os
import re
import sqlite3
import time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, JSONResponse
from starlette.concurrency import run_in_threadpool

from core import ContractError, MAX_BODY, Store, admit, parse_name
from schema import openapi


ROOT = Path(__file__).resolve().parent
logger = logging.getLogger("delivery_lab")
environment = os.environ.get("DELIVERY_LAB_ENV")
if environment not in {"qa", "review"}:
    raise RuntimeError("DELIVERY_LAB_ENV must be qa or review")
if os.environ.get("DELIVERY_LAB_DB_PATH", "/data/items.sqlite3") != "/data/items.sqlite3":
    raise RuntimeError("The database must use the declared data volume")
if os.environ.get("DELIVERY_LAB_PORT", "8000") != "8000":
    raise RuntimeError("The container service port must be 8000")

# Baked into the image after source publication. No runtime environment override.
identity = json.loads((ROOT / "build_identity.json").read_text())
if (set(identity) != {"source_commit", "build_id", "contract_version", "schema_version"}
        or not re.fullmatch(r"[0-9a-f]{40}", identity["source_commit"])
        or not isinstance(identity["build_id"], str) or not identity["build_id"]
        or identity["contract_version"] != "1" or type(identity["schema_version"]) is not int
        or identity["schema_version"] != 1):
    raise RuntimeError("A valid immutable build identity is required")

port = 18081 if environment == "qa" else 18080
allowed = {("localhost", port), ("127.0.0.1", port)}
# No internal QA alias is enabled. It needs independent route qualification.
store = Store("/data/items.sqlite3")


@asynccontextmanager
async def lifespan(_):
    try:
        await run_in_threadpool(store.initialize)
    except (sqlite3.Error, OSError, ValueError):
        logger.error("storage_initialization_failed")
    yield


api = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None,
              redirect_slashes=False)


@api.exception_handler(ContractError)
async def contract_error(_, error):
    return JSONResponse(error.body, status_code=error.status)


@api.exception_handler(HTTPException)
async def routing_error(request, error):
    code = {404: "not_found", 405: "method_not_allowed"}.get(error.status_code, "internal_error")
    public = ContractError(code)
    headers = error.headers
    if error.status_code == 405:
        headers = {"Allow": "GET, POST" if request.url.path == "/api/items" else "GET"}
    return JSONResponse(public.body, status_code=public.status, headers=headers)


@api.exception_handler(Exception)
async def unexpected_error(_, error):
    public = ContractError("internal_error")
    return JSONResponse(public.body, status_code=500)


@api.get("/api/items")
def items():
    return {"items": store.list()}


@api.post("/api/items")
async def create(request: Request):
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > MAX_BODY:
            raise ContractError("request_too_large")
    media_types = [v.decode("latin-1") for k, v in request.scope["headers"] if k.lower() == b"content-type"]
    name = parse_name(bytes(raw), media_types)
    value = await run_in_threadpool(store.create, name)
    return JSONResponse(value, status_code=201)


@api.get("/healthz")
def health():
    return {"status": "ok"}


@api.get("/readyz")
def ready():
    try:
        is_ready = store.ready()
    except sqlite3.Error:
        is_ready = False
    return JSONResponse({"status": "ready" if is_ready else "not_ready"},
                        status_code=200 if is_ready else 503)


@api.get("/api/version")
def version():
    return identity


@api.get("/openapi.json")
def schema():
    return openapi()


@api.get("/")
def index():
    return FileResponse(ROOT / "static/index.html", media_type="text/html")


@api.get("/assets/app.js")
def javascript():
    return FileResponse(ROOT / "static/app.js", media_type="text/javascript")


@api.get("/assets/style.css")
def stylesheet():
    return FileResponse(ROOT / "static/style.css", media_type="text/css")


class Admission:
    """Outer ASGI layer: admission precedes routing, body parsing and storage."""
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.inner(scope, receive, send)
        started, status = False, 500
        request_id, start = str(uuid4()), time.monotonic()

        async def respond(message):
            nonlocal started, status
            if message["type"] == "http.response.start":
                started, status = True, message["status"]
                headers = [(k, v) for k, v in message.get("headers", [])
                           if k.lower() != b"cache-control" and not k.lower().startswith(b"access-control-allow-")]
                headers.extend([
                    (b"cache-control", b"no-store"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"content-security-policy", b"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"),
                ])
                message = {**message, "headers": headers}
            # HEAD responses suppress the body while retaining selected status.
            if scope["method"] == "HEAD" and message["type"] == "http.response.body":
                message = {**message, "body": b""}
            await send(message)

        try:
            admit(scope["headers"], allowed)
            await self.inner(scope, receive, respond)
        except ContractError as error:
            if not started:
                await JSONResponse(error.body, status_code=error.status)(scope, receive, respond)
        except Exception:
            if not started:
                error = ContractError("internal_error")
                await JSONResponse(error.body, status_code=500)(scope, receive, respond)
            logger.error("request_failed request_id=%s", request_id)
        finally:
            known_routes = {"/", "/api/items", "/api/version", "/healthz", "/readyz",
                            "/openapi.json", "/assets/app.js", "/assets/style.css"}
            route = scope["path"] if scope["path"] in known_routes else "<unmatched>"
            method = scope["method"] if scope["method"] in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"} else "OTHER"
            logger.info(json.dumps({"request_id": request_id, "method": method, "route": route,
                                    "status": status, "duration_ms": round((time.monotonic() - start) * 1000),
                                    "source_commit": identity["source_commit"]}))


app = Admission(api)
