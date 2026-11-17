import json
from pathlib import Path
import pytest
from playwright.sync_api import expect
from support.oracles import SPEC, ERRORS, added, exact, unchanged

AUDIT = (Path(__file__).resolve().parents[1] / "support/dom_audit.js").read_text()
UNCERTAIN = "We could not confirm whether the item was created. Refreshing the list before you retry."
RECONCILED = "Check the list. A matching name may already exist. Create another item only if you intend to add one."
RECONCILE_FAIL = "We still cannot check the list. Refresh the list before creating another item."
INITIAL_FAIL = "Items could not be loaded. Refresh the list to try again."
CREATED_REFRESH_FAIL = "Item was created, but the list could not be refreshed. Refresh the list to see it."


def field(page):
    return page.get_by_role("textbox", name="Item name", exact=True)


def button(page):
    return page.get_by_role("button", name="Create", exact=True)


def names(page):
    return page.get_by_role("listitem").all_text_contents()


def capture(page, client, state):
    page.screenshot(path=str(client.evidence / (state + "-viewport.png")))
    page.screenshot(path=str(client.evidence / (state + "-full.png")), full_page=True)
    audit = page.evaluate(AUDIT)
    client.save("audit-" + state, audit)
    client.save("accessibility-tree-" + state, {"snapshot": page.locator("body").aria_snapshot()})
    assert audit["issues"] == [], audit


def opened(page, client, state="F-SEED"):
    client.reset(state)
    before = client.snapshot()
    page.goto(client.base_url, wait_until="domcontentloaded")
    expect(button(page)).to_be_enabled()
    expect(page.locator("form")).to_have_count(1)
    audit = page.evaluate(AUDIT)
    client.save("audit-opened", audit)
    assert audit["issues"] == [], audit
    expect(page.get_by_text("Synthetic data only. Create sample items to try the delivery journey.", exact=True)).to_be_visible()
    exact(names(page), [r["name"] for r in before])
    return before


def enter(page, f, client):
    control = field(page)
    b = f["browser_input"]
    assert control.get_attribute("type") == "text"
    if b["method"] == "standard_native_value_setter_then_input_event":
        checkpoint = control.evaluate("""(el, text) => {
          Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,text);
          const beforeEvent=el.value; el.dispatchEvent(new Event('input',{bubbles:true}));
          return {beforeEvent,afterEvent:el.value};
        }""", f["request_name"])
        exact(checkpoint["beforeEvent"], b["expected_control_value"])
        exact(checkpoint["afterEvent"], b["expected_control_value"])
    else:
        control.click()
        control.press("ControlOrMeta+A")
        control.press("Backspace")
        # Browser text/IME insertion, no DOM setter. Record it, do not claim an
        # actual human clipboard or physical keyboard session.
        page.keyboard.insert_text(f["request_name"])
        checkpoint = {"method": "Playwright keyboard.insert_text (text/IME)", "observed": control.input_value()}
    exact(control.input_value(), b["expected_control_value"])
    assert len(control.input_value()) == b["expected_control_scalar_count"]
    client.save("entry-checkpoint", {"fixture": f["key"], "method": b["method"], "classification": b["method_evidence_class"], "checkpoint": checkpoint, "codepoints": [f"U+{ord(c):04X}" for c in control.input_value()]})


