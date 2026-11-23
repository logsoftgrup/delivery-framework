# DEP-SUPPLY-1 independent static review — R1

**Static disposition: CHANGES_REQUIRED.** One medium defect, DEP1-R-01, prevents
complete failure evidence: the helper discards the real child exit status.
**Execution readiness: UNAVAILABLE**, independently of that defect, because
actual runner/tool/isolation and complete endpoint/egress evidence are absent.
No workflow, supplier, container, browser or acceptance test was executed.
This report is evidence on LOGA-23, not a native decision on LOGA-24 or TC.V.

## Identity and authorized scope

Reviewer: Independent Assurance `ce8e0a2f-a532-45cb-abeb-a3937e9be71e`, run
`25f7e3be-9e5f-4d26-96ef-856117f2a882`, provider session UNKNOWN. Evidence task LOGA-23.
Original producer: Engineer `07abe685-fbb1-4658-9dbe-187d9fe540aa`, LOGA-24.
Review requested by comment `27e78366-9078-4a4f-8a21-e30074df0fbb` under CEO
coordinator direction revision `32ab8f98-5869-4abe-858c-2514942b8a9e`.
Producer publication revision `a1dd8eab-7c4a-488e-9c08-eaa31ce3ad7e` was read.

Candidate **DEP-SUPPLY-1**, repository
`https://github.com/logsoftgrup/delivery-framework.git`, immutable commit
**`11850c330b676270e11c95107e3cef3ddf588caa`**, producer branch locator
`smoke/phase-b`. Exact Git fetch succeeded. All seven listed source files and
manifest were retrieved and independently matched by byte length and SHA-256.
The source diff from retained APP preparation
`3656f0cac2165e6b8f126ec0094776c8a060b9b1` contains only these eight files.

Manifest: `pilot/delivery-lab/manifests/dependency-supply-1.json`, SHA-256
`91f9e4b3c909ef9c9f401d2310cb10be53172087e72eb383bedcaa65f3baabba`.
The seven files below are under `pilot/delivery-lab/container/dependency-supply/`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `README.md` | 15585 | `b391b1df9b9d91d0e57033aee839e33ea5e3ed0eac597d9d472f096a99c7d74d` |
| `app-input.json` | 1003 | `722aed96535641d8be12cf5685ff4b73ab0b148b51ca362bccd4e9120e3a5176` |
| `operator-preflight.example.json` | 1123 | `8ceca00fa6aba0b3976ef9fce380eebe9966a3deb298700f43e2057b468774e7` |
| `supply.py` | 31057 | `e266a1f2222edfb8e4a16be578316d0b0ba95173a0839d3498e1f11ac962f0d6` |
| `test-input-interface.json` | 1426 | `d5e7aade9830458f200dc474208da4639b1f1ffc90fd6e1e28cbae182b5b5f67` |
| `verify_bundle.py` | 4903 | `0870acb3e911bb25aa1df82554e85368edebc0f498e5f225128c3482ad59d37c` |
| `workflow.yml.in` | 7845 | `9981ad3e051ce51799ac8652eb212f9b87f3af93593306f33641d1c0bc1bb110` |

Criteria: **TEST-SUPPLY-1** commit
`a94938bfcb37745c93843816a66d990cc46d888e`, contract
`pilot/delivery-lab/assurance/supply/test-runtime-contract.v1.json`
(SHA-256 `c8265cd20750d54677fba4944d4307a07820cdcebde408b6621b159b7093523d`),
verification `test-runtime-verification.v1.md`
(SHA-256 `60b330174778aa4315e97125737a77def723a80306917654277a86de08b64c24`),
input manifest SHA-256
`76a8a98ab7a47ed6f0045b715c6495841a33466db826b8adf731cca115e978c6`.
Native publication revision `ab060d2c-5ca0-4b10-9a3d-e005c72b9ccc`.
The candidate's TEST reference and requirements hashes match these actual files.

TC-D1 `47199f8ad78ad0b1c1ebae1487acfa79cb644937`, accepted BASE-3
`a76f458655c9bd2a8ef95562651e0c9155f6a878` and TS-3
`de46dadeb45c76280b0a99630303fb7666798789` are unchanged. Assurance has not
accepted any test artifact it authored or edited Engineer's candidate.

## Method and limits

