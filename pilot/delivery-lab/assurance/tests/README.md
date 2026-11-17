# Delivery Lab executable assurance suite — TC draft 1

**Not released for TC.R/TC.V or application acceptance.** This draft belongs to
LOGA-23 and its original Assurance producer. Engineer owns the later separate
LOGA-28 TC.R and LOGA-29 TC.V examinations and native non-author source review.
No author result accepts this suite. API-05 is an ordinary required 422/no-write
assertion for both C0 and C1. C0 acceptance/insert must fail the application run.

## Exact inputs and scope

- BASE-3 `a76f458655c9bd2a8ef95562651e0c9155f6a878`, eight files in
  `pilot/delivery-lab/docs/`.
- TS-3 `de46dadeb45c76280b0a99630303fb7666798789`, twelve files in
  `pilot/delivery-lab/assurance/scenarios/`.
- F2 `5c594e3087d68a8862072998478864f6ee18a253` continuation and native review rules.
- Incoming native release packet revision `ea3ef167-8a13-4cd6-80f2-a3d88cf0d0e8`
  on LOGA-23. Exact upstream path hashes are in `spec/inputs.json`.
- `spec/fixtures.json` is a byte-identical copy of the accepted scenario fixture
  file, including separate literal API, browser entry and API-created display
  oracles. No application implementation was used to derive expectations.

Only this directory is authored. `manifest.json` hashes every tracked suite
file except itself. The enclosing full commit and manifest checksum belong in
the native publication packet, avoiding self-referential commit hashes.

## Execution prerequisites and current blocker

The authored runtime targets CPython **3.12.3**, Linux x86-64, pytest **8.4.2** and
Playwright Python **1.56.0**, using that Playwright distribution's Chromium.
`requirements.in` pins the two direct dependencies. **The full hashed dependency
lock and verified browser revision are not yet available.** The configured proxy
rejected `/simple/pytest/` with HTTP 403. Neither Python package is installed;
`chromium-browser` is a launcher for an absent snap. No proxy bypass, mirror,
host install, credential expansion or system-browser substitution was attempted.

CEO must coordinate a permitted pinned package/browser artifact route or an
authorized existing environment. Then the producer must retrieve through that
route, pin every transitive wheel and hash, verify compatibility/browser identity,
run real pytest collection and producer checks, correct this draft as necessary,
and publish a new ready candidate. Until then syntax/offline/API-smoke checks are
limited producer evidence. **No pytest or browser PASS is claimed.**

Application execution additionally requires an accepted full suite and a reviewed
QA operator adapter with exact digest. `support/safety.py` defines its request /
receipt interface; it does **not** supply an application-specific reset, storage
fault, received-request seam or restart implementation. That runtime adapter must
be supplied/reviewed against the exact future application/configuration under the
existing assignments. Missing adapter or causal observation is UNAVAILABLE.
Browser interception alone never proves an actual server's pre/post-commit fault.

## Commands after the prerequisite is resolved

Run from this directory with the pinned Python environment. Installation must
use the eventual reviewed, hashed lock; do not install from `requirements.in`
and call the environment locked. No command below installs dependencies.

```bash
python run.py --kind fixture --profile api --evidence /tmp/tc-api-unique-run
python run.py --kind fixture --profile browser --evidence /tmp/tc-browser-unique-run
python run.py --kind fixture --profile all --evidence /tmp/tc-full-unique-run
python qualification/run.py /tmp/tc-independent-qualification-unique-run
python qualification/vectors.py /tmp/tc-independent-offline-unique-run
python run.py --kind qa --profile all --packet /absolute/reviewed-qa-packet.json --evidence /absolute/authorized/new-evidence-directory
```

Evidence directories must not already exist. The runner uses serial tests; do
not add xdist/parallel writers. `--select` and mutations are fixture qualification
only and refused for QA. Use `TC_SESSION_ID` to record an independently verified
current provider session; if absent the record says UNKNOWN. Do not invent it.
Actor/task/run come only from the executing actor's own Paperclip context.

The fixture controller binds `127.0.0.1` to an OS-assigned free port in the
executing process's network namespace. Every HTTP receipt records that actual
route; the thread is stopped on teardown. It is a synthetic test double, without
Docker, public ports, review data or a reset endpoint on its HTTP surface. Its
`/api/version` synthetic source (`f` repeated 40 times) is deliberately not an app
candidate claim. The enclosing suite commit identifies the fixture bytes. Its
logical restart and admission telemetry qualify assertions only; they are not
real process/container durability or infrastructure isolation evidence.

## Test and evidence behavior

`support/parameters.py` expands 147 literal API and 440 Host/Origin/priority
parameter cases before the additional data/security tests. Parameter IDs retain
the scenario and input key; requests are captured as bytes and hashes, responses
with exact JSON types/member sets, and snapshots as full ordered tuples. Raw
header multiplicity is preserved. A parser refusal without application dispatch
is recorded separately, not silently credited as E-HOST/E-ORIGIN.

