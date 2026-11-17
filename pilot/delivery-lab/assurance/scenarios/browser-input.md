# Browser parameter applicability — TS-2

Correction for TSR-02 on TS-1. This specifies test inputs; it contains no executable harness or observed browser result. Accepted BASE-2 API trim/scalar-count/preservation rules stay unchanged. The baseline's single-line native text field is retained. The [WHATWG text-input definition](https://html.spec.whatwg.org/multipage/input.html#text-(type=text)-state-and-search-state-(type=search)), checked 2026-11-17, requires CR/LF removal from this control's value. It does not authorize other normalization or changes to the API contract.

## Three separately identified checks

1. **Literal API** (`fixture key + /api`): send the exact `request_name` using JSON, regardless of browser representability. Keep the existing API status/error/stored-name/tuple oracle. Every trim scalar and the original C0 sentinel remain direct required API checks. No browser constraint can skip them.
2. **Browser entry** (`fixture key + /browser-entry`): use the per-case `browser_input` record, containing literal-entry applicability, exact expected control value, scalar count, allowed request-name values, trimmed/stored name, status if sent, record delta and method. No expected value comes from the running app. Confirm control type and record pre-submit `value` as escaped code points as well as visible content; equality is scalar-exact. UI-02/03 consumes this oracle.
3. **API-created browser display** (`fixture key + /browser-display`): for every accepted name with a C0/C1 control scalar, create the original literal via API, then show it in UI-10 and reload. Compare API tuples and actual text-node content to exact stored name; separately assess safe wrapping/rendering. CR/LF can be present in list text even though the create field cannot hold them. Other accepted names retain normal UI-10/visual coverage; this control subset is explicit in the fixture record.

For a source string S, the specified single-line control value C is S with U+000D and U+000A removed. Every other scalar is retained; this is native control sanitization, not the application's trim operation. Let T be C trimmed only with BASE-2's explicit 25-scalar set. Valid T yields 201 with that exact stored name and one new tuple; invalid T yields local rejection or exact E-LENGTH/422 with unchanged records. If the UI transmits a request, its only field is a string name equal to C or T (client-side trim is allowed by BASE-2); both permitted wire values are enumerated per fixture. No other rewriting/normalization/truncation is allowed. Server response remains exact public contract. Local rejection must still retain C and expose the required guidance; it never substitutes for direct API rejection evidence.

## Required entry method and causality

- Ordinary strings: actual typing or paste into the native control, including 1/80/81 ASCII, astral and combining boundaries. Record injected and observed values before submit. Type/paste limitations must be distinguished from an app mutation; do not silently fall back and claim an unperformed natural-entry test passed.
- Strings containing C0/C1 control scalars (U+0000–001F or U+007F–009F): use the future accepted TC method that assigns S through the standard native input value setter, reads C before events, dispatches the normal input event, then reads the control again before an explicit user-like submit. This is **controlled browser-state setup**, not evidence of typing/pasting that control character. Do not press Tab to enter U+0009 or Enter to enter LF. Natural printable keyboard/paste evidence remains separate and required.
- For CR/LF values the setter must yield the fixed C in the fixture, never literal S. A literal-only LF/CR source becomes empty, so its browser result cannot prove application trimming of LF/CR. The literal API case supplies that evidence.
- Capture type/entry method, source S, pre-event C, post-event/pre-submit value, request count/body, response and record snapshot. If tooling or the environment cannot establish the specified input, stop that parameter's dependent app assertions and report setup UNAVAILABLE with evidence. If the mismatch is caused by app-specified maxlength, a sanitizer, or an event handler, report the application violation (including UI-03 truncation); do not hide a known app defect as unavailable setup. If a verified C is then changed by app handling contrary to the allowed contract, report the observed application violation; do not relabel it as setup failure or revise the oracle. Missing method attribution or checkpoints fails HAR-03 qualification.
- Do not change the input type, replace the control, bypass native value sanitization, alter app code or submit a different fixture to obtain PASS. A future different UI model requires explicit baseline resolution. No browser/OS/clipboard behavior has been observed in TS.

## Concrete parameter examples

Escapes below designate literal scalar values, not backslash text. The exhaustive per-parameter map is `fixtures.json`.

| Fixture | Literal API value/oracle | Predetermined browser control C and oracle | Distinction |
|---|---|---|---|
| `interior` | `A\t\u00a0\nB`, 5 scalars; 201 preserves all 5 | `A\t\u00a0B`, 4 scalars; 201 preserves those 4 | Also display the original 5-scalar API-created record in UI-10 |
| `interior-cr` | `A\rB`, 3 scalars; 201 preserves CR | `AB`, 2 scalars; 201 stores AB | Separate API-created CR display |
| `interior-crlf` | `A\r\nB`, 4 scalars; 201 preserves both | `AB`, 2 scalars; 201 stores AB | No claim that form transmitted CRLF |
| `trim-000A-only`, `trim-000D-only` | Exact LF or CR; E-LENGTH/422, no write | Empty C; local rejection or E-LENGTH/422, no write | Browser checks empty rejection, API checks trim scalar |
| `c0-sentinel` | ` \t\r\n `; E-LENGTH/422, no write; C0 must FAIL | ` \t `; local rejection or E-LENGTH/422 | API sentinel remains unchanged and mandatory |
| `ascii-padded-80` | Full trim set around 80 A; 201 stores 80 A | Same padding minus CR/LF; 201 stores 80 A | Identical result does not make input identities identical |
| `preserve-0000`, `preserve-001C` | Exact non-trim control around A; 201 preserves it | Same exact C via controlled setup; 201 preserves it | API/display remain required even if browser setup is unavailable |
| `astral-80`, `combining-80` | Exact 80 scalars; 201 | Natural typing/paste, exact same C; 201 | Still catches UTF-16/grapheme-count errors |

Every raw byte fixture is explicitly direct-API-only; malformed encoding/JSON and lone surrogate payloads cannot be represented as an ordinary native form submission. Raw wire errors retain API coverage. The browser receives server validation responses through UI-12's approved interception method, labelled UI handling evidence, not server correctness. TC must map `/api`, `/browser-entry` and required `/browser-display` separately in its suite/traceability and report unavailable methods honestly.