Manual static examination covered all seven source files, their manifest,
workflow steps, helper control flow, archive verification and stated operator
procedures. JSON and Python AST parsing were read-only consistency checks;
no candidate module was imported or executed. The producer's reported 27 checks
were not replayed or treated as independent evidence. The counterexample below
is a manual source trace, not an observed dependency-job execution.

Own configured repository and Git root matched the Assurance workspace; own
branch `assurance/phase-b` was clean at TEST-SUPPLY-1 before writing this report.
Candidate source was read into a protected temporary evidence directory; no
checkout of Engineer's branch and no use of Engineer credentials occurred.
No denied-route retries, egress probes, host changes, dependency acquisition,
workflow publication/dispatch or test-suite changes occurred.

## TSP-01–TSP-05 results

PASS in this table is restricted to the specified static finding. It is not
execution permission, supplied-artifact acceptance, native source approval or
independent qualification of TC-D1.

| Check | Result | Evidence and reasoning |
|---|---|---|
| TSP-01 — source identity and authority | PASS, static identity | Exact fetch, manifest and seven file digests match. TEST interface pins the contract commit and hashes; `supply.py` 338–355 binds source/contract/requirements. The eight-file change scope excludes application and suite implementation. |
| TSP-02 — workflow scope | PASS, static scope | `workflow.yml.in` 5–22 declares manual dispatch and read-only contents permission; 49/71 and repeated job steps pin GitHub-authored actions by SHA; checkout disables credential persistence. APP/TEST jobs are exclusive by input, with separate artifacts. No deploy/PR/schedule trigger or continue-on-error exists. Exact action availability/support and operator permission remain preconditions, not verified runtime facts. |
| TSP-03 — target separation | PASS, static design | `app-input.json` proposes CPython 3.13.18/Bookworm for APP; TEST interface requires CPython 3.12.3/x86-64/glibc 2.39 and pytest 8.4.2/Playwright 1.56.0. `supply.py` 125–132, 269–282, 338–377 checks target properties; distinct output/locks/bundles prevent APP wheels substituting for TEST. Compatible tags and actual versions remain run-derived. |
| TSP-04 — runner and endpoint readiness | UNAVAILABLE | The receipt example is explicitly false with unfilled image/tool/endpoints. README 41–105 requires operator verification before dispatch and acknowledges that the URL guard does not govern pip, Docker or action traffic. Selected runner label and guarded URL prefixes do not demonstrate actual runner/egress. No complete permitted endpoint/redirect inventory or isolation proof was supplied. |
| TSP-05 — reproducibility and failure handling | FAIL, DEP1-R-01 | `supply.py` 158–205 resolves compatible binary wheels, saves hashes/locks and separates toolchain inventory; 285–335 derives browser closure and hashes; 367–451 checks isolation, browser identity, libraries and creates the complete manifest/archive only after success. The failure path at 53–57/477–480 loses child exit status, contrary to required real-status evidence and README 173. Other missing runtime/tool/hash facts remain explicit preconditions. |

## DEP1-R-01 — child failure exit status is discarded

