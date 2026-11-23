# TEST-SUPPLY-1 verification contract

This suite-owned preparation input accompanies
`test-runtime-contract.v1.json`. It does not modify the TC-D1 test suite,
its expected outcomes, or its candidate status. TC-D1 remains the exact
`47199f8ad78ad0b1c1ebae1487acfa79cb644937` tree under
`pilot/delivery-lab/assurance/tests/`. Its manifest SHA-256 is
`f04388ba40df8e6868f5539924e3a491218566c4457df2732c98cc5ab6201dd8`.
The publication packet identifies this contract's enclosing commit and file
digests; those are distinct from the suite identity.

The authenticated operator answer and CEO direction are pinned in the JSON.
They select administrator-operated GitHub Actions preparation. They supply
neither ready artifacts nor proof of runner availability or permitted egress.
Engineer owns the dependency-only workflow and APP inputs on LOGA-24. Assurance
owns TEST requirements and records independent examination of Engineer's exact
workflow/artifact references on LOGA-23 when supplied. CEO joins the references
on LOGA-20. Daniela/OpenClaw publishes through Bogdan's existing admin session.
No agent publishes an active workflow or dispatches it under this contract.

## Required handoff stages

1. **Preparation:** Engineer publishes immutable inert workflow/helper sources,
   intended workflow destination, trigger/permissions, action/tool identities,
   TEST/APP separation, endpoint inventory, failure handling, artifact packaging
   and offline-consumption procedures. Cite this exact contract commit/digests.
   Unknown runtime-derived lock/browser values remain explicitly unknown.
2. **Pre-execution review:** Assurance examines those exact source bytes against
   TSP-01 through TSP-05 below. Operator supplies actual runner and endpoint/egress
   verification before any execution. A runner label alone is insufficient.
   Static completeness can be reported separately; an unresolved permission or
   runtime-selection fact leaves execution readiness UNAVAILABLE. Do not use an
   unapproved download attempt to establish permission. CEO combines the exact
   producer and review packets for the existing administrator route.
3. **Supply:** Operator records actual publication commit, workflow/run/attempt/
   job/artifact identities, target inventory, complete locks/hashes and logs,
   allowed retrieval method, and a verified persistent copy before CI expiry.
   Runtime-derived values must now be concrete. A mutable download URL alone is
   not artifact identity. Original artifacts and failed-job evidence are retained.
4. **Independent consumption:** Assurance verifies returned TEST bytes and
   performs TSP-06 through TSP-11 within the existing authorized worker. It does
   not borrow the producer's interpreter, environment, cache or verdict as
   independent evidence. Report incompatibility without changing the target.
5. **Later suite completion:** Once supply is verified, Assurance runs its
   outstanding TC producer checks and publishes a ready candidate. Existing
   Engineer-owned TC.R/TC.V examinations and native non-author source review
   remain separate gates. Supply checks do not qualify an Assurance-authored
   harness or accept its test artifacts.

## Review and verification matrix

Every row records the exact contract/suite/workflow and, when available,
artifact identities, actor/task/run/session (UNKNOWN if unverified), command or
manual inspection, expected result, actual result, exit status, evidence path
and digest. Use PASS only for a demonstrated row. FAIL means an observed
contradiction; UNAVAILABLE means a required input/capability is absent;
UNKNOWN means evidence does not establish what occurred; NOT_RUN states that
the check was not executed. These labels are evidence, not native task statuses.

| ID | Check | Required result/evidence |
|---|---|---|
| TSP-01 | Source identity and authority | Retrieve exact workflow/helper commit and paths. Verify bytes against producer digests, allowed branch and immutable contract references. No source decision unless the current native participant is authorized. |
| TSP-02 | Workflow scope | Dependency-only trigger; explicit inputs; default read-only token; permitted pinned GitHub/repository-local actions and tools; no secret addition, deployment, broad cleanup, proxy changes or automatic cross-system dispatch. Failures propagate; missing outputs cannot become success. |
| TSP-03 | Target separation | Exact TEST CPython 3.12.3/Linux x86-64/glibc 2.39, pytest 8.4.2/Playwright 1.56.0. Distinct TEST and APP locks, staging directories, manifests, archives and artifact identities. Compatible tags measured for TEST; no reliance on APP CPython 3.13. |
| TSP-04 | Runner and endpoint readiness | Exact runner/OS/image and interpreter selection/provenance; complete action/tool/runtime/index/wheel/browser/artifact endpoint and redirect inventory; permitted-egress evidence tied to that environment. Absent facts block execution readiness. |
| TSP-05 | Reproducibility and failure handling | Complete hash-locked binary wheel closure, package-derived browser selection, full runtime-library inventory, immutable provenance and persistent-copy plan. Partial resolution, browser download/launch failure, missing archive or failed checksum must fail the relevant job and remain visible. |
| TSP-06 | Returned artifact identity | Match workflow publication/source/helper identities and run/attempt/job/artifact IDs to the reviewed packet. Recompute downloaded and persistent-copy archive/manifest digests. Distinguish service-reported artifact digest from independently hashed archive and extracted payload. Preserve failed/mismatching bytes as evidence; do not install them. |
| TSP-07 | Inventory and safe extraction | Verify each relative path, length, digest and executable mode; inventory exactly covers the payload. Extract only to a fresh pilot/task-owned directory; reject absolute/traversal paths or links escaping that directory. Match lock entries, wheel metadata/tags, provenance and browser descriptor/archive/tree identities. |
| TSP-08 | Offline installation | Fresh isolated environment under the exact authorized TEST interpreter, no system-site packages or reused installed dependencies. Record bootstrap/installer versions and provenance. Install only supplied hashed wheels using the command below; record compatible tags, dependency consistency and final installed inventory. No index, source build, automatic pip upgrade or browser download. |
| TSP-09 | Browser/runtime closure | Verify the complete supplied package-selected cache and library inventory, with no missing library. Launch the suite's default headless Chromium through Playwright 1.56.0, without system-browser or executable-path substitution. Record the actual executable/hash, browser.version(), return status and a local synthetic-page result. A launcher path alone does not pass. |
| TSP-10 | Isolation and offline evidence | Establish and document the already-authorized isolation method before consumption. Remote egress is unavailable for install/smoke while permitted local synthetic fixture communication remains possible. Logs and configuration corroborate this; --no-index alone does not prove all network is blocked. If available confinement cannot establish the claim, record UNAVAILABLE and return the exact missing capability to CEO; do not change host policy or credentials. |
| TSP-11 | Evidence completeness and retention | Save raw commands, stdout/stderr, exit status, target inventory and every digest in protected evidence. Console summaries stay within 4 KiB aggregate UTF-8. Confirm persistent-copy bytes before CI expiry. Missing logs/receipts are UNKNOWN; no blind redispatch or attempt allowance inferred from interruption. |

