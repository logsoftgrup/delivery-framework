# Delivery Lab scenarios — TS-1

Independent scenario candidate for [TEST.TS](/LOGA/issues/LOGA-22). Author/original native return: Independent Assurance `ce8e0a2f-a532-45cb-abeb-a3937e9be71e`. Separate examination: [TS.R](/LOGA/issues/LOGA-27), CEO `79ebc7d5-2399-4e63-aaff-a29207a852c1`; subsequent native source review is also CEO. Author checks below are not acceptance of this artifact.

## Authority and identity

Derived before application implementation, without inspecting application code, from accepted BASE-2 commit `3f0246514d8c8d4fee34aa5181d2f435303d3e6b` in `https://github.com/logsoftgrup/delivery-framework.git`, exact `pilot/delivery-lab/docs/` paths listed in `manifest.json`. Native baseline human approval: `4ae65f45-e6b8-4080-81b3-bdf2e4cd6353`. Input document `31f118cf-ec46-4e74-aac9-705e68adffb6`, revision `0f58973b-dd68-452e-b88d-c673c8a35fe7`; source plan revision `a3a6ba57-da85-4319-8561-70edc33243c2`. BASE.R report revision `0d7671a8-3a6e-4f0a-8082-c7a08fbfe6d2`; BASE.V `7924c43c-eb77-4702-80f9-d9309072dbc3`. These are static evidence only.

Framework F2 `5c594e3087d68a8862072998478864f6ee18a253`: `framework/continuation.md`, `framework/native-policies/README.md`, `framework/native-policies/non-author-review.template.json`, `framework/templates/TS.md`, `framework/templates/R.md`. Incorporated by exact reference; neither baseline nor F2 is merged or edited. The Assurance branch has separate history. TS-1's full publication commit is recorded externally on the task so this manifest does not contain a self-referential commit.

## Reading and result rules

- [Coverage](coverage.md) maps all ten acceptance criteria to stable scenario IDs. [API](api.md) specifies requests, response oracles and record effects. [Fixtures](fixtures.json) provides synthetic values and literal fixture states. It is data/specification, not a runnable suite.
- [Browser and human procedures](browser-manual.md), [accessibility](accessibility.md), [operations and lifecycle](operations-lifecycle.md), and [harness qualification](harness.md) complete the design. Execution and fault-injection code belong to later TEST.TC; actual execution belongs to distinct assigned V tasks.
- Modes: **A** planned automation in TC; **M** manual Assurance examination; **O** Engineer operation with independent Assurance observation; **H** human-only judgment. Mixed modes require each named kind of evidence. No runtime case has been executed here; all actual results are **NOT RUN**.
- PASS requires every assertion and evidence identity. FAIL means observed violation; UNAVAILABLE means an essential precondition/tool/observation is missing; UNKNOWN means an operation/outcome cannot be established. None is converted to PASS. N/A requires a documented, examined applicability rationale, especially for accessibility.
- Each execution record binds scenario ID and TS commit/hash, accepted suite commit/lock/tool identities, application full commit, OCI manifest/config digest and archive checksum, environment/config hash, fixture before/after hash, actor/task/run/session/UTC timestamps and raw artifacts. Record actual requests/responses and limitations; synthetic data only. Producer evidence stays labelled as producer evidence.
- C0 deliberately accepts whitespace-only names. **API-05 must FAIL C0** using the same required 422/no-write oracle as C1. It is not xfail, skipped, optional or a passing harness demonstration. C1 needs fresh affected evidence plus full required regression, technical and human gates.

## Open expectations and runtime prerequisites

**OBS-01 remains OPEN.** SEC-01–SEC-03 retain required rejection/no-write and origin isolation, but exact Host/Origin rejection status, body and cross-check precedence are not frozen. Original Engineer input is pending through coordinator interaction `5fecfd8f-80db-40be-86a5-7c24033d3672`. Do not infer these from framework defaults or an observed app. An answer proposing baseline changes needs the existing producer/review/affected-examination path. Publish and review clear scenarios now; final scenario acceptance and dependent formal expectations must reconcile this gap. Any amendment creates TS-2 with impact analysis; TS-1 and its report remain history.

**OBS-02 remains a qualification rule.** O2 selects a recorded exact C1 recovery target with an independently passed qualifying subset while O2 itself is still outstanding; see OPS-07. Same-artifact restoration does not claim compatibility with another release. C0 is never a rollback target or human review candidate.

Missing future runtime inputs are prerequisites, not findings against a nonexistent app: exact locks/base and app digests, suite/CI identity, routes, reset and fault-injection methods, operator manifests, browser/AT access, known-good target and human observation. CI rights/capacity remain UNKNOWN. No new service, environment, platform capability test, public endpoint, agent, skill, connection, merge or deployment is authorized by this design.

## Fixture and assertion convention

Before each isolated case, use an accepted TC fixture method confined to named/labeled QA storage; confirm its snapshot and exclusive synthetic writer control. Never reset review. Let **S0** be the complete ordered `(id,name,created_at)` snapshot and **S1** the post-action snapshot. Compare full tuples and IDs, not counts alone. A rejected operation requires `S1 = S0`; a success requires exactly one new ID, the unchanged old tuples, and the returned item present once. Repeated GET must be write-free. An uncertain POST may have committed zero or one record for one forwarded request; separately controlled committed/not-committed variants determine the expected database outcome. Do not infer it from matching names. If the fixture, interception or exclusivity cannot be proven, report UNAVAILABLE/UNKNOWN and preserve evidence before cleanup.

Publication includes only this directory. `manifest.json` hashes all other files and exact baseline inputs; its own hash and the full candidate SHA are in the task publication packet. Later executable suites must trace each parameter variant and manual obligation, not just one nominal test per scenario family.