@pytest.mark.parametrize("f", SPEC["name_cases"], ids=lambda f: f["browser_input"]["case_id"])
def test_UI02_UI03_entry(page, client, f):
    before = opened(page, client)
    posted, replies = [], []
    page.on("request", lambda r: posted.append(r.post_data_json) if r.method == "POST" and r.url.endswith("/api/items") else None)
    page.on("response", lambda r: replies.append(r.status) if r.request.method == "POST" and r.url.endswith("/api/items") else None)
    enter(page, f, client)
    b = f["browser_input"]
    button(page).click()
    if b["expected_http_if_sent"] == 201:
        expect(page.get_by_text("Item created.", exact=True)).to_be_visible()
        after = client.snapshot()
        assert len(posted) == 1 and replies == [201]
        assert posted[0]["name"] in b["allowed_request_name_values"]
        new = [r for r in after if r["id"] not in {s["id"] for s in before}]
        assert len(new) == 1
        added(before, after, new[0], b["expected_stored_name"])
        expect(field(page)).to_have_value("")
    else:
        expect(field(page)).to_have_attribute("aria-invalid", "true")
        expect(field(page)).to_be_focused()
        expect(field(page)).to_have_value(b["expected_control_value"])
        assert len(posted) <= 1
        if posted:
            assert posted[0]["name"] in b["allowed_request_name_values"]
            assert replies == [b["expected_http_if_sent"]]
        else:
            assert b["local_rejection_allowed"]
        unchanged(before, client.snapshot())
        capture(page, client, "validation")
        field(page).fill("Pilot notebook")
        button(page).click()
        expect(page.get_by_text("Item created.", exact=True)).to_be_visible()
        after = client.snapshot()
        new = [r for r in after if r["id"] not in {s["id"] for s in before}]
        assert len(new) == 1
        added(before, after, new[0], "Pilot notebook")