Browser tests use accessible roles and names, exact per-fixture pre-submit values,
network request counts and complete API snapshots. Native setters are used only
for the 28 specified controlled control-character setups, with before-event and
after-event checkpoints. The other 74 use browser keyboard text/IME insertion,
recorded as such; this does not assert a physical human keyboard or clipboard.
API-created CR/LF/control names have separate DOM text tests. The suite never
learns an expected string from observed app output.

Fault injection records forwarding, returned 201/500 and tuple effects. It covers
definite pre-forward 503, pre/post-commit 500, pre/post-forward dropped response,
and browser transport `timedout` errors. The latter is a controlled timeout error,
not a measurement of a real timeout deadline/SLA. Every uncertain variant tests
successful and failed reconciliation, preexisting duplicate names, deliberate
second creation, reload and zero automatic POST retry. UI-12 intercepted 422 is
browser handler evidence; direct API-04/05 supplies genuine API rejection checks.

Screenshots/traces/DOM and the versioned `TC-1-dom-audit` results are retained.
The scanner checks a narrow set of semantics, label/error references and bounds;
it does not claim complete accessibility, contrast, focus or screen-reader
coverage. Manual procedures below remain mandatory even when automation passes.

Runner exit codes: **0 automated PASS**, **1 assertion FAIL**, **2 UNAVAILABLE**,
**3 UNKNOWN**. Setup errors, missing packages, transport uncertainty, stale result
identity, zero collection and missing artifacts cannot become PASS. Full stdout
and stderr are file-backed. The console prints only a small summary. Each run
records prepared / dispatch-started / response-confirmed / evidence-saved where
observable; a stopped run is UNKNOWN and must be reconciled before retrying a
consequential operation. No exactly-once or general retry promise is made.

## Separate harness verification

The independent Engineer first runs the full good synthetic fixture, then each
bad mutation separately and the matching good restoration. The driver requires
an ordinary assertion FAIL for the intended bad run; unrelated crashes,
UNAVAILABLE, timeouts or zero collection earn no detection credit. In particular
`c0-accept` and `reject-writes` both must fail API-05. `qualification/vectors.py`
adds isolated tuple/safety/identity/result/recovery/role record discriminators
without any service mutation. This synthetic qualification is not a C0 app PASS.

For manual HAR-06, run browser cases on `low-contrast` and `hidden-focus` fixture
mutations and inspect saved screenshots plus focused states. Record the actual
manual defect; an automated subset may remain green. Never update a golden image
to accept the defect. HAR-12 requires examination of real evidence authorship and
native decisions; synthetic metadata shapes cannot authenticate a human verdict.

## Manual and operational obligations

`manual/` preserves six exact accepted TS files. Start with `manual/coverage.md`,
then use the entire applicable procedure, not only an illustrative example:

- VIS-01/02 inspect all state captures at 390×844 and 1440×900 against the exact
  BASE-3 reference. VIS-03 and AX-02–06 require actual zoom, keyboard, contrast,
  pointer and screen-reader observations with tool/OS/browser identities.
- `manual/accessibility.md` contains the complete scoped A/AA applicability map.
  Every criterion needs findings and an applicability rationale; N/A is reviewed,
  not inferred by a scanner. An unavailable AT/zoom route remains UNAVAILABLE.
- PKG-01/03 require real clean build/lock/base/CI/artifact retrieval and provenance.
  PKG-02's metadata assertions supplement inspection of inventory, layers, logs,
  mounts and the actual authorized running container. Metadata alone is not a
  clean build or a no-secrets certification.
- OPS-01–09 keep Engineer as operator, Assurance as independent observer. Supply
  the exact isolated QA route/resource identities and reviewed adapter before any
  mutation. Record actual process/container restart, consistent SQLite/WAL backup,
  restore and final C1 identity/tuples. The recovery validator is an evidence check,
  not a deployment or rollback engine. Retain the exact OBS-02 qualifying subset;
  O2 completion is not a prerequisite to exercising O2, and C0 is never a target.
- LIFE-01–05 require real C0 FAIL, native original-producer return, fresh-session
  continuation, C1 re-examination and authorized human acceptance. No platform
  test, manual reassignment or agent-authored human verdict substitutes.
- HUM-01/02 and AX-08 retain the human's own journey, visual/usability and final
  verdict. No invented time limits, synthetic transcript or agent proxy verdict.

Complete `manual/record-template.json` with actual exact identities, artifacts,
findings/limitations and responsible next actor on the assigned examination.
Keep separate reports on LOGA-28/29; native source submission waits for both and
must be the producer run's final required action after a saved/read-back handoff.
