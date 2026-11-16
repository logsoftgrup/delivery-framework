# Capability evidence report

- Criterion ID / task / authorReference / authorRole:
- Candidate repository, branch, full SHA and exact paths:
- documentRevisions: applicable immutable document/configuration revision references (private records stay private):
- documentRevisionsNotApplicableReason: include only when documentRevisions is empty, with an explicit justification that none apply:
- Expected result:
- Observed result and evidence:
- Outcome: PASS | FAIL | UNAVAILABLE:
- Native policy/participant/assignee before and after, decision ID (when relevant):
- Original producer / returnAssignee, actual stage and incoming participant verification reference:
- Run/session identity before and after (when authorized and relevant):
- Separate execution assignment / test target; route preflight and stable reviewer/concurrency evidence (when relevant):
- Exact non-secret request/response, timestamps and before/after statusVersion/state references:
- Interrupted-operation evidence labels: prepared / dispatch-started / response-confirmed / evidence-saved; UNKNOWN and missing evidence:
- Observation time and limitations:
- Scenario/suite/image identity: not applicable for manual static fixtures:
- Saved report revision, read-back evidence and continuation packet; next permitted owner/action and native wait mechanism:

This is a blank template, not a report of a completed test. Sanitize all public report copies. Full private evidence belongs in the control plane.

Use a distinct nonblank authorReference, such as a synthetic opaque alias, rather than a role label. The private evidence must map the alias to the actual author. Each revision reference must be nonblank and resolve to an immutable revision, using a private mapping when necessary. Missing or inaccessible required revisions remain an evidence gap, not a reason to claim N/A. Schema conformance alone cannot establish identity, retrievability or evidence sufficiency.

Save and read back the report, exact references, findings, limitations and continuation before any run-ending completion/handoff/decision. Include decision rationale in that same native operation; it is the final required action of the run. The incoming participant verifies actual stage/currentParticipant, candidate and original returnAssignee, and records resulting native decision evidence in its own continuing context. No outgoing post-transition receipt is required.

Completed examination may carry FAIL; it does not accept the source. Preserve previous revisions and require fresh affected evidence for a changed candidate. For a wrong-actor criterion, PASS requires participant-specific rejection plus unchanged state; unrelated errors/concurrent changes are inconclusive. Missing evidence stays UNKNOWN (use UNAVAILABLE for the criterion outcome), never permission to repeat. Evidence labels do not create statuses or exactly-once guarantees. Generic process corrections cannot replace missing live capability proof.

This report outline may reference private supplemental records for the lifecycle details above. It does not add fields to the strict JSON evidence schema; keep additional request/response or continuation material in referenced evidence records rather than inserting undeclared properties.
