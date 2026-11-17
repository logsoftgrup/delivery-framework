# Delivery Lab — proposed visual and interaction reference

Status: static proposal BASE-1, awaiting independent review and native human baseline approval. [Open the SVG reference](ui-reference.svg). It shows desktop 1440×900 and mobile 390×844 compositions at their stated dimensions. It is authored vector documentation, not an application screenshot or interactive prototype. Final approval concerns the actual running UI and screenshots at both viewports.

## Layout and appearance

One centered column, maximum content width 640px; 24px horizontal inset on desktop and 20px on mobile, shrinking fluidly to fit. No sidebar or fixed header. Ordered content: synthetic-data badge, h1 “Delivery Lab”, short scope sentence, h2 “Create an item”, labelled name field/help, primary Create button, persistent status region, h2 “Items”, count and semantic list. One form only. List names wrap anywhere when needed; list grows vertically without clipping. No virtualization, ellipsis or internal scroll trap. Human-facing UI contains no build/CI/configuration jargon.

Use system sans-serif; body 16px with 1.5 line height, h1 32px/1.2, h2 20px/1.4. Spacing scale 8/16/24/32px. Background `#f5f7fb`, white surfaces `#ffffff`, main text `#172033`, secondary text `#475569`, input borders `#64748b`; primary button `#1d4ed8` with white text. Error text `#991b1b` on `#fff1f2`; success `#166534` on `#f0fdf4`. A proposed 3px `#1d4ed8` focus outline with a 3px white separating gap surrounds interactive controls. These choices require actual computed contrast verification per [accessibility](accessibility.md); token choice alone is not PASS. Input and button are at least 44px tall; mobile Create fills the content width. All text may wrap and controls expand with text.

Label: “Item name”. Help: “Use 1–80 characters. Surrounding whitespace is removed.” Visible scope text: “Synthetic data only. Create sample items to try the delivery journey.” Seed names: Sample notebook, Sample cable, Sample adapter. Display only names in the visual list; stable IDs/timestamps remain available in API evidence. Count uses singular/plural correctly. Label/description association, native form controls and status semantics are implementation requirements.

## States and recovery

| State / trigger | Visible wording and behaviour | Focus / announcement |
|---|---|---|
| Initial GET pending | “Loading items…”; field available, Create disabled until initial list succeeds. No empty-state claim yet. | Persistent polite status region; do not move focus on load. |
| Initial GET failure | “Items could not be loaded. Refresh the list to try again.” plus “Refresh list”. Preserve entered name; Create disabled. | Announce error once; refresh is keyboard reachable. |
| Empty committed list | “No items yet. Create the first item.” and “0 items”. | Announce loading completion, not an error. QA can provide an initialized empty fixture. |
| Ready | Show list/count; editable field and Create. | Logical tab order; visible focus. |
| Local/server validation error | “Enter 1–80 characters after trimming surrounding whitespace.” or the appropriate API field guidance; preserve text, no insert. | Focus name on rejected form; set aria-invalid and associate error/help. Avoid repeated announcements on every keystroke. |
| POST pending | Button says “Creating…” and is disabled; no second submission. Keep value visible and freeze editing during pending request so it cannot be lost by a racing response. | Status says “Creating item…”; retain logical focus and do not trap traversal. |
| 201 received, refresh pending | “Item created. Updating the list…”; clear only the submitted value after success. | Polite announcement; no premature announcement before 201. |
| 201 and refreshed list | “Item created.”; exactly one additional ID for one deliberate request; show updated count/list. | Keep focus logically at form; status announces success once. |
| 201 but refresh failed | “Item was created, but the list could not be refreshed. Refresh the list to see it.” Create stays disabled until refresh succeeds. | “Refresh list” action; never repeat create. |
| Definite rejection, e.g. intercepted pre-forward 503 | “Item was not created. Try again.” Preserve value; enable deliberate retry with Create. | Announce error; field/action stay available. This certainty requires an explicit no-commit contract. |
| Network timeout/drop or unexpected 500 | “We could not confirm whether the item was created. Refreshing the list before you retry.” Preserve value; disable Create; issue GET only. | Announce uncertainty; never announce definite failure or retry POST automatically. |
| Uncertain result, reconciliation GET succeeds | “Check the list. A matching name may already exist. Create another item only if you intend to add one.” Display latest list; expose deliberate “Create another item” submit action for the same form. | Name matches do not prove which request committed. Keep input; user may clear/edit or deliberately submit. |
| Uncertain result, reconciliation GET fails | “We still cannot check the list. Refresh the list before creating another item.” Preserve value, keep Create disabled, offer GET refresh. | Announce once per deliberate refresh, no retry loop. |

Exactly one create form remains in every state. “Create another item” is a temporary label/action on that form, not a second form or automatic resend. Subsequent success follows the same 201/refresh path. “Refresh list” is type=button and never submits the form. Use textContent/text nodes for item names, never innerHTML. Native Enter submission observes the same pending guard. API validation is authoritative even when the UI prechecks. No use of HTML maxlength as the sole Unicode limit.

## Human and independent review

Assurance compares actual screenshots at 390×844 and 1440×900 to the approved reference and also tests 320px reflow, 200%/400% zoom, text spacing, long/combining/astral/markup-looking names, keyboard, screen reader and all state copy. Independent UI/API evidence shares the same candidate identity. Screenshots use synthetic names only and record viewport/device scale/browser version. The two reference views are illustrations of the same layout; they do not certify all responsive states.

Human performs create, correction and failure recovery without agent coaching and records wording, appearance and usability verdicts. Any assistance is recorded. No task-time threshold is invented. Static visual approval is distinct from final actual-UI approval; no implied runtime authorization comes from accepting this reference.
