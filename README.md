# Delivery framework templates

Product-independent templates for native Paperclip delivery assignments. This package is a prepared candidate, not an accepted framework or verified capability result. Publication, independent evidence and native acceptance are separate steps.

Use the same seven outcomes for an authorized increment: product definition, user experience, architecture, delivery planning, implementation, independent release acceptance and operations. For an existing product, preserve accepted baselines and assess relevant inherited evidence before creating gap/change work. Do not infer a rewrite. Goals express outcomes; native blockers express prerequisites.

## Assignments and ownership

P produces and corrects; R performs substantive review; TS designs scenarios; TC authors formal test code; V independently executes or manually verifies the exact candidate. The initial team is a Delivery Lead, Product Engineer and Independent Assurance. The human owner decides business acceptance. R and V performed by the same Assurance agent in separate sessions are independent of production, but are not two independent reviewing minds.

Stage assignments in backlog with their intended existing owners. Backlog assignment is preparation, not permission to examine. Before release to todo, supply authorized scope, acceptance criteria, reachable artifacts and exact evidence revisions; examination inputs include a remotely retrievable full candidate SHA and paths. Use native statuses and source-task review/approval stages. Reports belong to their own evidence tasks. An adverse completed examination is done with a FAIL verdict; a missing input is a blocker. Never equate done with correctness.

For Software projects using agent checkouts, deliberately configure the native project default `adapter_default`. Each incoming run verifies its actual agent repository and expected branch. Do not depend on a forgotten task override; an alternative workspace mode requires its own working repository/configuration.

## Candidate flow

1. Publish relevant requirements/contracts. TS can start before application implementation; TC can proceed alongside it using accepted scenarios and published contracts.
2. The producer commits and pushes each review-ready candidate to its authorized branch before handoff. Save and read back full SHA, exact paths, relevant document revisions, remote retrieval evidence and limitations. No local-only checkpoint is review-ready.
3. Release separate R and V against immutable inputs. V additionally requires accepted scenarios/suite and required environment; manual static work explicitly records why those software identities are not applicable.
4. After publication, P remains open and waits on actual R/V blockers. R/V never wait for P to be done. Distinguish production prerequisites from acceptance-only dependencies: if the coordinator cannot execute correction work while acceptance is blocked, use the authorized distinct production assignment, without removing acceptance edges or creating duplicate coordination/examination tasks. After both reports finish, save/read back the unchanged candidate, findings and continuation packet, then submit into the configured native review as the final required action of that run.
5. The incoming participant verifies live stage, currentParticipant, original returnAssignee and immutable candidate, and records that verification in its own continuing context. Only the active participant decides, with rationale in the native decision operation. Save/read back findings and continuation first; the transition is the final required action, with no required outgoing-run comment or receipt afterward. Changes requested returns the original producer natively. The producer publishes a new correction and obtains fresh affected evidence before resubmission.

Publication does not authorize main merge, deployment, release or product development. Human and operational approvals retain their own gates. Changed inputs invalidate affected evidence, even when native resubmission resumes a previously failed stage.

Match waits to native unresolved dependencies, pending interactions/approvals or a concrete blocker action with a permitted owner. Do not recreate blocked cycles against completed dependencies. The CEO coordinates recovery on the existing coordinator, inspects native recovery notices and records a supported next action or the exact remaining human decision. Before repeating an interrupted operation, reconcile durable request/result evidence and live state; UNKNOWN is not permission to redispatch. See [continuation and recovery](framework/continuation.md) and [native policy usage](framework/native-policies/README.md).

## Evidence provenance

The evidence schema requires `authorReference` separately from `authorRole`. Public copies use a privacy-safe opaque author reference; private control-plane evidence resolves it to the actual author. Do not publish internal identity records or private links to satisfy this contract.

`documentRevisions` contains nonblank references to applicable immutable document/configuration revisions. Private references may use opaque aliases with a resolvable private mapping. If no such revision applies, use an empty array and a nonblank `documentRevisionsNotApplicableReason`; omit that reason when revisions apply. Missing required evidence is not N/A. Reviewers verify identity mappings, immutable revision retrieval and any N/A justification: structural conformance alone proves none of these.

## Phase boundary

Phase B uses static synthetic fixtures, manual inspection and native records. Actions remains disabled. No formal automated suite, application, container build, persistent hosting or deployment is part of this package. TS/TC templates are reusable guidance for separately authorized work, not an instruction to execute Phase C.

Keep internal URLs, company inventory, actual configuration, credentials and private evidence in the control plane. Public artifacts contain generic templates and synthetic examples only. No custom budget, duration or run-count limits are introduced.
