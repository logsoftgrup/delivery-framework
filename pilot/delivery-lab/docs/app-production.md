# Delivery Lab application production — C0 preparation

This source snapshot is not a released C0 candidate. It implements the accepted
BASE-3 contract `a76f458655c9bd2a8ef95562651e0c9155f6a878` and TS-3 scenario inputs
`de46dadeb45c76280b0a99630303fb7666798789`, with the single explicitly authorized
API whitespace-only defect. The accepted baseline files and Assurance scenarios
are unchanged. No formal acceptance tests are authored here.

## Implementation and intended defect

`app/core.py` implements Host and present-Origin admission, the exact trim set,
Unicode scalar validation, first-failure error precedence and transactional
SQLite storage. `app/main.py` serves FastAPI routes behind admission before
routing/body parsing/storage. `app/schema.py` publishes the unchanged accepted
schema, including the 1–80 scalar requirement. `app/static/` contains the one-form
plain UI, text-only names, status/error regions, and explicit uncertain-create
reconciliation. There are no failure injection or fixture reset endpoints.

The marked `whitespace_only_c0` branch accepts a **nonempty** name composed entirely
of contract trim characters and stores the trimmed empty string. Empty input still
rejects. API-05 must therefore FAIL independently; the schema and UI still require
rejection. This is the only intentional contract failure. C1 correction is not
authorized until the unchanged released C0 has completed its separate examinations,
native Assurance has requested changes and returned to the original Engineer, and
the required task-scoped fresh-session continuation is verified.

## Build input blocker

The configured network returned Forbidden for Docker Hub manifest resolution and
HTTP tunnel 403 for PyPI metadata. There is no cached Python or Delivery Lab image
on the selected Docker engine. No network/proxy/access policy was changed and no
host-daemon route was used to circumvent those rejections. Docker client metadata
uses an isolated writable directory under `.git/app-p-evidence/`; the agent's
read-only configuration was not altered.

`app/requirements.in` is a resolution request, **not an installable lock**.
`container/Dockerfile.in` is deliberately non-buildable until its base is resolved
and a reviewed `requirements.lock` plus checksum-verified wheel bundle exist.
There is no fabricated base digest, image manifest/config digest, archive checksum,
build success, service route, or CI result. No service is deployed by this snapshot.

CEO is requested to coordinate a permitted artifact-supply route with the existing
administrator/operator. Supply a protected, retrievable bundle or native attachment
containing:

1. Official CPython 3.13 slim Bookworm linux/amd64 image: selected exact patch tag,
   retrieval time, source index and platform manifest bytes/digests, image config
   digest, transport/archive format and SHA-256, plus image archive. The immutable
   image and every blob must verify; a Docker image ID alone is insufficient.
2. Exact compatible FastAPI and minimal Uvicorn direct/transitive wheels resolved
   for that Python/platform; version list, archive SHA-256 values, complete hashed
   lock, resolver/installer identities, command and source provenance. Include the
   artifacts so the approved build can run with `--no-index --require-hashes`.
3. Toolchain identity/provenance sufficient to reproduce that resolution. If the
   existing approved network has a documented accessible mirror, provide that route
   for use within current confinement instead of granting broader agent access.

Verify the received bundle before generating the final Dockerfile/lock. Publish
the resolved inputs on the authorized branch and build from that exact published
commit. Generate `build_identity.json` in the image from SOURCE_COMMIT/BUILD_ID;
runtime environment cannot override it. Record Python/SQLite/installer/build tools,
non-root UID/GID, source/lock hashes and all resulting manifest/config/archive
identities in the external candidate packet. Do not place an image's source SHA
self-referentially inside the same source commit.

## Runtime and recovery continuation

Compose files are static configuration preparation. They use the accepted explicit
resource names/labels, non-root UID/GID 10001, read-only root, writable named data
volume, no socket/host credentials, internal private networks and host loopback
18081 (QA) / 18080 (review). Image/revision variables are required; set only from
the verified immutable packet. `pull_policy: never` prevents implicit retrieval.
Volume permission copy-up, health checks and route behavior require actual testing.
No additional internal Host alias is enabled. A health probe connects inside its
own app container and sends the admitted published Host; this is not proof of the
independent Assurance-to-service route.

Before deployment verify host port availability in the actual host namespace,
resource ownership labels and names, capacity and writable volume initialization.
Render and hash exact configuration, retain pre/post resource identities, deploy
C0 only to QA, and verify the real test route. Capture the synthetic seed snapshot
and its hash without resetting review data. Fixture/failure injection belongs to
accepted TC, not the application. Publish exact candidate source, complete package,
config, fixture and evidence destination before releasing APP.R. APP.V additionally
requires the accepted TC SHA/harness and actual route. Retain Assurance ownership;
CEO coordinates assignment/release scheduling. Separate reports may be FAIL/done;
they do not accept APP.P.

Follow accepted `runbook.md` for backup/restore and OBS-02 qualification. Use SQLite
online backup (not an isolated copy of a live WAL main file), checksum and integrity
verification, and separate restore volumes. A known-good target must meet accepted
OBS-02 before OPS-08; C0 is never a human review rollback target. Only independently
passing C1 may be deliberately promoted to review. Actual host loopback URL,
all-sessions-ended persistence, external exclusion, backup/restore, qualified
rollback and restoration remain unverified. Preserve native final Assurance then
human acceptance; no main merge or production release.

## CI administrator packet

Actions enablement and hosted-runner availability were supplied by the administrator;
actual workflow execution/artifact retrieval are still unverified. Prepare the full
workflow only against the published application and accepted TC input SHAs with
their reviewed invocation. It must use manual dispatch only, read-only contents
permissions, allowed GitHub-authored/local actions pinned by verified full SHA,
clean source retrieval, hashed offline dependency installation, build identity,
unchanged accepted suite execution (C0 API-05 remains a real FAIL), and artifact
publication even on test failure. Preserve real command exit status. Include
image manifest/config/archive digests, source/lock/config hashes and reports.
No dummy passing workflow, ignored failure, deployment trigger or `.github/` write
by Engineer. Supply the exact reviewed workflow/checksum/final path and input SHAs
on LOGA-20 for Daniela/OpenClaw via Bogdan's authorized administrator session.

## Verification limits

Producer checks may inspect standard-library contract/storage behavior, syntax,
and Compose rendering. They are not formal acceptance, a clean package build,
HTTP integration, browser/accessibility evidence or deployment verification.
Those checks and the immutable source publication receipt are saved on LOGA-24.
