# DEP-SUPPLY-2 — inert dependency-supply workflow candidate

This revision addresses DEP1-R-01 from independent report R1 at
`7301fe9c6203adcab016c442e5529f29fbf747ff`, path
`pilot/delivery-lab/assurance/supply/reviews/dep-supply-1-review.md`.
It preserves DEP-SUPPLY-1 `11850c330b676270e11c95107e3cef3ddf588caa`
and its report as immutable history. Corrected source requires fresh independent
review on LOGA-23; this correction does not establish execution readiness.

**Execution readiness: UNAVAILABLE.** This is Engineer-authored preparation for
independent review on LOGA-23 and administrator handoff on LOGA-20. It is not an
active workflow, supplied dependency bundle, pilot build, accepted test run or
source review submission. The operator's 23 November answer selects this route
for preparation and verification. It does not supply runner/egress/artifact proof.

Authority: LOGA-24 input revision `b38ebb1a-b75b-4ccd-b686-361d5b37aca9`; canonical
LOGA-20 direction `32ab8f98-5869-4abe-858c-2514942b8a9e`. Authenticated operator
answer `60503c13-ab72-44c1-a3d1-a0e2a5791e19`, 2026-11-23 15:51:54.990Z, text SHA-256
`2f89f8f958f13229012f8af633f3403b49a1418b01ea98fc514637efb5794546`.
The existing Engineer artifact question remains pending until real retrieval
references and bytes exist.

## Exact publication and execution boundary

The candidate workflow is `workflow.yml.in` in this directory. Intended final
path: `.github/workflows/delivery-lab-dependency-supply.yml`. Daniela/OpenClaw,
through Bogdan's existing repository-admin browser session, alone publishes the
independently reviewed bytes. Engineer does not write `.github/`, dispatch a job,
change credentials/network policy, or automatically send work to OpenClaw.

Only `workflow_dispatch` is present. A dispatch explicitly selects **one** APP or
TEST job, an immutable supplier commit, and a non-secret operator preflight
receipt. There is no push/PR/schedule trigger, deployment, formal test-suite run,
or automatic retry. The default token permission is `contents: read`; checkout
does not persist credentials. GitHub-authored actions are pinned to verified tags:

| Action | Full commit | Source tag |
|---|---|---|
| actions/checkout | `11bd71901bbe5b1630ceea73d27597364c9af683` | v4.2.2 |
| actions/upload-artifact | `ea165f8d65b6e75b540449e92b4886f43607fa02` | v4.6.2 |

The operator must verify these exact action runtimes remain supported on the
selected runner before execution. Existing repository selected-action policy
permits GitHub-authored/local actions; it is not proof that this candidate ran.
The workflow retrieves both supplier and actual published-workflow commits and
checks the published bytes against the reviewed inert file and receipt checksum.

## Runner and tooling prerequisites

Selected label: `ubuntu-24.04`, standard GitHub-hosted x64 Linux. The driver is
`/usr/bin/python3.12`, required to report **CPython 3.12.3**, with glibc **2.39**.
No setup-python download or host package/snap installation is performed. The
operator must establish the exact runner image version, interpreter binary and
provenance, available venv/ensurepip, Git/Docker, sudo/unshare/ip/ldd/dpkg-query,
capacity and the permissions for the narrowly scoped namespace operation below.
Runtime assertions compare Ubuntu release, Python, architecture, libc, ImageVersion
and Docker version to the receipt. A mismatch fails; no alternate interpreter,
runner or browser is silently substituted.

`supply.py` and `verify_bundle.py` are repository-owned stdlib helpers bound by the
candidate commit and file hashes. The resolver/installer is exactly **pip 26.2.2**,
with its public Git tag object recorded in `app-input.json`. Its wheel SHA-256 is
measured from the permitted PyPI metadata/download during supply, captured in a
separate toolchain lock/inventory, then used for offline installs. No transitive
version/hash is guessed. Complete resolution output and command failure status
are retained. Binary wheels only; no VCS/editable inputs or sdist build.

