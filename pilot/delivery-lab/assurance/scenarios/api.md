# API and data scenarios — TS-1

Normative source: BASE-2 `api.md`, with architecture Host/Origin restriction pending OBS-01. Mode A except restarts A/O. Each case starts from F-SEED (or its explicit fixture) and a captured S0. Use an authorized Host, same-origin or non-browser accepted route, and `Content-Type: application/json` unless the case changes it. UTF-8 JSON property order is immaterial; additional properties, exact string values, numeric types and array order are significant. Exact error fixtures are in fixtures.json; no default framework errors may replace them. Request/response byte captures, tuple snapshots and fixture identity are required.

## Requests and responses

| ID / kind | Given / action | Exact expected response and record effect |
|---|---|---|
| API-01 positive | GET list; POST `{"name":"  Pilot notebook  "}` once; GET twice and reload | GET 200 `{items:[...]}`; POST 201 Item directly with name `Pilot notebook`, fresh lowercase UUIDv4, valid UTC timestamp with six decimals and Z; S1 contains returned tuple exactly once, all S0 unchanged. Both later GETs identical and write-free. UI evidence separately in UI-01. |
| API-02 boundary | Independently POST each 1/80 scalar valid fixture, including surrounding trim characters | 201 exact trimmed name; no normalization; one new tuple each. 80 astral scalars succeed despite 160 UTF-16 units. All generated IDs/times satisfy DATA-01. |
| API-03 negative | POST `{}`, then each name type null, false, true, 0, 1.5, `[]`, `{}` separately | 422 E-REQUIRED for missing; E-TYPE for every non-string. S1=S0 for each request; never coerce input. |
| API-04 negative | POST empty string and each 81-scalar fixture | 422 E-LENGTH; S1=S0. Do not truncate and insert. |
| API-05 negative / C0 sentinel | POST `{"name":" \t\r\n "}` directly, then each trim code point alone and combined trim-only fixture | 422 E-LENGTH, S1=S0 for every variant. C0's acceptance of whitespace produces ordinary FAIL with request/response and added tuple retained as evidence; never xfail/skip or cleanup before capture. C1 uses the identical oracle. |
| API-06 negative | Each raw top-level `null`, `true`, `1`, `"text"`, `[]` | 422 E-OBJECT; S1=S0. A JSON object with name:null uses API-03, not E-OBJECT. |
| API-07 negative/priority | POST `{"extra":1}`, `{"name":"valid","extra":1}`, `{"name":null,"extra":1}` | 422 E-UNKNOWN for each, before missing/type checks; S1=S0. |
| API-08 negative | Independently raw empty bytes, truncated JSON, trailing comma, invalid UTF-8, duplicate keys, NaN, Infinity, -Infinity | 400 E-JSON; S1=S0. Exact byte fixtures in fixtures.json; valid non-object JSON uses API-06. |
| API-09 negative | name is JSON escape for lone high surrogate, lone low surrogate, or valid character plus lone surrogate | 422 E-UNICODE; S1=S0. A paired surrogate encoding of an astral scalar succeeds. Unicode-invalid name with 81 characters still produces E-UNICODE before length. |
| API-10 negative | Omit Content-Type; send text/plain, form encoding, application/xml, each with a short valid JSON body | 415 E-MEDIA; S1=S0. application/json and application/json;charset=utf-8 succeed for valid short input. Unspecified content-type parameters/case variants are not frozen by this scenario. |
| API-11 negative | Send valid name JSON padded with ASCII spaces to 16,385 UTF-8 bytes | 413 E-SIZE; S1=S0. Byte count includes whitespace. Repeat with multibyte name fixture so counting characters instead of bytes would choose wrong branch. |
| API-12 boundary/priority | 16,384-byte valid body; 16,384-byte malformed body; 16,385-byte malformed body with missing media type; short malformed body missing media type | Respectively 201 (+one tuple), 400 E-JSON (unchanged), 413 E-SIZE (unchanged), 415 E-MEDIA (unchanged). Byte-limit, media, parse, structure, extra, missing, type, surrogate, length ordering is mandatory on authorized Host/Origin. |
| API-13 negative/priority | Object with unknown key and invalid name; duplicate keys plus unknown key; unpaired name surrogate plus overlong text | Respectively E-UNKNOWN/422, E-JSON/400, E-UNICODE/422; S1=S0. Return only the first field error. Error bodies do not echo the supplied name or internal diagnostics. |
| API-14 positive | POST `Pilot notebook` twice as two deliberate requests | Two 201s, same name, different UUIDv4s; count increases by two; tuples immutable and each appears once. Duplicate values are permitted; no false deduplication. |
| API-15 negative/read-only | GET `/api/no-such-route`; PUT `/api/items` with valid body | 404 E-NOTFOUND; 405 E-METHOD respectively, no writes. 405 includes Allow declaring supported GET and POST, with no unsupported method. Baseline does not freeze Allow serialization or optional framework HEAD/OPTIONS handling. |
| API-16 negative/storage | Accepted TC QA fault proves no transaction started, lock exceeds 5 seconds before write, or verified rollback; exercise GET and POST independently | 503 E-STORAGE; S1=S0; no persistent probe/error row. Capture lock/fault timing and rollback proof; no invented upper latency/SLA threshold. A 503 with committed row is FAIL. Fault mechanism not yet implemented here. |
| API-17 negative/uncertain | Accepted injection produces internal failure before commit in one run and after commit in another | Both return 500 E-INTERNAL if HTTP response is delivered. Precommit fixture yields S1=S0; postcommit fixture yields one new tuple. Response alone establishes neither; UI reconciles in both (UI-07). No 503 substitute when outcome is unknown. Lost response is UI-08, not a presumed 500. |
| API-18 positive/headers/schema | Read `/`, each API success and the specified errors on allowed route; examine published OpenAPI | API responses application/json, API+HTML Cache-Control:no-store. Exact Item, list, error and version key sets/types match baseline; no secret/path/input leakage. OpenAPI agrees with public schema/errors including 400 and custom 422; unavailable schema is recorded. Headers are compared semantically, not by case/order. |

