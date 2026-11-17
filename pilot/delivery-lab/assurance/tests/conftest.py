import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import pytest
from support.client import Client, Unavailable
from support.safety import OperatorController, validate_packet


def pytest_addoption(parser):
    parser.addoption("--evidence", required=True)
    parser.addoption("--kind", choices=("fixture", "qa"), required=True)
    parser.addoption("--packet")
    parser.addoption("--mutation", default="good")


def pytest_configure(config):
    config._tc_results = []
    config._tc_ids = []


def pytest_collection_modifyitems(config, items):
    config._tc_ids = [i.nodeid for i in items]
    assert items, "No tests collected"
    for i in items:
        assert not any(i.get_closest_marker(k) for k in ("skip", "skipif", "xfail")), "Required checks cannot skip/xfail"
    Path(config.getoption("--evidence"), "collected.json").write_text(json.dumps(config._tc_ids, indent=2))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    result = {"id": item.nodeid, "phase": report.when, "outcome": report.outcome, "duration": report.duration}
    if report.failed:
        result["classification"] = "UNAVAILABLE" if call.excinfo and isinstance(call.excinfo.value, Unavailable) else "FAIL" if report.when == "call" and call.excinfo and isinstance(call.excinfo.value, AssertionError) else "UNKNOWN"
        result["detail"] = str(report.longrepr)
    item.config._tc_results.append(result)


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    run = json.loads(Path(config.getoption("--evidence"), "run.json").read_text())
    result = {"attempt_id": run["attempt_id"], "pytest_exit": int(exitstatus), "collected": len(config._tc_ids), "results": config._tc_results, "manual_verdict": "PENDING", "source_acceptance": "NOT DECIDED"}
    Path(config.getoption("--evidence"), "results.json").write_text(json.dumps(result, indent=2))


@pytest.fixture(scope="session")
def controller(request):
    if request.config.getoption("--kind") == "fixture":
        from fixture.server import Controller
        c = Controller(request.config.getoption("--mutation"))
        c.identity |= {"static_assets": ["/fixture.js"], "verified_qa_alias": "synthetic-fixture", "classification": "synthetic-contract-double"}
        yield c
        c.close()
    else:
        p = request.config.getoption("--packet")
        if not p:
            raise Unavailable("QA packet missing; no request issued")
        run = json.loads(Path(request.config.getoption("--evidence"), "run.json").read_text())
        packet = validate_packet(json.loads(Path(p).read_text()), run["suite_sha"])
        c = OperatorController(packet, request.config.getoption("--evidence"))
        c.url, c.identity = packet["base_url"], packet
        yield c


@pytest.fixture
def client(request, controller):
    key = hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:20]
    folder = Path(request.config.getoption("--evidence")) / key
    c = Client(controller.url, "127.0.0.1:18081", folder, controller, controller.identity)
    c.save("identity", {"test": request.node.nodeid, "fixture_mutation": request.config.getoption("--mutation"), "candidate": controller.identity})
    if request.config.getoption("--kind") == "qa":
        from support.oracles import version
        version(c.request(path="/api/version"), controller.identity)
    return c


@pytest.fixture(scope="session")
def browser(request):
    from playwright.sync_api import sync_playwright
    assert importlib.metadata.version("playwright") == "1.56.0"
    with sync_playwright() as p:
        executable = Path(p.chromium.executable_path)
        if not executable.is_file():
            raise Unavailable("Pinned Playwright Chromium not installed; no system-browser fallback")
        h = hashlib.sha256(executable.read_bytes()).hexdigest()
        b = p.chromium.launch(headless=True)
        Path(request.config.getoption("--evidence"), "browser.json").write_text(json.dumps({"version": b.version, "executable_sha256": h, "playwright": "1.56.0", "headless": True}))
        yield b
        b.close()


@pytest.fixture
def page(browser, client):
    context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, service_workers="block")
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    p = context.new_page()
    p.on("console", lambda msg: client.save("console", {"type": msg.type, "text": msg.text}))
    p.on("pageerror", lambda exc: client.save("pageerror", {"text": str(exc)}))
    p.on("request", lambda r: client.save("browser-request", {"method": r.method, "url": r.url, "post_data": r.post_data}))
    p.on("response", lambda r: client.save("browser-response", {"url": r.url, "status": r.status, "headers": r.headers}))
    yield p
    try:
        p.screenshot(path=str(client.evidence / "final.png"), full_page=True)
        (client.evidence / "final.html").write_text(p.content())
    finally:
        context.tracing.stop(path=str(client.evidence / "trace.zip"))
        context.close()