The source tag selections have been retrieved from public GitHub. Package
availability, compatibility, registry digests, wheel hashes and runtime tool
versions on CI remain unmeasured. A source tag is provenance for a proposed
selection, not a substitute for verifying the returned artifact bytes.

## Required endpoint and redirect inventory

Before **any dispatch**, the operator must attach evidence that the selected
runner may use every required endpoint and redirect. A successful speculative
download does not establish permission. `operator-preflight.example.json` is an
explicitly false/non-executable template. Replace its unknowns with real evidence
through the existing operator route; never just flip its boolean. The helper
validates exact host names (no wildcards) and evidenced HTTPS URL prefixes for its
own downloads, checks redirect destinations, strips credentials on cross-host
redirects, and records sanitized source/final URLs and redirect chains. Signed
redirect query values and the anonymous registry bearer token are not archived.

| Operation | Required source endpoints/routes | Exact unresolved facts |
|---|---|---|
| Repository checkout | `https://github.com/logsoftgrup/delivery-framework.git`; GitHub API/codeload endpoints used by the pinned checkout action | Actual action/bootstrap/checkout endpoint and redirect inventory on the selected runner, and permitted egress |
| GitHub action acquisition | GitHub's service endpoints serving the two exact pinned action commits | Actual request URLs/redirect hosts; runner services may be contacted before any step-level guard |
| APP registry authorization | `https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/python:pull` | Permission for anonymous token retrieval; no user credential is requested |
| APP tag/index resolution | `https://registry-1.docker.io/v2/library/python/manifests/3.13.18-slim-bookworm` | Index/platform manifests and their SHA-256 values |
| APP manifest/blob retrieval | `https://registry-1.docker.io/v2/library/python/manifests/sha256:<measured>` and `/blobs/sha256:<measured>` | Exact digest-derived URLs and CDN redirect hosts/paths; no wildcard CDN allowance is assumed |
| pip bootstrap metadata | `https://pypi.org/pypi/pip/26.2.2/json` | Wheel URL and expected hash from metadata |
| Package resolution | `https://pypi.org/simple/` plus normalized direct/transitive package paths | Complete resolver request/redirect inventory for the measured graph; APP and TEST graphs differ |
| Wheel bytes | `https://files.pythonhosted.org/packages/...` URLs supplied by the resolver/PyPI metadata | Exact filename/path/hash and any redirects for every wheel |
| Browser bytes | URLs generated by the verified Playwright 1.56.0 wheel's registry for the selected Linux platform | All selected Chromium/headless-shell/ffmpeg archive URLs and their redirect chains. Common CDN names are not an approved substitute for measured URLs |
| Artifact upload/retrieval | GitHub Actions result/artifact services, including the actual storage destination issued to that run | Exact results-receiver/storage hosts, redirects, permitted retrieval method and expiry |

The complete measured inventory is **not available yet**. This blocks execution
readiness even if static workflow review passes. The receipt can identify
evidenced path prefixes for a service and must retain its actual exact URL/redirect
inventory in the linked evidence. Any newly discovered host or path outside that
evidence stops the helper. pip, GitHub actions and Docker perform their own
network operations: the helper is not an egress firewall for them. Their full
upstream and redirect behavior must be verified externally by the operator before
dispatch. No proxy/environment-policy change is made to enforce or bypass access.
If existing authorization cannot establish that fact, CEO must obtain the narrow
endpoint/capability decision described by the operator answer; do not execute first.

