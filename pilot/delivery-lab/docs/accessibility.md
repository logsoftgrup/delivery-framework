# Accessibility examination map

Scope: the single Delivery Lab page, list/create journey and every loading, empty, invalid, success, service-error and ambiguous-result state; desktop/mobile, zoom, keyboard and assistive technology. Target: all applicable A and AA criteria of [WCAG 2.2, dated recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/). The table enumerates its 55 A/AA criteria by ID. Removed 4.1.1 is not a WCAG 2.2 criterion; valid, robust markup remains an implementation requirement. AAA is outside this target.

This is our proposed product-specific mapping, not a conformance result. “Applies” means independent evidence is required. “Absent” is a provisional applicability rationale requiring Assurance to inspect the actual implementation and revisit it when features change. No row is already PASS. All rows are owned by Assurance; Engineer supplies design/producer evidence and fixes only on the source assignment. Final human review retains accessibility/usability observations.

| ID | Level | Applicability and Delivery Lab obligation | Independent examination evidence |
|---|---|---|---|
| 1.1.1 | A | Applies: controls and status are text; any added meaningful icon gets an equivalent accessible name. | Inspect accessibility tree and alternatives; decorative art ignored. |
| 1.2.1 | A | Absent: no recorded audio/video content. | Inspect page and states for media. |
| 1.2.2 | A | Absent: no recorded synchronized media. | Confirm no embedded player. |
| 1.2.3 | A | Absent: no recorded video. | Confirm no video instructions. |
| 1.2.4 | AA | Absent: no live media. | Confirm no streaming content. |
| 1.2.5 | AA | Absent: no recorded video. | Reassess if a demo video is embedded. |
| 1.3.1 | A | Applies: main landmark, h1/h2 order, ul/li items, form/label, associated help and error. | Inspect DOM/tree and navigate headings, fields and list in screen reader. |
| 1.3.2 | A | Applies: DOM follows title, instructions, field, action, status, list. | Compare reading sequence to visual order, including errors. |
| 1.3.3 | A | Applies: instructions name the field/action, never rely on position or colour alone. | Read all state copy without layout cues. |
| 1.3.4 | AA | Applies: no orientation lock; form/list remain usable after rotation. | Portrait and landscape browser checks. |
| 1.3.5 | AA | Absent: item name is synthetic inventory text, not information about the user. | Inspect input purpose; reassess if personal fields appear. |
| 1.4.1 | A | Applies: error/success/required information has words, not colour alone. | Inspect each state with colour cues disregarded. |
| 1.4.2 | A | Absent: no audio. | Confirm no sound on load, error or create. |
| 1.4.3 | AA | Applies: proposed text colours need measured contrast against each actual background. | Measure computed text pairs, including errors, hints, button and state messages (4.5:1 normal, 3:1 large). |
| 1.4.4 | AA | Applies: resizing text to 200% preserves form actions and complete names. | Browser text/zoom checks; no clipping or lost functionality. |
| 1.4.5 | AA | Applies: live UI uses real text, not a screenshot of the SVG. | Inspect rendered text and styles. The static SVG is only a design artifact. |
| 1.4.10 | AA | Applies: one column reflows at 320 CSS px; long names cannot force page-wide horizontal scrolling. | 400% zoom at 1280px-wide viewport and direct 320px width; all states. |
| 1.4.11 | AA | Applies: input boundary and focus indicator remain distinguishable on adjacent colours. | Measure rendered controls/focus contrasts of at least 3:1; inspect high-contrast mode. |
| 1.4.12 | AA | Applies: user text-spacing overrides cannot hide help, errors, names or controls. | Set line height 1.5×, paragraph spacing 2×, letter spacing .12em and word spacing .16em; inspect all states. |
| 1.4.13 | AA | Absent: no hover/focus popovers or tooltips. | Inspect interactions; if added, review their dismissal, hover and persistence behaviour. |
| 2.1.1 | A | Applies: create, refresh and deliberate retry work with keyboard alone. | Tab/Shift-Tab/Enter/Space through complete journey and failures. |
| 2.1.2 | A | Applies: no modal or trapped focus; pending operations do not trap traversal. | Move into and out of every control in every state. |
| 2.1.4 | A | Absent: no custom character shortcuts. | Inspect key handlers; native form Enter is not a single-character shortcut. |
| 2.2.1 | A | Applies: no application session/time limit or timed disappearance of information. | Observe delayed input and recovery; separate remote-desktop timeout limitations below. |
| 2.2.2 | A | Applies: static loading words; no automatic scrolling, cycling banners or animated busy indicators. | Observe page during slow GET/POST and after results. |
| 2.3.1 | A | Applies: no flashes in any state. | Observe transitions and reduced-motion settings. |
| 2.4.1 | A | Absent in proposed one-page layout: no repeated navigation blocks; main landmark still required. | Inspect actual chrome; add a skip route if repeated content appears. |
| 2.4.2 | A | Applies: browser title identifies Delivery Lab and synthetic item list. | Inspect document title. |
| 2.4.3 | A | Applies: logical focus sequence; invalid submission focuses name; async success leaves user in control. | Record focus path including failure recovery and refresh. |
| 2.4.4 | A | Applies if links appear: link text states its destination/purpose. | Audit every link in actual UI; none required in baseline main form. |
| 2.4.5 | AA | Absent: only one application page, not a set needing alternative navigation. | Confirm no hidden settings/help page. |
| 2.4.6 | AA | Applies: headings and “Item name”, “Create”, “Refresh list” describe their functions. | Inspect labels and screen-reader control list. |
| 2.4.7 | AA | Applies: every keyboard target has visible focus. | Capture focused field and each action. |
| 2.4.11 | AA | Applies: no fixed overlays; focused control remains visible in small/zoomed layouts. | Traverse at 200%/400% and after validation with onscreen keyboard where available. |
| 2.5.1 | A | Absent: no path or multipoint gesture. | Complete journey with single pointer taps. |
| 2.5.2 | A | Applies: buttons activate on release; dragging away cancels activation. | Pointer press/move-away/release on Create/refresh. |
| 2.5.3 | A | Applies: accessible names contain visible wording, particularly “Item name” and “Create”. | Compare computed names; voice-control spot check if available. |
| 2.5.4 | A | Absent: no motion input. | Confirm no device-motion handlers. |
| 2.5.7 | AA | Absent: no drag action. | Confirm list cannot require dragging to interact. |
| 2.5.8 | AA | Applies: proposed field/buttons are at least 44px high; inspect each actionable target/spacing. | Measure all rendered targets against 24×24 CSS px minimum or documented criterion exception. |
| 3.1.1 | A | Applies: page language is English. | Inspect html lang and screen-reader pronunciation. |
| 3.1.2 | AA | Applies: authored foreign-language passages need language metadata; arbitrary user names have unknown language. | Inspect authored strings; document proper-name/unknown-language exceptions for synthetic input. |
| 3.2.1 | A | Applies: focusing a field/action never submits or navigates. | Keyboard traversal without activation. |
| 3.2.2 | A | Applies: editing name never submits or unexpectedly moves focus. | Type, paste and blur; explicit Create triggers request. |
| 3.2.3 | AA | Absent: no navigation across multiple pages. | Inspect app routes and consistent controls if new pages appear. |
| 3.2.4 | AA | Applies: Create/Refresh list keep their accessible meanings across states. | Compare repeated controls/names throughout journey. |
| 3.2.6 | A | Absent: no recurring contact/help mechanism across pages. Inline field instructions remain consistent. | Reassess if support/help is added. |
| 3.3.1 | A | Applies: invalid name identifies field and cause in text with associated error. | Submit invalid input; inspect aria-invalid/description and spoken feedback. |
| 3.3.2 | A | Applies: persistent label and explicit 1–80-character/trim guidance precede submission. | Inspect blank, focused and entered field; placeholder cannot replace label. |
| 3.3.3 | AA | Applies: error says how to fix name; storage/network copy explains next action. | Correct invalid name and recover from both failure types. |
| 3.3.4 | AA | Absent: synthetic create-only data; no legal/financial operation, test answers or modification/deletion of stored user-controlled records. | Verify exclusions; reassess if edit/delete or consequential data is introduced. |
| 3.3.7 | A | Applies: name remains available after validation or failed/uncertain POST; no re-entry demanded for retry. | Compare field value before/after all failures. Clear only after confirmed 201. |
| 3.3.8 | AA | Absent in app: no authentication flow. External remote-desktop authentication is separately constrained below. | Record external route limitation; do not imply its conformance. |
| 4.1.2 | A | Applies: native controls expose name/role/value and disabled/error state correctly. | DOM/tree inspection plus screen-reader interaction. |
| 4.1.3 | AA | Applies: a persistent polite status region announces loading/result; errors announced without needless focus jumps. | Listen for each transition once, including uncertainty and successful create with failed list refresh. |

## Required examination record and limitations

Assurance records the exact source/image/configuration, page URL, browser and OS versions, viewport/zoom, scanner/version/ruleset and assistive technology/version. Automated scans cover all reachable states, with raw results and investigated false positives. Manual evidence covers the keyboard sequence, focus, reading order and complete create/correct/recover journey with a real screen reader. Identify every unavailable combination; missing screen-reader access means that check is UNAVAILABLE and the release decision must retain that limitation. Do not substitute a screenshot or accessibility tree for spoken interaction evidence.

The static SVG cannot establish semantics, focus, announcements, reflow, touch or runtime contrast. Neither this matrix nor a single browser/AT pair certifies all accessibility. Remote-desktop accessibility, its authentication mechanism, clipboard/keyboard forwarding and session timeouts may constrain human testing; record them separately. They are outside the application conformance scope but cannot be ignored when reporting O1/U1 accessibility of the end-to-end route. If the intended human cannot complete that route, record failure/limitation and obtain the next permitted action before final acceptance.
