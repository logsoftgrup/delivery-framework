# TS-3 criterion coverage

Unchanged expected outcomes derive from accepted BASE-2; SEC-01–03 and the admitted OPTIONS clarification derive from accepted BASE-3; modes and tuple assertions are defined in README. This is design coverage, not PASS evidence. Each listed range includes every defined member and its applicable parameter variants. Literal API cases and browser-entry/display variants are separately mapped in fixtures.json and browser-input.md; no unsupported literal browser entry is implied. Negative operational cases are safe fixture/config comparisons or abort-path observations, not authority to create an unsafe deployment.

| Criterion | Positive scenarios | Negative scenarios | Boundary / recovery scenarios | Modes and required evidence |
|---|---|---|---|---|
| B1 useful journey | API-01, UI-01, UI-11, HUM-01 | API-03–05, UI-02, UI-06 | API-02, UI-04–09, DATA-04 | A API tuples/network/browser; M reload; H understands journey/wording |
| B2 validation | API-02, UNI-01–06, UI-03 | API-03–11, API-13, UI-02, UI-12 | API-05 C0 FAIL, API-12, UNI-01–08 | A literal API plus per-fixture browser-entry/display map; missing/non-string/malformed are direct API cases; M error association |
| T1 contract/data | API-01, API-14–18, DATA-01–05, UI-10–11 | API-03–13, API-16–17, UI-12, SEC-01–03 | UNI-01–08, DATA-02–05, UI-02–03, UI-05–09 | A exact schema/errors/headers/order/tuples; O process/container restart; M text safety; exact SEC-01–03 admission oracles from BASE-3; TSR-01 awaits fresh review |
| T2 package | PKG-01–03, OPS-01–02 | PKG-02–03, HAR-08–10 | clean build, archive round-trip, config/digest disagreement | A/M pinned build/lock/manifest/config and inventory; O operator packet; CI unavailable remains open |
| V1 visual | VIS-01, UI-01, UI-11, HUM-01 | VIS-02, UI-02, UI-05–09, UI-12 | VIS-01–03 and UI-10 at 390×844 / 1440×900 / 320 CSS px | A captures; M layout/state comparison; H final appearance |
| A1 accessibility | AX-01–08 and all AX-SC rows | invalid/failed/uncertain states in AX-01–08; UI-11–12 | zoom, reflow, text spacing, keyboard/focus/AT and provisional absent features; HUM-02 | A scanner + DOM, M actual keyboard/screen-reader/measurements; H route observations; all 55 A/AA rows accounted |
| U1 usability | HUM-01–02, UI-01 | HUM-02, UI-02, UI-06–09, UI-12 | retained input, failed initial/reconciliation GET, deliberate second create | A input/request assertions; M facilitation record; H uncoached verdict; no timing threshold |
| O1 persistent access | OPS-01–05, HUM-01 | OPS-01–04, SEC-01–03, HAR-08–10 | actual host route; all sessions ended; restart; IPv4/IPv6 | O operator configuration/session operation; A/M independent identity/access; H later remote-desktop visit |
| O2 recovery | OPS-06–09 | OPS-06–09, HAR-11 | backup with WAL, restore tuples, known-good qualification without O2 cycle, final C1 | O Engineer recovery; A/M independent checksum/digest/schema/tuple checks; no review reset |
| L1 delivery proof | LIFE-01–05, HAR-01–12 | API-05/C0, LIFE-02, HAR-02–12 | fresh producer session, exact affected rerun, original return, human decision | M durable native and report audit; H native final acceptance; no platform-decision probing |

## Scenario changes and completeness

Formal testcase IDs later map to these stable IDs plus parameter keys. Missing variants, missing manual records, inactive/skipped assertions, artifact mismatches or missing accepted inputs prevent an unqualified completion claim. A named criterion cannot inherit PASS from a producer check or another candidate. AX-SC rows include provisional absence checks; absence must be observed on the actual page and all states.

Source artifacts to publish: README.md, coverage.md, api.md, fixtures.json, browser-manual.md, accessibility.md, operations-lifecycle.md, harness.md, browser-input.md, impact-ts-2.md and manifest.json. Separate TS.R examines substantive coverage and unresolved contract gaps. Source review follows the completed separate report; Assurance cannot accept its own scenarios.

## Reverse scenario index

Every defined scenario family member appears below; each AX-SC row inherits A1 and its AX procedures from accessibility.md. TC must retain per-parameter API/entry/display distinctions.

| Scenario IDs | Criteria |
|---|---|
| API-01 | B1, T1 |
| API-02 | B1, B2 |
| API-03–04 | B1, B2, T1 |
| API-05 | B1, B2, L1, T1 |
| API-06–13 | B2, T1 |
| API-14–18 | T1 |
| UNI-01–08 | B2, T1 |
| DATA-01–03 | T1 |
| DATA-04 | B1, T1 |
| DATA-05 | T1 |
| SEC-01–03 | O1, T1 |
| UI-01 | B1, U1, V1 |
| UI-02 | B1, B2, T1, U1, V1 |
| UI-03 | B2, T1 |
| UI-04 | B1 |
| UI-05 | B1, T1, V1 |
| UI-06–09 | B1, T1, U1, V1 |
| UI-10 | T1, V1 |
| UI-11 | A1, B1, T1, V1 |
| UI-12 | A1, B2, T1, U1, V1 |
| VIS-01–03 | V1 |
| HUM-01 | B1, O1, U1, V1 |
| HUM-02 | A1, U1 |
| AX-01–08 | A1 |
| PKG-01–03 | T2 |
| OPS-01–02 | O1, T2 |
| OPS-03–05 | O1 |
| OPS-06–09 | O2 |
| LIFE-01–05 | L1 |
| HAR-01–07 | L1 |
| HAR-08–10 | L1, O1, T2 |
| HAR-11 | L1, O2 |
| HAR-12 | L1 |
| All 55 AX-SC parameter IDs | A1 |

## TS-3 affected security coverage

SEC-01 O01–O12, SEC-02 H01–H13 and SEC-03 P01–P15 map to T1 and O1. Expand every row by its explicit alternatives and I/H instance-host parameters; conditional H10–H12 require exact independently verified QA-route inputs. Positive: O01/O02/O10/O12, H01/H02/H10/H13, P10/P14. Negative: O03–O09/O11, H03–H09/H11/H12, P01–P09/P11–P13/P15. Boundary: numeric host comparison, distinct origin tuples/ports, absent versus present-empty Origin, conditional alias disabled/enabled, 16,384/16,385 bytes, parser-before-dispatch and body suppression. Mixed positive/negative H13 and route P14 retain each exact outcome.

A later automated suite must map each parameter; M static/control and browser observations plus O setup/route/fault evidence remain explicit in api.md. Neither conditional unavailability nor transport refusal closes a dispatched-application obligation. Header tests do not replace OPS-04. OBS-01 input is supplied by accepted BASE-3; TSR-01 is an author correction pending fresh independent TS.R, not independently closed. Existing TSR-02/03 corrections, API-05/C0 failure expectation and all ten criterion mappings remain.
