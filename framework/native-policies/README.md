# Native policy usage

The adjacent JSON is a template, not a submitted configuration. Replace its symbolic participant with the actual authorized non-author agent UUID. Read back the saved policy. This repository does not implement a workflow engine.

Configure source-task stages through the supported issue PATCH. During production, use separate completed R/V reports as real blockers. After they finish, the producer submits the unchanged candidate to in_review. Inspect executionState.currentParticipant, currentStageType and returnAssignee. Only that current participant may decide: status done approves; status in_progress with a reason requests changes. Capture the native decision ID/outcome and returned assignee. Do not manually reassign to simulate a return.

For framework/application artifacts, Assurance is the non-author participant. For Assurance-authored TS use the Delivery Lead; for TC use the Product Engineer. A required human business approval is a separate user participant with an actual authorized user ID. Do not add a stage that makes an author approve their own output.

Coordination tasks initially waiting for human/operator input have a saved interaction and no deliverable stage. When the readiness evidence arrives, resume production, attach/read back the approved stage, obtain separate R/V evidence and only then submit the deliverable. Setting in_review to wait for input must not prematurely start deliverable acceptance.

A new candidate requires fresh affected evidence even if native resubmission resumes the failed stage. Preserve unresolved blockers when replacing blockedByIssueIds. Do not create source-done dependencies for its R/V tasks. Cancellations are not successful blocker resolution.
