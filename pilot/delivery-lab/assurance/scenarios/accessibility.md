# Accessibility scenarios — TS-1

Target: all applicable WCAG 2.2 A/AA requirements for the one application page and complete create/correct/recover journey, every UI state, both required viewports plus zoom/reflow boundaries. Source is accepted BASE-2 `accessibility.md` (file revision BASE-1). Reference checked 2026-11-17: [W3C dated WCAG 2.2 recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/). The following are product-specific examination procedures, not a conformance claim. The table accounts for 55 A/AA IDs; removed 4.1.1 and AAA are outside this target.

Every AX-SC row uses `AX-SC-<criterion>` as its stable parameter ID. Applies = execute listed checks; provisional absence = inspect all page/state content and confirm the stated premise. If premise is false, reclassify and perform the applicable criterion examination before reporting coverage. Absence is never a pre-granted PASS. Automation and manual observations have separate results; missing AT access remains UNAVAILABLE.

## Procedures and negative/boundary checks

- **AX-01 (A/M):** For loading, ready, empty, validation, pending, success, definite failure, confirmed-create/refresh-failed and both uncertainty states, run a versioned scanner with raw results; inspect DOM and accessibility tree. Validate heading/main/list/form relationships, field label/help/error and control role/name/state. Use HAR-06 pages with missing label, detached error and meaningless status to confirm detection; scanner results require investigation, not blind suppression.
- **AX-02 (M):** Starting with keyboard only, Tab/Shift-Tab through page, submit with Enter, activate refresh/retry with keyboard, correct invalid input, traverse during delayed GET/POST. Record focus sequence and visible focus screenshots. Expected logical order, no traps, no submit/navigation just from focus/type/blur; invalid submission focuses field, async success does not steal focus. Repeat at both required viewports and 200%/400% zoom. Moving away from pending control remains possible.
- **AX-03 (M):** With a real screen reader and recorded browser/OS/AT version, navigate landmarks/headings/form/list, read label/help, enter valid/invalid input, submit and recover from 503/500/drop and failed refresh. Record actual spoken transcript/observations, including once-per-transition status announcements, errors and disabled state. No transcript invented from DOM. Retain keyboard/clipboard/forwarding limitations of remote desktop. Tree inspection alone cannot satisfy this procedure.
- **AX-04 (M):** Measure computed foreground/background of ordinary text, hints, button, validation, success and status in all states: normal text >=4.5:1, qualifying large text >=3:1; required control boundaries/focus >=3:1 against adjacent colors. Record sizes/weights/colors, measurements and exceptions. Ensure state still understood without color. Inspect available high-contrast rendering and focused controls; reference token colors alone are insufficient.
- **AX-05 (A/M):** 200% text resize; 400% zoom from 1280px viewport and direct 320 CSS px; both orientations; overrides line-height 1.5, paragraph spacing 2em, letter spacing .12em, word spacing .16em. Test long/astral/combining names and error/recovery text. Expect no loss/clipping/overlap or two-direction page scroll; focus remains visible/unobscured and all actions reachable. Record actual viewport/zoom and limitations.
- **AX-06 (M):** Inspect every actionable target's CSS bounds/spacing: at least 24×24 CSS px or recorded applicable exception; also compare reference's >=44px control height. Press Create, move pointer away, release; expect no create. Normal release within target creates once. Compare accessible to visible label, including Create another item. Check single-pointer use without motion/drag/multipoint gesture requirement; voice-control spot check if available, explicitly label availability.
- **AX-07 (A/M):** Inspect authored copy, page title/lang, persistent help and state actions. Delay while editing and while fault pending; text/input must not disappear on application timer. No automatic navigation/submission, flashing/auto-scrolling content or audio. Inspect complete rendered page and available route/content inventory for provisional absent features in table. An added feature triggers applicability review, not silent exclusion.
- **AX-08 (M/H):** End-to-end create, correction, definite/uncertain failure recovery with retained input, meaningful next action and consistent labels. Combine actual screen-reader/keyboard evidence with human observations from HUM-01/02. Record application vs external route/auth/session limitations separately. Human approval does not replace missing technical checks; a scanner pass does not supply a human verdict.