The official [GitHub runner communication requirements](https://docs.github.com/en/actions/reference/runners/github-hosted-runners#communication-requirements-for-github-hosted-runners)
describe platform service categories; they do not prove this repository's route.
[Artifact action documentation](https://github.com/actions/upload-artifact/tree/ea165f8d65b6e75b540449e92b4886f43607fa02)
defines artifact IDs/digests and retention controls. Capture the actual identities.

## Separate APP bundle

`app-input.json` proposes official `python:3.13.18-slim-bookworm`, linux/amd64,
FastAPI **0.165.0**, minimal Uvicorn **0.54.0**, and pip **26.2.2**. The exact official
image tag was read at docker-library/official-images commit
`cf9d26d6c18941c210ad0c01f3dfe20e07a3aa54`. No base or package digest is fabricated.

The supplier saves the raw registry index, selects one linux/amd64 manifest,
verifies every original config/layer blob, and writes an OCI layout. It also
creates a Docker transport archive and verifies the loaded image's config digest.
The registry index digest, platform manifest digest, config digest, OCI blob hashes
and Docker archive checksum remain separate identities. Exact CPython 3.13.18 in
that base resolves the APP wheel graph. APP wheels never come from the TEST ABI.

A second container uses the already-loaded config with `--pull never --network
none` for a fresh venv, supplied hashed wheels, dependency consistency and imports.
No application source or accepted suite runs. This is supplier smoke evidence;
offline import/build compatibility on Engineer's actual engine remains a later
gate. Loading a Docker tar need not preserve the original RepoDigest: the OCI
layout and recorded registry manifests remain authoritative. Do not silently
replace a digest-pinned application build with a mutable tag.

## Separate TEST bundle and Assurance input

TEST-SUPPLY-1 is pinned in `test-input-interface.json` to commit
`a94938bfcb37745c93843816a66d990cc46d888e`, three exact paths/digests and publication
revision `ab060d2c-5ca0-4b10-9a3d-e005c72b9ccc`. This is a reference to Assurance's
contract, not a rewritten contract. TC-D1 remains
`47199f8ad78ad0b1c1ebae1487acfa79cb644937`; the exact requirements.in bytes are
checked and copied. No test-suite code is edited or executed here.

The TEST graph uses CPython 3.12.3/Linux x86-64/glibc 2.39, pytest **8.4.2** and
Playwright **1.56.0**. A temporary install from supplied wheels is used to read the
verified Playwright package's embedded browser descriptors and registry. It is
selection preparation, not isolated-consumer evidence. Package-owned registry
logic supplies Linux platform, versions, paths and URLs for chromium,
chromium-headless-shell and ffmpeg. No remembered Chromium revision or system
browser substitute is used. Only the first package-selected URL is requested;
there is no mirror retry. Unexpected redirects or failed checks stop the job.
Archives, browser descriptor, extracted tree hashes and executable modes are saved.
The installation marker denotes completed extraction only; no dependency-validation
marker is forged. Symlink-containing archives are rejected for review.

Proposed TEST offline isolation is a process-scoped Linux network namespace:
`sudo -n unshare --net`, enabling only its loopback interface. It changes no host
firewall, host interfaces or installed packages. The operator must explicitly
verify this existing runner capability and permission in the receipt before any
job. There is no fallback if unavailable. The child asserts only loopback exists,
records routes, creates a fresh venv, installs only supplied hash-locked wheels,
checks dependencies, and performs a local synthetic-page smoke with
`chromium.launch(headless=True)`. It records the actual descendant executable,
hash and browser.version(), requiring the package-selected headless shell.
Full ldd output for browser/driver ELF files, system package versions, library
paths/hashes and missing-library results are retained. No host packages are added.
This smoke is supplier environment verification, not formal acceptance-code
authoring or TC.V. Assurance must independently repeat its own contract checks in
its authorized consumer environment and establish its own isolation first.

## Artifacts, failures and retention

Successful jobs produce separate `app-bundle.tar.gz` (root `APP/`) or
`test-bundle.tar.gz` (root `TEST/`), archive checksum, payload manifest with
path/size/hash/mode, complete wheel/lock/toolchain inventories and provenance.
Browser/archive/library evidence is TEST-only; OCI/Docker/base evidence is APP-only.
No bundle is published by the success step if acquisition/smoke fails. Separate
diagnostic artifacts use an explicit `-diagnostics-` name and cannot satisfy supply.
Every `run()` invocation writes a sibling `<log-name>.result.json` before raising
on child failure. It records the stage's fixed log name, an allowlisted executable
name (otherwise `other`), argument count, raw Python subprocess return code,
separate nonnegative exit status or signal number, and the combined stdout/stderr
log's relative path, byte length and SHA-256. Raw argv, executable directories,
cwd and environment are omitted from the receipt. Known call sites pass no
credentials to child processes; the retained output remains protected evidence.

The receipt starts as `dispatch_started` with null result fields. `completed`
means that the child has returned, even for nonzero or signal failure; it is not
a success claim. A launch error records its type and errno without exception
text and leaves child result fields null. An interrupted wrapper may leave only
the initial receipt; its child outcome is UNKNOWN and must be reconciled before
retry. These evidence labels are not task statuses or retry authorization.

The wrapper still fails on a nonzero/signal child result; its exit 1 is distinct
from the saved child status, including a silent child exit 42. Receipts and their
`.log`, `.json` or `.txt` output references are retained by both diagnostic upload
paths. There is no `continue-on-error` or passing dummy job. Actual CI artifact
retention remains to be verified on the administrator-operated runner.

The archive's internal provenance records source/helper/workflow identities and
run/attempt/runner facts. Actual GitHub artifact ID/service digest, creation/expiry
and persistent-copy receipt are recorded **externally after upload**; they cannot
be inserted into the same already-uploaded archive without changing its identity.
The step summary records artifact ID/digest, and CEO's final operator packet must
join those values to the independently measured archive/manifest hashes. Internal
`retrieval.json` is a plan with `persistent_copy_verified: false` until that external
receipt exists. Supplier completion is not supply acceptance.

Requested CI retention is 14 days, subject to the actual repository limit. Before
expiry the operator must download through the existing authorized route, verify
GitHub's artifact identity and the enclosed tar checksum, store a protected
persistent copy, read it back/recompute its checksum, and record location/access,
retention, run/job/attempt/artifact IDs and verification time on LOGA-20. A CI URL
alone is insufficient. No purchase or new storage connection is requested.

## Independent offline consumption

Start with the trusted operator archive checksum, exact supplier commit and
artifact receipt. Verify in a fresh task-owned destination:

```text
python verify_bundle.py <bundle.tar.gz> --sha256 <trusted-archive-sha256> \
  --source <reviewed-supplier-commit> --kind app|test --destination <new-directory>
```

The stdlib verifier performs no network/install/launch. It checks archive hash,
bounded safe extraction, exact payload coverage/modes, source binding, lock grammar
and APP OCI graph. Preserve mismatches; do not install failed bytes. Then establish
already-authorized egress isolation and exact target ABI before fresh-venv installs:

```text
<fresh-python> -m pip --isolated --disable-pip-version-check install --no-index \
  --no-cache-dir --require-hashes --only-binary=:all: \
  --find-links <bundle>/wheelhouse -r <bundle>/toolchain.lock
<fresh-python> -m pip --isolated --disable-pip-version-check install --no-index \
  --no-cache-dir --require-hashes --only-binary=:all: \
  --find-links <bundle>/wheelhouse -r <bundle>/requirements.lock
<fresh-python> -m pip --isolated --disable-pip-version-check check
```

`--no-index` alone is not isolation. No source build, hidden direct URL, automatic
installer upgrade or browser download is allowed. Bind TEST's supplied browser
cache with PLAYWRIGHT_BROWSERS_PATH; Assurance owns TSP-06–TSP-11 consumer findings
and any later TC checks. Keep APP and TEST provenance and venvs separate.

Remaining before execution: independent review of these exact source bytes;
actual runner/action/interpreter/tool/isolation evidence; complete permitted
endpoint/redirect facts; administrator publication approval and receipt. Remaining
after supply: actual artifact identities, verified persistent copy and independent
offline consumer results. C0 packaging, separate APP.R/APP.V, B2 FAIL/native return,
fresh session/C1, recovery and human acceptance all retain their existing gates.