Severity: **medium**. Owner: original Engineer on LOGA-24. Affected exact file:
`pilot/delivery-lab/container/dependency-supply/supply.py` at candidate
`11850c330b676270e11c95107e3cef3ddf588caa`, SHA-256
`e266a1f2222edfb8e4a16be578316d0b0ba95173a0839d3498e1f11ac962f0d6`.
Primary [lines 53–57](https://github.com/logsoftgrup/delivery-framework/blob/11850c330b676270e11c95107e3cef3ddf588caa/pilot/delivery-lab/container/dependency-supply/supply.py#L53); terminal [handler lines 477–480](https://github.com/logsoftgrup/delivery-framework/blob/11850c330b676270e11c95107e3cef3ddf588caa/pilot/delivery-lab/container/dependency-supply/supply.py#L477). README line 173 states
that logs retain real exit status, but this implementation does not ensure it.

Expected: TEST-SUPPLY-1's required bundle evidence retains complete operation
logs with real exit statuses. Its TSP-05 failure handling and TSP-11 evidence
contract require a reviewer to distinguish the actual command result, including
failure/signal outcomes, from the wrapper/job result. The command identity and
result must be saved before control flow raises or terminates.

Actual static trace:

1. `run()` opens the child log and sends only stdout/stderr into that file.
2. It receives `result.returncode`, but uses that value solely in a Boolean
   `require(result.returncode == 0, "command failed; inspect " + log.name)`.
3. On any nonzero status, `require()` raises a generic ValueError. No numeric
   return code or command-result receipt is written or returned.
4. The top-level handler prints the generic error and exits 1. A nested helper
   adds another wrapper failure; diagnostic uploads preserve output logs but
   cannot reconstruct the discarded original status.

Manual counterexample: a child that emits no output and exits 42 produces an
empty child log, generic command-failed detail and helper exit 1. A child with
another nonzero status can produce the same saved evidence. The source cannot
guarantee retention of exit 42. This is a deterministic control-flow finding;
no child, browser, supplier or workflow was executed to make it.

Impact: the job correctly fails and does not publish a success bundle, so this
is **not** a false-success finding. However, required failure/recovery evidence
cannot distinguish the child outcome from wrapper failure, undermining precise
triage and interrupted-operation reconciliation.

Required producer correction: persist a sanitized command identity and actual
return/signal status, with full stdout/stderr evidence references, before raising
on failure; retain that receipt in the diagnostic artifact. Preserve the existing
fail-closed behavior and avoid recording credentials or signed request material.
The return/signal status must remain distinguishable from the wrapper exit code.

Re-examination criterion: a new immutable candidate and candidate-bound producer
evidence distinguish successful and different nonzero/signal child outcomes,
including a child that writes no output, while the wrapper still fails on a child
failure. Assurance will re-examine the changed helper/evidence/upload path on
LOGA-23. This request does not authorize a dependency transfer, workflow dispatch,
new platform test or any additional privileged action.

## Other observations and remaining gates

The workflow verifies the administrator-published workflow bytes against the
reviewed inert file. Exact actual publication/workflow commit remains absent.
Its action commits are syntactically pinned to the permitted GitHub namespace;
this review did not independently retrieve action internals or prove current
runner support. The operator must establish those facts before execution.

The browser plan is derived from the verified Playwright package registry and
retains chromium/headless-shell/ffmpeg archives, descriptor and extracted-tree
hashes. No actual Playwright wheel, browser revision/hash, library inventory or
successful launch is available yet. Proposed sudo/unshare loopback isolation is
an unverified operator prerequisite, not an authorization granted by this report.

The byte verifier checks archive hash, extraction constraints, manifest coverage,
lock grammar and APP OCI references. It explicitly returns BYTES_VERIFIED, not
runtime or retention acceptance. Its advertised boundary is preserved; TSP-06–11
must still verify returned bytes/platform/lock/browser identity and independently
consume them using already-authorized confinement. No library/tool/bootstrap
availability is inferred from static source.

Successful payload provenance is separate from post-upload artifact identity:
README 175–188 requires actual run/job/attempt/artifact and persistent-copy receipts
outside the immutable uploaded archive. No artifact ID, archive hash, expiry,
permitted retrieval path or verified persistent copy was supplied. Those facts
cannot be cleared by this static report.

TC-BLK-01 remains open. This review produces no native source decision and does
not release TC.R/TC.V, accept a TEST bundle or application, or replace any human
acceptance gate. The retained operator route question is answered; the existing
LOGA-24 artifact question remains pending until usable artifact references exist.

## Handoff and continuation

At entry and pre-report, LOGA-23 is in_progress under Assurance, executionState
null, with the Engineer non-author review policy retained. LOGA-24 is under the
original Engineer and its prior changes_requested return path points to Engineer;
its residual currentParticipant field is not permission for Assurance to decide
that source during producer preparation. Only evidence is returned here.

Next Engineer action: correct DEP1-R-01, publish exact new supplier SHA/paths/hash
and affected evidence. CEO retains the coordination path for unresolved runner,
endpoint/egress and later artifact facts. Assurance re-examines new exact inputs;
no completed BASE/TS hold or circular dependency is added.

Save this report, its immutable publication identity, limitations and native
continuation on LOGA-23 and read them back before the final blocked transition.
Return the exact report revision to LOGA-24/20. No post-transition comment or
command is required. A later wake must reconcile current native participant/
return and durable evidence before another consequential operation; absent
receipts remain UNKNOWN, not proof of non-execution or permission to retry.