All procedures include positive working paths, negative error/fault states and boundaries named above. Intentional bad fixtures validate checking methods only; actual candidate findings cite exact SC/scenario/location, expected/actual, raw evidence, severity and original producer. No app repair on an examination task.

## Criterion-to-procedure map

| SC | Level | Scope premise and observable outcome | Procedure |
|---|---|---|---|
| 1.1.1 | A | Inspect added art/icons; meaningful content has equivalent text/name and decoration is omitted from AT output | AX-01/03 |
| 1.2.1 | A | Provisional absence: inspect all states for prerecorded audio-only/video-only media; reassess if present | AX-07 |
| 1.2.2 | A | Provisional absence: no prerecorded synchronized-media player or content | AX-07 |
| 1.2.3 | A | Provisional absence: no video requiring alternative/descriptive presentation | AX-07 |
| 1.2.4 | AA | Provisional absence: no live synchronized stream in the app | AX-07 |
| 1.2.5 | AA | Provisional absence: no prerecorded video content requiring description | AX-07 |
| 1.3.1 | A | Tree exposes main, heading hierarchy, form label/help/error and list/item structure in every state | AX-01/03 |
| 1.3.2 | A | DOM/AT reading order agrees with meaningful scope/title/form/status/list order, including inserted errors | AX-01/03 |
| 1.3.3 | A | Each instruction identifies field/action without dependence on shape, position or color | AX-07/08 |
| 1.3.4 | AA | Rotate through portrait/landscape; no orientation lock or lost action/content | AX-05 |
| 1.3.5 | AA | Provisional absence: synthetic item-name input is not personal-user data; inventory any added fields | AX-01/07 |
| 1.4.1 | A | Disregard color: words still distinguish required/error/success and next action | AX-04/07 |
| 1.4.2 | A | Provisional absence: observe load and transitions; no automatically playing sound | AX-07 |
| 1.4.3 | AA | Actual text/background measurements meet required ratios with size/weight recorded, including hints/errors | AX-04 |
| 1.4.4 | AA | At 200% resize all labels/names/errors/actions remain available without clipped content | AX-05 |
| 1.4.5 | AA | Inspect text content: live readable text, not embedded reference screenshot/text rendered as image | AX-01/07 |
| 1.4.10 | AA | 320 CSS px and 400% zoom preserve one-column content and controls without two-direction scrolling | AX-05 |
| 1.4.11 | AA | Required input boundaries and focus/state indicators distinguishable from adjacent colors | AX-04 |
| 1.4.12 | AA | Spacing overrides preserve full names/help/errors/actions and operability | AX-05 |
| 1.4.13 | AA | Provisional absence: inspect hover/focus for extra content; any addition needs dismiss/hover/persist checks | AX-02/07 |
| 2.1.1 | A | Keyboard completes create, correct, refresh, inspect uncertain list and deliberately create another | AX-02/08 |
| 2.1.2 | A | Forward/reverse traversal enters/exits every control, including slow network states, without trap | AX-02 |
| 2.1.4 | A | Provisional absence: no custom character-key shortcut; examine behavior separately from native Enter submit | AX-02/07 |
| 2.2.1 | A | No app time limit removes input/action; delayed user can still finish. External desktop timeout recorded separately | AX-07/08 |
| 2.2.2 | A | Observe slow loading/results: no moving/blinking/auto-updating distraction requiring unprovided controls | AX-07 |
| 2.3.1 | A | Observe all transitions/faults; no flashing content introduced | AX-07 |
| 2.4.1 | A | Provisional absence of repeated navigation; main landmark still verified. Added repeated block requires bypass route | AX-01/02/07 |
| 2.4.2 | A | Browser document title describes Delivery Lab synthetic item page | AX-01/07 |
| 2.4.3 | A | Logical tab sequence and error focus; results do not cause unexpected focus jumps | AX-02/03 |
| 2.4.4 | A | Inspect all actual links if any; accessible text/context explains their destination | AX-01/07 |
| 2.4.5 | AA | Provisional absence: single app page, no additional page set requiring multiple navigation methods | AX-07 |
| 2.4.6 | AA | Headings and field/Create/Refresh/Create another item labels describe actual purpose | AX-01/03/07 |
| 2.4.7 | AA | Every keyboard focus target is visibly indicated in all states/layouts | AX-02/04 |
| 2.4.11 | AA | Author content never fully obscures focused control; record zoom/mobile/onscreen-keyboard observations | AX-02/05 |
| 2.5.1 | A | Provisional absence of multipoint/path gesture requirement; complete with single pointer | AX-06 |
| 2.5.2 | A | Pointer-down then move-away/release cancels activation; release on target activates once | AX-06 |
| 2.5.3 | A | Accessible names contain visible control wording in normal, pending and recovery states | AX-01/06 |
| 2.5.4 | A | Provisional absence: no motion-dependent action; no new motion handlers in implementation inventory | AX-06/07 |
| 2.5.7 | AA | Provisional absence: no dragging operation required by list or form | AX-06 |
| 2.5.8 | AA | All targets meet 24px minimum or documented criterion exception; check spacing/bounds and reference height | AX-06 |
| 3.1.1 | A | English document language exposed correctly; actual AT reading checked | AX-01/03 |
| 3.1.2 | AA | Authored passages use proper language metadata; record proper-name/unknown-language exceptions for synthetic names | AX-03/07 |
| 3.2.1 | A | Focus alone never creates a record or navigates away | AX-02 |
| 3.2.2 | A | Editing/pasting/blur does not submit or unexpectedly change context; explicit action controls create | AX-02/07 |
| 3.2.3 | AA | Provisional absence: no multi-page navigation; reassess if added routes/pages appear | AX-07 |
| 3.2.4 | AA | Repeated form/refresh controls retain consistent function and accessible meaning across states | AX-01/03/08 |
| 3.2.6 | A | Provisional absence: no repeated multi-page help mechanism; inventory additions | AX-07 |
| 3.3.1 | A | Invalid name yields textual cause and field identification, associated error and spoken feedback | AX-01/03/08 |
| 3.3.2 | A | Persistent label and 1–80/trim help available before entry, while typing and after failure; no placeholder-only label | AX-01/03/07 |
| 3.3.3 | AA | Validation explains correction; definite/uncertain failures explain safe next action | AX-03/08 |
| 3.3.4 | AA | Provisional absence: synthetic create-only scope, no consequential legal/financial/change/delete/test submission; reassess if scope differs | AX-07 |
| 3.3.7 | A | Original useful text survives rejected/uncertain POST; no forced retyping for retry, clear only after confirmed 201 | AX-03/08 |
| 3.3.8 | AA | Provisional absence in app: no authentication; external remote desktop/access restrictions separately recorded | AX-07/08 |
| 4.1.2 | A | Controls expose accurate role/name/value, invalid/disabled state and changes through native semantics | AX-01/03 |
| 4.1.3 | AA | Real AT hears loading/result/error/uncertainty updates, without repeated keystroke announcements or unnecessary focus movement | AX-03/08 |

## Record and limitations

Each row records applicability, scenario parameters/state, method A/M/H, expected/actual, PASS/FAIL/UNAVAILABLE or confirmed absence, evidence location, scanner ruleset/browser/AT/version, source/image/config and observer. Capture raw scans with triage reasons plus actual manual steps/observations. Record unavailable screen-reader/OS combinations and remote-desktop limitations. Full-page and complete-process scope includes failures, not only initial page. No broad WCAG conformance claim from this design, screenshots, a scanner, or a single passing browser/AT pair. Human final accessibility/usability observations remain HUM-01/02.
