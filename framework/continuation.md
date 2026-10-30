# Fresh-session continuation packet

Persist a concise packet on the source task before ending a session. A normal packet is 200–400 words; this is a writing guideline, not a run/token limit.

```text
Task / source task / current native stage and participant:
Outcome and remaining criterion IDs:
Repository, authorized branch, remotely retrievable full SHA, exact paths, PR and image digest:
Scenario revision, suite SHA and CI/execution run (or explicit static/manual N/A):
Completed work, report revisions and evidence references:
Decisions/reasons, known failures, pending interactions and real blockers:
Next concrete actions and original producer / returnAssignee:
Unpublished workspace changes and access/environment constraints:
```

A fresh session checks current task authority, reads this packet and exact referenced artifacts, verifies identities and resumes only the listed scope. The packet is evidence, not permission. It must not require the old transcript or private memory. Preserve uncommitted work; never call it a ready candidate.

Use only the supported scoped reset after an authorized operator verifies the exact non-null task key and the producer run has ended. Record before/after session/run identities. No global reset, hidden session-file deletion or database manipulation. If scope cannot be proven, report UNAVAILABLE and stop the dependent recovery check.
