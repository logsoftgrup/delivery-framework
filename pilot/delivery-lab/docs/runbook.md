# Delivery Lab operator runbook — baseline requirements

This is a static operational design. Commands/actions below are future procedures for separately authorized application work, not instructions to deploy BASE-1. Engineer is the operator; Assurance independently verifies; CEO coordinates administrator/session-reset requests; Bogdan retains repository administration. No merge, production deployment, access expansion or host-wide action is authorized here.

## Observed facts and open gates

Read-only checks performed by Engineer run `f3ef7ae2-ed2b-40ca-906e-afe9eed8c05b` on 2026-11-17:

| Check | Observed result | Limit |
|---|---|---|
| `docker context show` | `default` | Existing authorized context only. |
| Docker selected server metadata | Name `buc01w01ai01`, `linux`, `x86_64`, root `/var/lib/docker`, version `28.0.4` | No socket or host configuration changed. Architecture supports proposed linux/amd64 selection. |
| Filtered Docker published-port listing for 18080/18081 | No matching mapping | Does not exclude a non-Docker host listener or reserve the port. |
| `ss -ltn '( sport = :18080 or sport = :18081 )'` in agent execution environment | No listeners | Host network namespace equivalence is unverified. Host port availability remains UNKNOWN. |
| Docker volumes filtered to `com.logsoftgrup.pilot=delivery-lab` | None | No pilot storage provisioned; named-volume route is proposed, capacity/permissions/durability unproven. |

Reuse the human's completed Docker access checks from interaction `b564497b-933c-44af-aa66-dc76a8dce684`; do not repeat capability tests. The selected engine is accessible to Engineer and independently to Assurance; CEO intentionally has no socket. No image pull/build, container start or resource mutation occurred for this baseline.

Open runtime gates: exact build inputs and image digest in [architecture](architecture.md); CI enablement/capacity/publication rights UNKNOWN (CEO observed Actions settings/runners 403 and zero workflows); host port freedom; volume permissions/free space/backup destination; actual agent-to-service route; actual authenticated human review URL; persistence after sessions end; external reachability exclusion; known-good rollback target; native technical and human approvals. None is silently waived by static acceptance.

## Allowed resources and authority

All future resources must carry `com.logsoftgrup.pilot=delivery-lab`, `com.logsoftgrup.environment=qa|review`, plus source revision where supported. Name and label must both match before mutation; a same-name resource with unexpected ownership is a stop condition. No wildcard deletion. Record actual resource IDs in the deployment manifest.

| Resource | QA allowlist | Review allowlist / constraints |
|---|---|---|
| Compose project | `delivery-lab-qa` | `delivery-lab-review` |
| App container (explicit name) | `delivery-lab-qa-app` | `delivery-lab-review-app` |
| Private network | `delivery-lab-qa-net` | `delivery-lab-review-net`; never shared with QA or unrelated services |
| Active data volume | `delivery-lab-qa-data` | `delivery-lab-review-data`; review is never fixture-reset |
| Restore verification volume | `delivery-lab-qa-restore` | `delivery-lab-review-restore`; isolated, no overwrite of original data |
| Image name | `delivery-lab:qa-<full-source-sha>` plus immutable manifest/config identity | Same verified C1 artifact by digest; `delivery-lab:review-<full-source-sha>` is convenience only |
| Published port | `127.0.0.1:18081:8000/tcp` | `127.0.0.1:18080:8000/tcp` |
| Operator artifacts | `pilot/delivery-lab/artifacts/qa/<run-id>/` in Engineer's configured checkout | `pilot/delivery-lab/artifacts/review/<run-id>/` in that checkout; checksum/log/backup files only, no credentials. Runtime assignment must authorize these paths; BASE.P cannot write them. |

Named volumes reside on the selected Docker engine, not the agent checkout. The default Docker root observation is not permission to manipulate `/var/lib/docker` directly. Storage setup/backup uses only an approved pilot container/volume route and non-root data owner. Confirm enough space for the database, image/archive and at least two backups before use; record measured values and expected sizes rather than claiming unlimited capacity. If operator artifacts are not durable across worker sessions, obtain a specific permitted durable destination before deployment. Do not mount the socket/host credentials into app or helper containers.

No unrelated containers, networks, images, volumes, ports or artifact paths are in scope. No prune, system restart, daemon configuration, firewall changes or new public ingress. Existing remote desktop is the human access boundary; no new domain, gateway or SSH alias.