## Offline consumption procedure

This procedure is specified, not executed by publishing the contract. Run it
only after the reviewed supply and all applicable authorization/preconditions
are present. Work in new task-owned directories outside the source tree.

Record the interpreter's actual patch version, implementation, architecture,
libc, OS, compatible tags and installed bootstrap tooling. The environment must
match TEST, irrespective of the producer runner's label. Create a fresh virtual
environment without system-site packages. If its bootstrap tooling requires
an additional distribution, include that tool's exact versions and wheel hashes
in a separate bootstrap lock/inventory first. Never repair the worker by a host
package/snap installation or by substituting a newer Python/browser.

After archive and per-file verification, use the fresh environment's pinned
installer with an absolute wheelhouse and lock path:

```text
<fresh-venv>/bin/python -m pip --isolated --disable-pip-version-check install \
  --no-index --no-cache-dir --require-hashes --only-binary=:all: \
  --find-links <verified-TEST-wheelhouse> -r <verified-TEST-requirements.lock>
<fresh-venv>/bin/python -m pip --isolated --disable-pip-version-check check
```

Before running these commands, ensure the lock contains only the exact
distribution/version/hash requirements; a direct URL or VCS entry could make
`--no-index` insufficient. Capture complete installation and dependency-check
logs with actual exit status. Record the complete installed distribution list,
including separately identified venv bootstrap packages. Differences from the
declared lock/bootstrap inventory require explanation and verification, not
automatic acceptance.

Point Playwright's browser-cache selection at the verified extracted cache
using its supported `PLAYWRIGHT_BROWSERS_PATH` setting. Do not run an install or
download command during offline consumption. Run a bounded synthetic local-page
smoke with the same default `chromium.launch(headless=True)` used by TC-D1.
Record Playwright version, descriptor digest, resolved executable and hash,
actual browser version, launch/close result, and any missing shared library.
No real user data, app container or human-review service is needed for this
dependency smoke. Preserve the authorized browser security settings; a launch
failure is a result to report, not authority to relax the environment.

## Outstanding producer checks and independent gates

After supply verification, outstanding TC producer checks use a fresh evidence
directory for each run and the exact subsequently published suite candidate.
The existing commands, interpreted from TC-D1's tests directory, are:

```text
python run.py --kind fixture --profile all --evidence <new-producer-evidence-dir>
```

Actual pytest collection/full execution and browser checks remain outstanding.
Do not replay the completed 587 HTTP probes or 45 offline discriminator vectors
merely to restate their result. Do not run QA/application tests without the
separate exact application/runtime/adapter packet. Keep whitespace API-05's
required 422/no-write outcome unchanged; no skip, xfail or weakened assertion.

The existing `qualification/run.py` good/bad harness qualification belongs to
Engineer in the separately assigned TC.V task. The TEST artifact smoke and
Assurance's producer checks neither substitute for that independent execution
nor accept the test code Assurance authored. Final readiness requires actual
reviewed candidate publication, separate examination reports and native review.

## Return packet and recovery

For each review/consumption revision, save an identity header, TSP row results,
defects and limitations, exact next responsible actor/action, native stage/
participant/return identities and the outstanding gates on LOGA-23. Return
Engineer workflow or bundle defects to the original Engineer via LOGA-24; keep
the substantive report on LOGA-23 and send its exact references to LOGA-20.
Any expectation change still requires TS review. Do not modify Engineer's
workflow or application to make the check pass.

Before a consequential action, save its exact request as prepared, then record
dispatch-started, response-confirmed and evidence-saved only when established.
These are evidence labels, not an exactly-once guarantee. Reconcile durable
receipts and current native state before retry. A stopped run, missing receipt
or revised plan does not authorize another dispatch.

Save and read back the continuation before the final native blocked/ownership
transition. Keep the missing-supply blocker and the original native review
policy. Do not restore completed BASE/TS wait edges, duplicate the existing
artifact question, or use in_review as an input wait.