## Unicode parameter families (A; API plus UI string input)

Every member is independently reset or snapshots sequentially with explicit expected deltas. `fixtures.json` records actual strings, scalar counts and expected trimmed names. Never use a browser maxlength guard as the oracle.

| ID | Parameter / action | Expected result |
|---|---|---|
| UNI-01 | ASCII `A` repeated 1,80,81; padded 80 | 201/201/422/201; exact trimmed name on success, E-LENGTH/no change on rejection. |
| UNI-02 | Astral notebook symbol repeated 1,80,81 | Same boundary results, counting scalars not UTF-16 units/UTF-8 bytes. |
| UNI-03 | Combining `e`+U+0301 repeated 40 (=80) and that plus `x` (=81); precomposed U+00E9 repeated 80 | 201/422/201; stored combining text is not normalized. |
| UNI-04 | Each of the 25 named trim scalars on both ends of `A` and of 80 `A`; each by itself | Trim to A / 80 A (201); alone E-LENGTH (422), no write. |
| UNI-05 | U+200B and U+FEFF individually and around `A`; U+001C and U+0000 around `A` via JSON escapes | Preserved exactly, nonempty scalar counts valid, 201. They are outside the explicit trim set. Log and display remain safe text. |
| UNI-06 | `A` + interior tab, NBSP, newline + `B`; mixed non-Latin characters; valid surrogate pair encoding | Preserve all interior scalars, 201. No whitespace collapsing, normalization or case folding. |
| UNI-07 | Lone high/low surrogate escapes and mixed invalid sequence | API-only E-UNICODE; native text input cannot promise to transmit a lone surrogate, so no invented UI equivalent. |
| UNI-08 | 80 vs 81 scalars made from interior whitespace and combining/non-Latin/astral characters | 201 vs E-LENGTH/422, unchanged rejected snapshot. Distinguishes byte/grapheme/string-unit counting. |

## Data and operational endpoint oracles

| ID | Fixture / action | Required outcome |
|---|---|---|
| DATA-01 | Every successful POST; read item repeatedly | Exactly `id,name,created_at`; UUIDv4 lowercase with valid variant; timestamp is calendar-valid UTC `YYYY-MM-DDTHH:mm:ss.ffffffZ`; name equals exact trimmed scalars. IDs server-generated, unique, immutable. Timestamp lies in recorded server-clock observation window if clock stable; never impose client-clock order. |
| DATA-02 | F-ORDER inserted out of sort order, including equal timestamps; GET twice | Exact F-ORDER.expected_items order (ascending stored time then ASCII lowercase ID), never insertion/name order. S1=S0; all records exactly once. |
| DATA-03 | F-UNINITIALIZED, F-EMPTY, F-NONEMPTY each at startup; repeated GET and restart | First empty/uninitialized store gets exactly three seed names and initialized marker atomically, distinct IDs/ordered timestamps. Initialized empty stays empty. Nonempty store is never reseeded; all existing tuples survive. GET never seeds. Fixture installation requires accepted TC method. |
| DATA-04 | F-SEED + one acknowledged create; Engineer process restart then separate container restart against same volume | Before each restart record 201/tuple, source/image/config/volume and all rows; after each health/ready restored, same tuple set including IDs/times, no repeated seeds. No acknowledged-create loss. A restart while a POST is unacknowledged cannot be counted as acknowledged-loss proof. |
| DATA-05 | Repeated `/healthz`, `/readyz`, `/api/version` on ready store; isolated not-ready DB/schema/identity variants | health 200 `{status:"ok"}` for live process even DB unavailable; ready 200 `{status:"ready"}` only when all probes pass. Not-ready 503 exactly `{status:"not_ready"}` (no error wrapper). Version 200 exact four keys, full source SHA/build matches external manifest, contract_version string `1`, schema_version integer 1. Missing identity prevents readiness. No probe rows persist; unchanged snapshot. Startup exit for invalid config is allowed only as documented with no readiness claim. |

## Retained boundary gap

SEC-01 (A/M, T1/O1): allowed Host with same-origin browser create accepts valid input; unauthorized browser Origin cannot create or gain a CORS allowance. SEC-02 (A/M): Host outside published loopback values/declared ports and explicitly authorized QA service name must be rejected. SEC-03 (A): combined unauthorized Host + Origin, and each combined with oversized/malformed/wrong-media/invalid-name bodies, needs deterministic precedence and no write. Candidate exact denied status/body/check order is **UNRESOLVED OBS-01**. Record the missing oracle; do not encode `any 4xx` as final compliance or silently freeze 403/400 defaults. Origin handling without Origin header and permitted internal QA route must be pinned in the supplementary input. Native external access proof is separately OPS-04; a Host error is not authentication.