## Deployment preflight and access route

1. Verify native task/participant, candidate commit, accepted baseline/scenario/suite identities and authorization for the intended QA/review operation. Obtain immutable image manifest/config digest and archive checksum. Verify exact resource names/labels and configuration before issuing mutations. C0 runs only in QA; review requires independently passing C1 and separate promotion authority.
2. Check host-local listeners at both proposed ports immediately before launch. The operator may use its authorized host context if available; otherwise save the exact host-only read-only action for CEO to relay through Bogdan/OpenClaw. Do not equate a check in the worker namespace with a host check. If occupied, stop; do not kill the occupant or silently choose another port. Obtain a recorded revised loopback port if needed.
3. Render/checksum the exact Compose config, verify only loopback publishing, no host network or privileged mounts, separate networks/volumes, non-root writable data directory, restart/log/resource policy, and no secrets. Check pilot storage capacity and backup destination. Record baseline resources so unrelated resources remain untouched.
4. Launch only the named pilot instance under the deployment assignment. Inspect actual container/volume/network IDs, image config and published binding. Probe `/healthz`, `/readyz`, `/api/version`, GET and UI from the permitted route. A version payload alone is insufficient; bind it to inspected image/config identity.
5. Human route: existing authenticated remote desktop on `buc01w01ai01` → browser → `http://127.0.0.1:18080/` **proposed until verified**. QA proposed host browser URL is `http://127.0.0.1:18081/`. Record the actual working URL only after deployment checks. No public unauthenticated URL is supplied.
6. Agent route: direct agent loopback is unproven. Assurance must independently record the successful route from its own authorized execution context. A permitted option is a separately declared synthetic QA test runner on the QA network using the service DNS name; it must be authorized/identified in the TC/runtime input packet before creation. This baseline authorizes no extra runner/container. Host loopback tests can use the authenticated host browser context when available. Missing route is a concrete runtime blocker, not permission to add network access.
7. Prove nonexposure of both UI and API: inspect published IPv4/IPv6 bindings and routing configuration; use a specifically authorized external unauthenticated check if available. No wide network scanning. If external negative evidence is unavailable, report UNAVAILABLE and retain O1 gate. [Docker's port guidance](https://docs.docker.com/engine/network/port-publishing/) explains loopback binding and version-dependent limitations; a config declaration alone is not end-to-end access proof.
8. Record healthy operation and persistent IDs, restart the pilot app container in its existing volume, then compare IDs/health/version. End all agent sessions through the authorized task/session process; a subsequent actor/run verifies service and data remain. Do not reset globally or delete hidden session files. Human checks the route after sessions end; record actual timestamps and identities, not a promise of persistence.

## Deployment evidence manifest

Engineer publishes a non-secret record and reads it back before transition. Required fields: task/actor/run/session; environment; source repo/full commit; accepted BASE manifest Git blob/SHA-256 and document revisions; TS scenario revision; TC suite SHA; build workflow commit/run URL; exact lock hash and tool versions; base index/platform digests; app manifest/config digest, platform and archive filename/SHA-256; image labels and `/api/version`; rendered Compose path/hash and configuration values; actual Docker context/server; project/container/network/volume IDs and labels; actual bindings/verified URLs and observer routes; fixture snapshot/checksum; health/readiness results; timestamped record-ID snapshots; storage/backup locations; known-good target; independent report revisions; native approvals and unresolved limitations.

Never publish tokens, host credentials, real data, private keys or arbitrary environment dumps. Keep producer logs distinguishable from independent results. A local archive checksum is not a registry/OCI manifest digest. If images are exchanged by OCI archive, preserve the OCI manifest bytes/digest and transfer/archive SHA-256, then independently verify both on import. No invented remote registry location.

## Backup, restore and known-good rollback

1. Before promotion or any recovery operation, identify the exact source image/config and volume. Quiesce the pilot's new writes during the demonstrated backup/recovery window; record last acknowledged item IDs. Preserve the original database/volume and archive. No live raw copy of just the `.sqlite3` file while WAL may contain committed data.
2. Use the [SQLite backup API](https://www.sqlite.org/backup.html) via the pinned Python sqlite3 library to create a consistent standalone snapshot in the allowlisted operator artifact location. Record UTC time, source volume/schema/image, `PRAGMA integrity_check` result, item count/full synthetic IDs and backup SHA-256. Inspect for synthetic-only content. The backup mechanism is implemented in app/operator work, not here.
3. Restore into the separate allowlisted restore volume. Verify checksum before restore, run integrity/schema checks and compare every acknowledged ID/name/time. Run the exact image/config against the restored data in isolated QA for the recovery demonstration, without attaching the review live volume to QA. Assurance verifies independently and records route plus manifest/config identities. Keep at least the pre-change and last verified backups until human acceptance; later cleanup needs scope/retention authority.
4. A known-good target is a prior immutable image/config with independently passing criteria on compatible schema plus a verified restore point. **C0 is intentionally defective and is never the known-good target.** Initial deployment has no known-good target by default. Establish a separately recorded recovery target from independently passing C1 before human promotion, then demonstrate restoration of that exact target and C1. If the intended acceptance exercise requires a distinct earlier version, CEO must authorize that candidate; do not call C0 acceptable or fabricate one.
5. Rollback triggers: failed health/readiness, version/digest mismatch, record loss or post-promotion technical regression. Operator stops new pilot writes, captures failure evidence and a fresh backup, verifies the known-good target's schema compatibility, switches only the pilot image/config (or isolated verified restored volume if necessary), and repeats health/version/record checks. Do not apply an old schema image to incompatible data. A schema migration without a verified reverse/restore path blocks promotion. Record any data-loss interval; no acknowledged-create loss is allowed in the demonstrated restart/recovery proof.
6. Restore the intended C1 image/config and current verified synthetic records after the rollback exercise; Assurance checks digest/config/IDs again. Human review route must serve C1, never a temporary defective or unverified recovery target. Record final service state before relinquishing the operator task.

No runtime execution in this baseline proves these steps. Review data is not reset. Fixture reset is isolated QA-only under TC's accepted method: confirm environment/project/volume label, save evidence if needed, initialize an explicit accepted fixture and record its snapshot/hash. There is no app reset/delete endpoint. Never let a test script target review by a default URL.

## CI publication packet

CI facts remain UNKNOWN; Docker access does not resolve them. Engineer prepares requirements on the source task, CEO coordinates, Bogdan uses the permitted repository-admin publication route. No `.github/` changes are authorized by BASE.P and no credential widening is requested.

Administrator packet for the later workflow includes:

- Repository `logsoftgrup/delivery-framework`, candidate `smoke/phase-b` and exact app/suite/base commits; no main merge or forced ref update. Workflow file path proposal `.github/workflows/delivery-lab.yml`; actual publication authority/route, Actions enabled state, runner capacity and artifact upload/download permission must be confirmed by Bogdan.
- Manual workflow_dispatch with exact published candidate SHA and exact accepted suite SHA as required inputs; branch/head changes must not silently alter the candidate. Validate commits and pin checkout/action refs. Permit a normal CI trigger only if the administrator approves its branch/path filters. No automatic deployment step.
- Clean linux/amd64 build with resolved Python image/hashed lock; record runner image/tools, base/app digests, source identity and SBOM/package inventory. Execute producer checks and accepted independent suite as separately labelled jobs/reports; producer execution does not become independent acceptance.
- Least privilege: contents read for checkout, only the artifact/package permission actually needed by the chosen authorized publication route. No access to Docker host/socket/credentials from untrusted pull-request code; no secrets in image layers or logs. Pin third-party actions to reviewed full commit SHAs and record them. Follow [GitHub's workflow hardening guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions).
- Publish OCI image archive/manifest, archive checksum, dependency lock/inventory, build/producer and independent reports, plus source-to-image manifest as downloadable artifacts. Proposed retention 30 days, extended or durably copied before expiry through a permitted route; exact retention/capacity/location are administrator selections. Record immutable workflow run URL/ID and artifact IDs. Assurance must independently download and verify the exact artifact; a successful upload alone is insufficient.
- No automatic promotion, merge or deploy. Human review promotion retains passing C1, completed independent reports, recovery evidence and the separately authorized operator action. Missing Actions capacity/publication rights require a recorded decision on a permitted alternative, not an unannounced local-build equivalence.

If host-only commands or a genuinely fresh-session reset require OpenClaw, save the exact non-secret request, target task/session key, scope, preconditions, expected result/evidence destination and rollback/abort condition on the Engineer task. CEO relays to Bogdan; no automatic cross-system dispatch. Record verified before/after state and operator identity. Missing response means UNKNOWN; reconcile before retry and never infer new authority from an interrupted run.
