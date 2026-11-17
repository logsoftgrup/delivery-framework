# TS-3 affected correction and provenance

Author Independent Assurance `ce8e0a2f-a532-45cb-abeb-a3937e9be71e`, LOGA-22, run `e953940b-a069-4776-b62d-7903f0068dbe`. Original native return remains Assurance; source stays in changes-requested correction until completed separate examination and native CEO review. This is author evidence, not acceptance or independent finding closure.

## Exact derivation

- Starting TS-2: `4fe13631a568df29f96a8685d5f674a968150d44`, manifest SHA-256 `e3d3c038fb713cab33481ad20dcc4c79406e3422cca7df3dbe56090a24f2f823`, publication revision `3fb2caa4-d8b0-4e1a-bbf6-0ffd1f4b1d5d`.
- TS-2 TS.R report `a7936f93-c32c-4b13-8ab1-3d067f185048`: overall FAIL for TSR-01, independently closed TSR-02/03. Reconciliation `ec1ec338-d835-429b-97a0-677ff7094e3e`; native changes-requested decision `a45bf6c8-c45e-41b0-9f13-a87373e0a16b` retains original producer.
- Accepted BASE-3: `a76f458655c9bd2a8ef95562651e0c9155f6a878`; CEO handoff document `a8e28743-8490-4a2f-beab-f246b487e562`, revision `53ffc545-66ae-4619-90a9-4167c988193b`. Exact `pilot/delivery-lab/docs/api.md` and `architecture.md` control denials, authority comparison, route scope, precedence and boundaries; all eight baseline files and hashes are listed in the scenario manifest and independently retrieved from that remote commit.
- BASE-3 final native decision `f34e7937-ab56-4b66-a509-a02975629681`; Assurance decision `745e7918-7cc9-454d-9786-d0b329b89fef`, review basis revision `fc4cb131-54db-4cdc-a1c0-415cfdcf61da`. Fresh BASE.R `055cd714-be50-48d5-9bc4-00664ffff60d` and BASE.V `b40699d2-8dea-47c5-b188-848e47cfbffa` are accepted static evidence as copied in that verified CEO packet. No new baseline decision is taken in TS.
- Original Engineer proposal revision `0daaaae0-2043-4be9-b5f4-8b07e4215bb6` and response revision `43ac0d10-5726-4389-9c31-eb1e405a3e4a` are historical provenance, not the acceptance substitute. The accepted published baseline now supplies the contract; do not recreate the old missing-input wait.

## Changed paths and meaning

| Path under `pilot/delivery-lab/assurance/scenarios/` | Change / reason |
|---|---|
| `api.md` | Replace SEC-01–03 unresolved stub with literal denial oracles and 40 parameter rows (12 Origin, 13 Host, 15 precedence/route). Bind all alternatives/instance-host combinations, byte boundary, zero-write assertions, conditional QA prerequisites, static/runtime/browser/manual applicability, transport/body-suppression limitations. Update normative input reference. Clarify API-15 OPTIONS note to agree with the accepted admission-before-405 amendment; existing ordinary PUT/404/405 outcomes and HEAD limits remain. |
| `coverage.md` | Add positive/negative/boundary security parameter links to T1/O1; mark accepted input supplied and TSR-01 correction pending independent examination. Preserve ten-criterion and reverse mappings. |
| `README.md` | Add BASE-3/current correction provenance and replace obsolete missing-input blocker; retain original BASE-2 derivation and TS-2 history. |
| `impact-ts-3.md` | This correction/provenance and limitations record. |
| `manifest.json` | New candidate, baseline input hashes, previous-candidate/report, current review state, affected scope and refreshed payload hashes. |

Unchanged payloads: `fixtures.json`, `browser-input.md`, `browser-manual.md`, `accessibility.md`, `operations-lifecycle.md`, `harness.md`, `impact-ts-2.md`. Their hashes must match TS-2 exactly. Existing API-01–14 and API-16–18, UNI and DATA rows remain byte-identical; API-15 changes only its now-superseded OPTIONS caveat. The literal API control-character cases and API-05 whitespace C0 required failure remain. No application, baseline, framework, workflow or executable-suite path changes.

## Evidence and handoff limits

The new candidate commit and manifest self-hash are recorded externally in the publication packet to avoid self-reference. Producer static checks verify scope, unchanged rows/payloads, unique parameter keys, manifest hashes and exact remote retrieval; they do not substitute for independent TS.R. No runtime results, accepted suite or image identity, actual service route/QA alias, fault injection or external access proof is claimed. Browser variants that cannot set headers use separately approved HTTP observations; transport refusal is separately reported rather than a fabricated application pass. Header admission does not prove authentication. Conditional internal QA variants require the concrete authorized runtime proof; no wildcard or placeholder is enabled by this document.

OBS-01 missing-input state is resolved by BASE-3 acceptance; TSR-01 remains an author correction awaiting fresh LOGA-27. TSR-02/03's prior independent closure is preserved. OBS-02 recovery qualification and suite/application/CI/runtime/human gates remain. Publish only on `assurance/phase-b`, release existing CEO-owned LOGA-27 after remote verification, then wait via the native unresolved dependency. On examination completion reconcile the exact new report and submit to unchanged native CEO source review; only its active non-author participant decides. No unchanged-candidate resubmission, self-acceptance or downstream release.
