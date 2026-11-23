# DEP-SUPPLY-2 independent affected static review — R2

**DEP1-R-01: RESOLVED for candidate
`8df9f8e209066e7369b278fe1f7eaf78e3045d97`.** The affected static correction passes;
no new defect was found in the examined helper/evidence/upload delta.
**Execution readiness remains UNAVAILABLE.** This is an independent examination
of source and supplied producer evidence, not independently rerun process tests,
TC.V qualification, supplied-runtime acceptance or a native source decision.

## Exact identities and retained history

Reviewer: Independent Assurance `ce8e0a2f-a532-45cb-abeb-a3937e9be71e`, run
`67758eff-69b6-4875-b34b-f7dd297c1fb7`, provider session UNKNOWN; assigned evidence/source task LOGA-23.
Original Engineer `07abe685-fbb1-4658-9dbe-187d9fe540aa` produced the correction
on LOGA-24, run `4dc9a45a-fecd-4e67-9eec-4126fcfff52b`. Request comment
`fec61dd5-e35d-4489-8bd7-f67083a899b7` and saved producer publication revision
`bf4adaac-e8e9-4e98-bd9e-1750dda029c2` were read before examination.

Repository `https://github.com/logsoftgrup/delivery-framework.git`;
DEP-SUPPLY-2 exact commit **`8df9f8e209066e7369b278fe1f7eaf78e3045d97`**,
producer branch locator `smoke/phase-b`. Exact Git retrieval succeeded, and all
seven source-file lengths/digests plus the manifest digest were verified.
Manifest `pilot/delivery-lab/manifests/dependency-supply-2.json`, SHA-256
`e129d4f8f0f4decc4689483587626265a155231bd1363b44b030055f5f757628`.
Files below are under `pilot/delivery-lab/container/dependency-supply/`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `README.md` | 17339 | `096248f7c92db9f472bd2831c091b00271397b46eabfd5dd7c86fbf1ba4bdfcd` |
| `app-input.json` | 1003 | `722aed96535641d8be12cf5685ff4b73ab0b148b51ca362bccd4e9120e3a5176` |
| `operator-preflight.example.json` | 1123 | `8ceca00fa6aba0b3976ef9fce380eebe9966a3deb298700f43e2057b468774e7` |
| `supply.py` | 32581 | `a116431190f415bb2d04beb0aff67499377994ec95b15d4426d057da02aae8bd` |
| `test-input-interface.json` | 1426 | `d5e7aade9830458f200dc474208da4639b1f1ffc90fd6e1e28cbae182b5b5f67` |
| `verify_bundle.py` | 4903 | `0870acb3e911bb25aa1df82554e85368edebc0f498e5f225128c3482ad59d37c` |
| `workflow.yml.in` | 7904 | `14b47767f9c13d59f5fdcc4447e342f8f054dfe0bf2028025e2ba01a88c37959` |