@pytest.mark.parametrize("viewport", [(390, 844), (1440, 900)])
def test_UI01_UI04_VIS01_pending_journey(page, client, viewport):
    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    client.reset()
    before = client.snapshot()
    held, posts = [], []

    def intercept(route):
        held.append(route)
        if route.request.method == "POST":
            posts.append(route.request.post_data_json)

    page.route("**/api/items", intercept)
    page.goto(client.base_url, wait_until="domcontentloaded")
    expect(page.get_by_text("Loading items…", exact=True)).to_be_visible()
    expect(button(page)).to_be_disabled()
    expect(page.get_by_text("No items yet. Create the first item.", exact=True)).not_to_be_visible()
    field(page).fill("Pilot notebook")
    capture(page, client, "loading")
    assert len(held) == 1
    held.pop().continue_()
    expect(button(page)).to_be_enabled()
    capture(page, client, "ready")
    button(page).click()
    expect(page.get_by_role("button", name="Creating…", exact=True)).to_be_disabled()
    expect(page.get_by_text("Creating item…", exact=True)).to_be_visible()
    assert field(page).is_disabled() or field(page).get_attribute("readonly") is not None
    expect(page.get_by_text("Item created.", exact=True)).not_to_be_visible()
    page.keyboard.press("Enter")
    page.keyboard.press("Enter")
    page.keyboard.press("X")
    box = page.get_by_role("button", name="Creating…", exact=True).bounding_box()
    page.mouse.dblclick(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    expect(field(page)).to_have_value("Pilot notebook")
    page.keyboard.press("Tab")
    assert len(posts) == 1
    capture(page, client, "pending")
    held.pop().continue_()
    expect(page.get_by_text("Item created. Updating the list…", exact=True)).to_be_visible()
    expect(field(page)).to_have_value("")
    assert len(held) == 1
    held.pop().continue_()
    expect(page.get_by_text("Item created.", exact=True)).to_be_visible()
    capture(page, client, "success")
    page.unroute("**/api/items", intercept)
    after = client.snapshot()
    new = [r for r in after if r["id"] not in {s["id"] for s in before}]
    assert len(new) == 1 and len(posts) == 1
    added(before, after, new[0], "Pilot notebook")
    page.reload()
    expect(button(page)).to_be_enabled()
    exact(names(page), [r["name"] for r in after])
    unchanged(after, client.snapshot())
    assert all(r["id"] not in page.locator("body").inner_text() for r in after)


@pytest.mark.parametrize("viewport", [(390, 844), (1440, 900)])
def test_UI05_confirmed_refresh_failure(page, client, viewport):
    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    before = opened(page, client)
    posts = []
    fail_get = [True]

    def intercept(route):
        if route.request.method == "POST":
            posts.append(route.request.post_data_json)
            route.continue_()
        elif fail_get[0]:
            route.fulfill(status=503, json=ERRORS["E-STORAGE"]["body"])
        else:
            route.continue_()

    page.route("**/api/items", intercept)
    field(page).fill("Pilot notebook")
    button(page).click()
    expect(page.get_by_text(CREATED_REFRESH_FAIL, exact=True)).to_be_visible()
    expect(button(page)).to_be_disabled()
    capture(page, client, "created-refresh-failed")
    after = client.snapshot()
    new = [r for r in after if r["id"] not in {s["id"] for s in before}]
    assert len(new) == 1
    added(before, after, new[0], "Pilot notebook")
    fail_get[0] = False
    page.get_by_role("button", name="Refresh list", exact=True).click()
    expect(button(page)).to_be_enabled()
    assert len(posts) == 1
    unchanged(after, client.snapshot())


@pytest.mark.parametrize("status", [422, 503])
@pytest.mark.parametrize("viewport", [(390, 844), (1440, 900)])
def test_UI06_UI12_definite_rejection(page, client, status, viewport):
    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    before = opened(page, client)
    intercepted = []

    def intercept(route):
        if route.request.method == "POST":
            intercepted.append(route.request.post_data_json)
            route.fulfill(status=status, json=ERRORS["E-LENGTH" if status == 422 else "E-STORAGE"]["body"])
        else:
            route.continue_()

    page.route("**/api/items", intercept)
    field(page).fill("Pilot notebook")
    button(page).click()
    if status == 422:
        expect(field(page)).to_have_attribute("aria-invalid", "true")
        expect(field(page)).to_be_focused()
    else:
        expect(page.get_by_text("Item was not created. Try again.", exact=True)).to_be_visible()
    expect(field(page)).to_have_value("Pilot notebook")
    expect(button(page)).to_be_enabled()
    capture(page, client, "validation" if status == 422 else "definite-failure")
    unchanged(before, client.snapshot())
    assert len(intercepted) == 1
    client.save("fault-causality", {"intercepted": 1, "forwarded": 0, "status": status, "scope": "browser-handler-only"})
    page.unroute("**/api/items", intercept)
    button(page).click()
    expect(page.get_by_text("Item created.", exact=True)).to_be_visible()
    after = client.snapshot()
    new = [r for r in after if r["id"] not in {s["id"] for s in before}]
    assert len(new) == 1
    added(before, after, new[0], "Pilot notebook")


FAULTS = [("internal-pre", 0), ("internal-post", 1), ("drop-pre", 0), ("drop-post", 1), ("timeout-pre", 0), ("timeout-post", 1)]


@pytest.mark.parametrize("fault,delta", FAULTS)
@pytest.mark.parametrize("failed_reconciliation", [False, True])
@pytest.mark.parametrize("duplicate", [False, True])
@pytest.mark.parametrize("viewport", [(390, 844), (1440, 900)])
def test_UI07_UI08_UI09_uncertainty(page, client, fault, delta, failed_reconciliation, duplicate, viewport, input_name="Pilot notebook"):
    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    opened(page, client)
    if duplicate:
        assert client.request("POST", body={"name": input_name})["status"] == 201
        page.reload()
        expect(button(page)).to_be_enabled()
    before = client.snapshot()
    posts, forwarded, gets = [], [], []
    interception = [True]

    def intercept(route):
        if route.request.method != "POST":
            gets.append(route)
            return
        posts.append(route.request.post_data_json)
        if not interception[0]:
            route.continue_()
            return
        if fault.startswith("internal"):
            client.control("configure", fault=fault)
            response = route.fetch(max_retries=0)
            forwarded.append({"status": response.status, "body": response.json()})
            client.save("internal-fault-proof", client.control("observe"))
            client.control("configure", fault=None)
            route.fulfill(response=response)
        else:
            if fault.endswith("post"):
                response = route.fetch(max_retries=0)
                assert response.status == 201
                forwarded.append({"status": response.status, "body": response.json()})
            route.abort("timedout" if fault.startswith("timeout") else "failed")

    page.route("**/api/items", intercept)
    field(page).fill(input_name)
    button(page).click()
    expect(page.get_by_text(UNCERTAIN, exact=True)).to_be_visible()
    expect(field(page)).to_have_value(input_name)
    expect(page.locator("form button[type=submit]")).to_be_disabled()
    capture(page, client, "uncertain")
    after = client.snapshot()
    new = [r for r in after if r["id"] not in {s["id"] for s in before}]
    assert len(new) == delta
    if delta:
        added(before, after, new[0], input_name)
    else:
        unchanged(before, after)
    assert len(posts) == 1 and len(gets) == 1
    if failed_reconciliation:
        gets.pop().fulfill(status=503, json=ERRORS["E-STORAGE"]["body"])
        expect(page.get_by_text(RECONCILE_FAIL, exact=True)).to_be_visible()
        expect(page.locator("form button[type=submit]")).to_be_disabled()
        capture(page, client, "reconciliation-failed")
        assert len(posts) == 1 and not gets
        page.get_by_role("button", name="Refresh list", exact=True).click()
        expect(page.get_by_role("button", name="Refresh list", exact=True)).to_be_visible()
        # Process the browser's explicit GET, without wall-clock retry loops.
        page.wait_for_function("document.readyState === 'complete'")
        assert len(gets) == 1
    gets.pop().continue_()
    expect(page.get_by_text(RECONCILED, exact=True)).to_be_visible()
    expect(field(page)).to_have_value(input_name)
    expect(page.locator("form")).to_have_count(1)
    expect(page.get_by_role("button", name="Create another item", exact=True)).to_be_enabled()
    exact(names(page), [r["name"] for r in after])
    assert len(posts) == 1
    capture(page, client, "reconciled")
    client.save("fault-causality", {"fault": fault, "forwarded": forwarded, "observed_delta": delta, "duplicate_preexisted": duplicate, "timeout_class": "browser transport timedout injection" if fault.startswith("timeout") else None})
    interception[0] = False
    page.get_by_role("button", name="Create another item", exact=True).click()
    expect(page.get_by_text("Item created. Updating the list…", exact=True)).to_be_visible()
    assert len(gets) == 1
    gets.pop().continue_()
    expect(page.get_by_text("Item created.", exact=True)).to_be_visible()
    final = client.snapshot()
    extra = [r for r in final if r["id"] not in {s["id"] for s in after}]
    assert len(extra) == 1 and len(posts) == 2
    added(after, final, extra[0], input_name)
    page.unroute("**/api/items", intercept)
    page.reload()
    expect(button(page)).to_be_enabled()
    unchanged(final, client.snapshot())


def test_UI09_initial_failure_and_reload_guard(page, client):
    client.reset()
    before = client.snapshot()
    held = []
    page.route("**/api/items", lambda r: held.append(r))
    page.goto(client.base_url, wait_until="domcontentloaded")
    expect(button(page)).to_be_disabled()
    field(page).fill("Pilot notebook")
    assert len(held) == 1
    held.pop().fulfill(status=503, json=ERRORS["E-STORAGE"]["body"])
    expect(page.get_by_text(INITIAL_FAIL, exact=True)).to_be_visible()
    expect(field(page)).to_have_value("Pilot notebook")
    expect(button(page)).to_be_disabled()
    page.get_by_role("button", name="Refresh list", exact=True).click()
    page.wait_for_function("document.readyState === 'complete'")
    assert len(held) == 1 and held[0].request.method == "GET"
    held.pop().continue_()
    expect(button(page)).to_be_enabled()
    expect(field(page)).to_have_value("Pilot notebook")
    page.reload(wait_until="domcontentloaded")
    expect(button(page)).to_be_disabled()
    assert len(held) == 1 and held[0].request.method == "GET"
    held.pop().continue_()
    expect(button(page)).to_be_enabled()
    unchanged(before, client.snapshot())


DISPLAY = [f for f in SPEC["name_cases"] if f["api_created_browser_display"]["required"]]
DISPLAY += [{"key": "markup", "request_name": '<img src="/should-not-load" onerror="window.injected=true">', "expected_stored_name": '<img src="/should-not-load" onerror="window.injected=true">'}]


@pytest.mark.parametrize("f", DISPLAY, ids=lambda f: f["key"])
def test_UI10_API_created_display(page, client, f):
    client.reset("F-EMPTY")
    before = client.snapshot()
    r = client.request("POST", body={"name": f["request_name"]})
    after = client.snapshot()
    assert r["status"] == 201
    added(before, after, r["json"], f["expected_stored_name"])
    requests = []
    page.on("request", lambda r: requests.append(r.url))
    for _ in range(2):
        page.goto(client.base_url)
        expect(button(page)).to_be_enabled()
        exact(names(page), [f["expected_stored_name"]])
        expect(page.get_by_role("listitem").locator("img,script,iframe,svg")).to_have_count(0)
        assert page.evaluate("window.injected === undefined")
        assert not any("should-not-load" in url for url in requests)
    unchanged(after, client.snapshot())


@pytest.mark.parametrize("viewport", [(390, 844), (1440, 900)])
def test_UI11_empty_plural_VIS02_long(page, client, viewport):
    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    before = opened(page, client, "F-EMPTY")
    expect(page.get_by_text("0 items", exact=True)).to_be_visible()
    expect(page.get_by_text("No items yet. Create the first item.", exact=True)).to_be_visible()
    capture(page, client, "empty")
    for count, text in enumerate(["A" * 80, "📓" * 80, "e\u0301" * 40, "<b>Synthetic</b>"] + [f"Synthetic long list {i}" for i in range(20)], 1):
        field(page).fill(text)
        button(page).click()
        expect(page.get_by_text("Item created.", exact=True)).to_be_visible()
        expect(page.get_by_text(f"{count} item" + ("s" if count != 1 else ""), exact=True)).to_be_visible()
        assert names(page)[-1] == text
    capture(page, client, "long-list")
    page.set_viewport_size({"width": 320, "height": 844})
    page.add_style_tag(content="*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}")
    capture(page, client, "320-text-spacing")
    assert len(client.snapshot()) == 24 and before == []


@pytest.mark.parametrize("text", ["A"*80, "📓"*80, "e\u0301"*40, "<b>Synthetic</b>"])
@pytest.mark.parametrize("viewport", [(390,844),(1440,900)])
def test_VIS02_long_uncertain_states(page,client,text,viewport):
    test_UI07_UI08_UI09_uncertainty(page,client,"internal-post",1,True,False,viewport,text)


@pytest.mark.parametrize("text", ["A"*80, "📓"*80, "e\u0301"*40, "<b>Synthetic</b>"])
@pytest.mark.parametrize("viewport", [(390,844),(1440,900)])
def test_VIS02_long_error_states(page,client,text,viewport):
    page.set_viewport_size({"width":viewport[0],"height":viewport[1]})
    before=opened(page,client)
    def reject(route):
        if route.request.method=="POST":
            route.fulfill(status=422,json=ERRORS["E-LENGTH"]["body"])
        else: route.continue_()
    page.route("**/api/items",reject)
    field(page).fill(text)
    button(page).click()
    expect(field(page)).to_have_attribute("aria-invalid","true")
    expect(field(page)).to_have_value(text)
    capture(page,client,"long-validation")
    unchanged(before,client.snapshot())
