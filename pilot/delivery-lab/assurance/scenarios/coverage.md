# TS-1 criterion coverage

All expected outcomes derive from accepted BASE-2; modes and tuple assertions are defined in README. This is design coverage, not PASS evidence. Each listed range includes every defined member and every parameter variant. Negative operational cases are safe fixture/config comparisons or abort-path observations, not authority to create an unsafe deployment.

| Criterion | Positive scenarios | Negative scenarios | Boundary / recovery scenarios | Modes and required evidence |
|---|---|---|---|---|
| B1 useful journey | API-01, UI-01, HUM-01 | API-03–05, UI-02, UI-06 | API-02, UI-04–09, DATA-04 | A API tuples/network/browser; M reload; H understands journey/wording |
| B2 validation | API-02, UNI-01–06, UI-03 | API-03–11, API-13, UI-02 | API-05 C0 FAIL, API-12, UNI-01–08 | A API and UI strings; missing/non-string/malformed are direct API cases; M error association |
| T1 contract/data | API-01, API-14–18, DATA-01–05, UI-10 | API-03–13, API-16–17, SEC-01–03 | UNI-01–08, DATA-02–05, UI-05–09 | A exact schema/errors/headers/order/tuples; O process/container restart; M text safety; OBS-01 open |
| T2 package | PKG-01–03, OPS-01–02 | PKG-02–03, HAR-08–10 | clean build, archive round-trip, config/digest disagreement | A/M pinned build/lock/manifest/config and inventory; O operator packet; CI unavailable remains open |
| V1 visual | VIS-01, UI-01, HUM-01 | VIS-02, UI-02, UI-05–09 | VIS-01–03 and UI-10 at 390×844 / 1440×900 / 320 CSS px | A captures; M layout/state comparison; H final appearance |
| A1 accessibility | AX-01–08 and all AX-SC rows | invalid/failed/uncertain states in AX-01–08 | zoom, reflow, text spacing, keyboard/focus/AT and provisional absent features | A scanner + DOM, M actual keyboard/screen-reader/measurements; H route observations; all 55 A/AA rows accounted |
| U1 usability | HUM-01–02, UI-01 | HUM-02, UI-02, UI-06–09 | retained input, failed initial/reconciliation GET, deliberate second create | A input/request assertions; M facilitation record; H uncoached verdict; no timing threshold |
| O1 persistent access | OPS-01–05 | OPS-01–04, SEC-01–03, HAR-08–10 | actual host route; all sessions ended; restart; IPv4/IPv6 | O operator configuration/session operation; A/M independent identity/access; H later remote-desktop visit |
| O2 recovery | OPS-06–09 | OPS-06–09, HAR-11 | backup with WAL, restore tuples, known-good qualification without O2 cycle, final C1 | O Engineer recovery; A/M independent checksum/digest/schema/tuple checks; no review reset |
| L1 delivery proof | LIFE-01–05, HAR-01–12 | API-05/C0, LIFE-02, HAR-02–12 | fresh producer session, exact affected rerun, original return, human decision | M durable native and report audit; H native final acceptance; no platform-decision probing |

## Scenario changes and completeness

Formal testcase IDs later map to these stable IDs plus parameter keys. Missing variants, missing manual records, inactive/skipped assertions, artifact mismatches or unresolved OBS-01 prevent an unqualified completion claim. A named criterion cannot inherit PASS from a producer check or another candidate. AX-SC rows include provisional absence checks; absence must be observed on the actual page and all states.

Source artifacts to publish: README.md, coverage.md, api.md, fixtures.json, browser-manual.md, accessibility.md, operations-lifecycle.md, harness.md and manifest.json. Separate TS.R examines substantive coverage and unresolved contract gaps. Source review follows the completed separate report; Assurance cannot accept its own scenarios.