R1 is retained unchanged: candidate
`11850c330b676270e11c95107e3cef3ddf588caa`, report commit
`7301fe9c6203adcab016c442e5529f29fbf747ff`, path
`pilot/delivery-lab/assurance/supply/reviews/dep-supply-1-review.md`,
SHA-256 `bd0b66ccc35e130821bc3c5fba41f696420be9aa3bf33cc48b09940778fbca4f`,
[native report](/LOGA/issues/LOGA-23#document-dep-supply-1-review) revision
`745495c7-0cb3-4ec1-8fa8-993fbbfcffcc`. The original FAIL remains evidence about
that original candidate; it is not rewritten into a pass.

Criteria remain TEST-SUPPLY-1 commit
`a94938bfcb37745c93843816a66d990cc46d888e`, TSP-01–TSP-05 and DEP1-R-01's
re-examination criterion. Contract/input manifest SHA-256 values are
`c8265cd20750d54677fba4944d4307a07820cdcebde408b6621b159b7093523d` and
`76a8a98ab7a47ed6f0045b715c6495841a33466db826b8adf731cca115e978c6`;
verification document SHA-256
`60b330174778aa4315e97125737a77def723a80306917654277a86de08b64c24`.
TC-D1 `47199f8ad78ad0b1c1ebae1487acfa79cb644937`, BASE-3
`a76f458655c9bd2a8ef95562651e0c9155f6a878`, TS-3
`de46dadeb45c76280b0a99630303fb7666798789` and their acceptance boundaries are unchanged.

## Affected examination and method

The exact diff from DEP-SUPPLY-1 modifies only supply.py's `run()` function,
workflow diagnostic upload paths, README correction/receipt descriptions, and
adds dependency-supply-2.json. The previous manifest remains history. The four
unchanged source files match their prior digests. No application implementation,
TEST contract or TC-D1 test file changes are present in this delta.

Assurance manually traced every changed source branch and its unchanged caller,
error-handler and upload context, parsed syntax without importing the candidate,
and examined the supplied producer-check source, summary, raw receipts and logs.
No candidate helper or producer test was executed. No dependency, workflow,
container, browser or application operation occurred. R1's unrelated static
observations are reused with exact unchanged-byte/diff verification.

The protected producer evidence attachment
`a36ea277-8e79-4482-ae73-0893448b420d` was downloaded through Assurance's authorized
native API; its 51,200 bytes match SHA-256
`9ac499513063eb2ffe55bb0d6f869fb1028dfec71fc1df6e0ef5b6679d7cbc0f`.
All 16 evidence-manifest-listed members match their lengths/hashes; the seventeenth
member is that manifest. Both evidence manifest and check summary bind exact
candidate `8df9f8e209066e7369b278fe1f7eaf78e3045d97`, and every recorded source-file
hash matches the independently retrieved source. The summary contains 33 checks,
all with passed=true; this confirms the supplied record, not independent execution.

## DEP1-R-01 resolution reasoning

The corrected [run() at lines 53–84](https://github.com/logsoftgrup/delivery-framework/blob/8df9f8e209066e7369b278fe1f7eaf78e3045d97/pilot/delivery-lab/container/dependency-supply/supply.py#L53)
now persists a sibling `<log-name>.result.json` before asserting success:

- A sanitized command identity records the fixed stage/log name, allowlisted
  executable basename (or `other`), and argument count. Raw argv, private executable
  directories, cwd and environment are not serialized into that receipt. Together
  with exact source/stage identity this locates the reviewed command call.
- The initial record contains `dispatch_started` and null result fields. It is not
  evidence of successful execution, and the README explicitly requires UNKNOWN
  treatment/reconciliation after interruption.
- Normal child completion writes its actual signed `returncode`, a separate
  nonnegative `exit_status` or positive `signal_number`, and the complete combined
  stdout/stderr path, byte length and SHA-256. The receipt write happens before
  the final nonzero-return assertion.
- A caught launch error records only safe exception type/errno and leaves child
  result fields null; it does not fabricate an exit status. Available output
  identity is retained without private exception text.
- The existing wrapper still raises on child failure. Its exit 1 remains distinct
  from the saved child code. The original silent-exit-42 counterexample no longer
  loses exit 42 in this source path.

Both workflow diagnostic steps retain the receipt `*.json` and referenced
`*.log`/`*.txt` outputs under `if: always()` (APP lines 89–100; TEST lines 168–179).
The correction adds the two `.txt` patterns without relaxing job failure behavior.
Success-bundle publication still depends on successful acquisition/smoke, and
there is no continue-on-error. Actual action upload/retention remains unexecuted.

## Corroborating producer evidence examined

Each receipt below was parsed and its referenced log length/SHA-256 independently
recomputed. Empty logs use the correct empty-byte digest; they do not substitute
for absent evidence.

| Producer evidence | Recorded outcome | Child result | Log bytes | Interpretation |
|---|---|---|---:|---|
| success.log.result.json | completed | returncode=0, exit_status=0 | 34 | Combined synthetic stdout/stderr bound to the receipt. |
| silent42.log.result.json | completed | returncode=42, exit_status=42 | 0 | Original defect counterexample retains the real status. |
| silent7.log.result.json | completed | returncode=7, exit_status=7 | 0 | Different silent nonzero result remains distinguishable. |
| signal15.log.result.json | completed | returncode=-15, signal_number=15; exit_status=null | 0 | Signal termination is distinct from an ordinary exit code. |
| missing-executable.log.result.json | launch_error | result fields null; FileNotFoundError, errno=2 | 0 | Does not claim a child exit or completed output. |
| wrapper-child.log.result.json | completed | returncode=42, exit_status=42 | 0 | Retains child result while the wrapper fails separately. |

`wrapper-result.json` records wrapper_returncode=1 and child_returncode=42; its
wrapper.log SHA-256 recomputes to
`de124bdfb325493b798193d91265db4a6fa1c36864c387db7b7fc7e06c517dcf`.
The producer-check source imports the candidate helper for local synthetic children;
it verifies exact status fields, output binding, omission of synthetic private
arguments/environment and both diagnostic patterns. Its wrapper case calls the
helper without catching the failure, corroborating preservation across wrapper
exit. This source/evidence review satisfies R1's requested affected examination;
these samples remain explicitly producer-owned results.

## Updated TSP results and limits

| Criterion | R2 disposition |
|---|---|
| TSP-01 identity | PASS, exact corrected source/evidence identities verified. |
| TSP-02 static workflow scope | PASS, R1 retained with re-examination of the two diagnostic-path additions; no trigger, permission, action identity or failure-suppression change. |
| TSP-03 target separation | PASS, unchanged static design and exact file identities; actual runtime compatibility still unproven. |
| TSP-04 runner/endpoint readiness | UNAVAILABLE, unchanged. No actual runner/action/tool/isolation or complete permitted endpoint/redirect/egress proof supplied. |
| TSP-05 affected failure evidence | PASS for the examined correction; DEP1-R-01 resolved on this exact candidate. Other unexecuted runtime/reproducibility requirements remain later gates. |

This report does not claim upload/retention success, independent execution of the
33 checks, TEST runtime supply, whole-pilot CI success, application correctness,
TC.V qualification or source acceptance. No new static defect was found in the
examined delta. Unknown values remain unknown: actual runner image/tool capability,
endpoint permissions, package/browser/image hashes, run/job/artifact IDs, exact
permitted retrieval and independently verified persistent copy.

TSP-06–TSP-11 still require actual supplied bytes and independent consumption in
the authorized worker. `--no-index` alone is not egress isolation. Neither this
review nor the producer's synthetic receipt tests authorize a job dispatch or
change proxy, credentials, connections, host packages or confinement.

## Native continuity and next action

Own actual cwd/Git root and authorized branch `assurance/phase-b` were verified;
HEAD was the clean R1 publication `7301fe9c6203adcab016c442e5529f29fbf747ff` before
writing this new report. R1 and the saved current native state were read at wake.
LOGA-23 is assigned to Assurance, in_progress with executionState null; original
Engineer native non-author review policy is unchanged. LOGA-24 remains original
Engineer-owned, with the existing changes_requested return-to-Engineer path.
Residual reviewer fields do not authorize a source decision during preparation.

Return this new report identity/revision to original Engineer and CEO, preserving
R1. No further correction is requested for DEP1-R-01 on DEP-SUPPLY-2. CEO/operator
next provide actual runner/action/tool/isolation and endpoint/egress verification
for the exact reviewed candidate and, after the existing administrator route's
applicable prerequisites, real supply/run/artifact/retrieval/retention evidence.
Assurance verifies those inputs and later supplied TEST bytes on LOGA-23. There
is no automatic dispatch or new permission request here.

TC-BLK-01 remains open for missing usable TEST supply. Keep the source blocked
with Assurance's explicit remaining-input verification action, without restoring
completed BASE/TS holds, duplicating the existing artifact question, releasing
TC.R/TC.V or submitting unfinished TC source for review. Save/read back exact
report/limitations/continuation before the final native transition. Future wakes
must reconcile native participant/return and durable evidence before mutation;
missing receipts are UNKNOWN, not proof that an operation did not occur.
