# API and data scenarios — TS-3

Normative source: accepted BASE-3 `api.md` and `architecture.md` at `a76f458655c9bd2a8ef95562651e0c9155f6a878`; exact input hashes/provenance are in manifest.json. Mode A except restarts A/O. Each case starts from F-SEED (or its explicit fixture) and a captured S0. Use an authorized Host, same-origin or non-browser accepted route, and `Content-Type: application/json` unless the case changes it. UTF-8 JSON property order is immaterial; additional properties, exact string values, numeric types and array order are significant. Exact error fixtures are in fixtures.json; no default framework errors may replace them. Request/response byte captures, tuple snapshots and fixture identity are required.

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
| API-15 negative/read-only | GET `/api/no-such-route`; PUT `/api/items` with valid body | 404 E-NOTFOUND; 405 E-METHOD respectively, no writes. 405 includes Allow declaring supported GET and POST, with no unsupported method. Allow serialization and optional HEAD handling remain unfrozen. BASE-3 requires admitted OPTIONS `/api/items` to follow this 405 E-METHOD contract; admission denials take precedence (SEC-03). |
| API-16 negative/storage | Accepted TC QA fault proves no transaction started, lock exceeds 5 seconds before write, or verified rollback; exercise GET and POST independently | 503 E-STORAGE; S1=S0; no persistent probe/error row. Capture lock/fault timing and rollback proof; no invented upper latency/SLA threshold. A 503 with committed row is FAIL. Fault mechanism not yet implemented here. |
| API-17 negative/uncertain | Accepted injection produces internal failure before commit in one run and after commit in another | Both return 500 E-INTERNAL if HTTP response is delivered. Precommit fixture yields S1=S0; postcommit fixture yields one new tuple. Response alone establishes neither; UI reconciles in both (UI-07). No 503 substitute when outcome is unknown. Lost response is UI-08, not a presumed 500. |
| API-18 positive/headers/schema | Read `/`, each API success and the specified errors on allowed route; examine published OpenAPI | API responses application/json, API+HTML Cache-Control:no-store. Exact Item, list, error and version key sets/types match baseline; no secret/path/input leakage. OpenAPI agrees with public schema/errors including 400 and custom 422; unavailable schema is recorded. Headers are compared semantically, not by case/order. |

## Unicode parameter families (A; literal API, mapped browser variants)

Every member is independently reset or snapshots sequentially with explicit expected deltas. `fixtures.json` records unchanged literal API strings, scalar counts and expected trimmed names. Its separate `browser_input` member and [browser-input.md](browser-input.md) specify whether literal entry is representable, exact native control value, method and browser oracle. CR/LF literal preservation is API-only; sanitized single-line entry and browser display of API-created names are distinct required checks. Never use browser maxlength or an observed app value as the oracle.

| ID | Parameter / action | Expected result |
|---|---|---|
| UNI-01 | ASCII `A` repeated 1,80,81; padded 80 | 201/201/422/201; exact trimmed name on success, E-LENGTH/no change on rejection. |
| UNI-02 | Astral notebook symbol repeated 1,80,81 | Same boundary results, counting scalars not UTF-16 units/UTF-8 bytes. |
| UNI-03 | Combining `e`+U+0301 repeated 40 (=80) and that plus `x` (=81); precomposed U+00E9 repeated 80 | 201/422/201; stored combining text is not normalized. |
| UNI-04 | Each of the 25 named trim scalars on both ends of `A` and of 80 `A`; each by itself | Trim to A / 80 A (201); alone E-LENGTH (422), no write. |
| UNI-05 | U+200B and U+FEFF individually and around `A`; U+001C and U+0000 around `A` via JSON escapes | Preserved exactly, nonempty scalar counts valid, 201. They are outside the explicit trim set. Log and display remain safe text. |
| UNI-06 | `A` + interior tab, NBSP, LF + `B`; separate interior CR and CRLF strings; mixed non-Latin characters; valid surrogate pair encoding | Literal API: preserve all interior scalars, 201, no normalization/case folding/collapsing. UI-03 uses each explicit browser control variant; UI-10 displays the API-created literal names. These are distinct identities and oracles, not substitutions. |
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

## SEC-01–03 — accepted Host/Origin admission (TSR-01 correction)

Normative basis: BASE-3 `api.md` Request admission and `architecture.md` Host and Origin admission. These are T1/O1 design obligations, not runtime results or a finding-closure decision. OBS-01's missing input is supplied by accepted BASE-3; independent TS.R must examine this correction before source review. Earlier TS-1/TS-2 FAIL reports remain unchanged.

### Shared fixtures, oracles and applicability

Use F-SEED and capture all tuples S0 before each variant. A denied/rejected request requires S1=S0, including IDs, names and timestamps, no probe/error row and no insert/update/delete. Re-observe through an admitted route after restoring a temporary fault. The default create is exactly `POST /api/items`, `Content-Type: application/json`, UTF-8 `{"name":"Pilot notebook"}`, with no forwarded headers. Run every applicable parameter separately, restoring only isolated QA fixtures through the accepted later TC method. Accepted creates require API-01's 201 Item and exactly one new tuple; admission passing alone is not a success oracle.

For published authorities, parameterize instance I over QA (P=18081) and review (P=18080), host H over `127.0.0.1` and `localhost`. Host A is `H:P`, and matching Origin O is `http://H:P`. The other instance port is Q. These are contract configuration variants exercised in isolated QA; no review-data resets or unauthorized alternate deployment are implied. A future actual-port mismatch blocks release pending explicit amendment and affected examination. Record actual admitted authority, environment/configuration identity and client-to-service route; never assume agent localhost reaches host localhost.

Literal denial oracles (exact JSON values, no additional members):

- E-HOST: HTTP 403, `{"error":{"code":"host_not_allowed","message":"Host is not allowed.","fields":[]}}`.
- E-ORIGIN: HTTP 403, `{"error":{"code":"origin_not_allowed","message":"Origin is not allowed.","fields":[]}}`.

For both: `Content-Type: application/json`, `Cache-Control: no-store`, no `Access-Control-Allow-*` header, no reflected Host/Origin, no body parsing or storage-readiness probe before rejection, zero writes. Header field-name case/order and JSON member order/insignificant whitespace are immaterial; response strings, types and member sets are exact. Do not accept another 4xx, a framework text body or a reflected error as equivalent. E-SIZE/MEDIA/JSON/OBJECT/UNKNOWN/REQUIRED/TYPE/UNICODE/LENGTH/STORAGE/INTERNAL/METHOD retain fixtures.json's exact envelopes and API-03–17 effects.

Mode A: later independent HTTP assertions and tuple snapshots. Mode M: later static examination of admission-before-routing/parsing/probes, route coverage and configuration, plus browser network observations where headers are browser-set. A browser cannot freely set Host or invalid/raw Origin; send those HTTP variants using the later approved QA client, not DOM value injection or a browser request that never reached the service. Mode O: authorized operator fault/setup and actual-route proof, before runtime examination. No implementation is inspected or executable test authored in TS. Missing route/fault/client capability is UNAVAILABLE, not PASS.

Keep raw wire request, response and proof of application dispatch. Missing/malformed/multiple headers may be rejected by the HTTP parser before dispatch: record that transport result separately; it is neither E-HOST/E-ORIGIN evidence nor an application violation when dispatch did not occur. Do not disable the parser or fabricate a dispatch claim. An accepted later harness may exercise the dispatched-request boundary directly with separate seam identity; it does not replace real network/access proof. Timeouts, disconnects and invalid framing remain outside the received-request JSON oracle. For methods suppressing bodies (e.g. HEAD), assert denial status and relevant headers with HTTP body suppression; do not require JSON bytes on the wire. Internal selected error-code claims require separate observable evidence.

### SEC-01 — Origin matrix (A/M, T1/O1)

Use admitted Host A for every row. Unless stated otherwise use the default valid create. The IDs below are parameter keys under SEC-01; each semicolon-separated value is a separate variant. Every denial is E-ORIGIN and S1=S0.

| Key | Origin input / action | Exact expected result |
|---|---|---|
| O01 | Exactly O for each I/H | Admission passes; 201 Item, +one tuple. Browser same-origin create independently observes the same result. |
| O02 | Header absent, for each I/H | Admission passes; default create 201/+one. Separately GET `/healthz` 200 `{status:"ok"}` on live process, and ready `/readyz` 200 `{status:"ready"}`; both write-free. Absence is allowed, not authentication. |
| O03 | For Host `localhost:P`, Origin `http://127.0.0.1:P`; reverse pairing | E-ORIGIN although both hostnames are separately admitted Hosts. |
| O04 | `http://H:Q`; `http://H:8000`; `http://H` (effective 80); `http://H:80` | E-ORIGIN for each; numeric port must match the admitted instance. |
| O05 | `https://H:P`; `https://H`; `ftp://H:P` | E-ORIGIN: configured scheme is HTTP; no trust in forwarded scheme. |
| O06 | Empty value; literal `null` | E-ORIGIN for each present value. Do not treat either as absent. |
| O07 | `not-an-origin`; `http://`; `http://H:P/path`; `http://H:P?x=1`; `http://user@H:P` | E-ORIGIN: malformed/non-serialized origin values. Capture actual wire bytes. |
| O08 | Two Origin fields both O; two fields O plus `http://example.invalid`; one comma-list `O, http://example.invalid`; one space-list `O http://example.invalid` | E-ORIGIN when dispatched; never choose the first allowed entry or split into an allowed subset. |
| O09 | `http://localhost.evil.invalid:P`; `http://sub.localhost:P`; `http://localhost.:P`; `http://127.0.0.2:P`; `http://[::1]:P` | E-ORIGIN for each: different normalized hostname, no suffix/prefix or loopback equivalence. |
| O10 | Host `LoCaLhOsT:P`, Origin `http://localhost:P` | Parsed DNS comparison passes; default create 201/+one. Also Host `localhost:P`, Origin `http://LOCALHOST:P` compares normalized hostname and passes. |
| O11 | Host A, Origin `http://example.invalid`, with `Forwarded: host=A;proto=http`, `X-Forwarded-Host: A`, `X-Forwarded-Proto: http` | E-ORIGIN; forwarded values cannot make the denied actual Origin trusted. |
| O12 | Host A and O (then absent Origin), with `Forwarded: host=example.invalid;proto=https`, `X-Forwarded-Host: example.invalid`, `X-Forwarded-Proto: https` | Actual admission unchanged: default create 201/+one for each. No forwarded-host/scheme trust. |

For O07/O08 and raw empty headers, distinguish application dispatch from transport refusal as above. Browser cross-origin observation supplements the direct HTTP oracle: an attempted browser request cannot create or obtain CORS access. If browser policy/preflight prevents the POST, record that actual path and its no-write result; it does not prove the absent POST's denial JSON.

### SEC-02 — Host matrix and conditional QA authority (A/M/O, T1/O1)

Use absent Origin to isolate Host checks, and separately matching O for H01/H02. Every dispatched Host denial is E-HOST and S1=S0.

| Key | Host input / configuration | Exact expected result |
|---|---|---|
| H01 | A for every I/H | Default create 201/+one; absent and matching Origin each pass. |
| H02 | `LoCaLhOsT:P`; `localhost:0P` with the literal decimal digits of P prefixed by zero | Parsed ASCII case-insensitive hostname/numeric-port equality passes; default create 201/+one. Origin uses normalized O. |
| H03 | Header missing; empty | E-HOST if dispatched. The client must not silently synthesize a valid Host. |
| H04 | `H` with no port; `H:Q`; `H:8000`; `H:80`; `H:0` | E-HOST for each. Declared port is required, not inferred. |
| H05 | `H:abc`; `H:65536`; `H:P:extra`; `user@H:P`; `http://H:P`; `H:` | E-HOST if dispatched: malformed authority is not an allowlist member. |
| H06 | Two Host fields A and A; A and `example.invalid:P`; comma-list `A,example.invalid:P` | E-HOST if dispatched; do not accept one member or collapse duplicates into an admitted request. |
| H07 | `localhost.:P`; `sub.localhost:P`; `localhost.evil.invalid:P`; `evil-localhost:P`; `127.0.0.2:P`; `[::1]:P`; `example.invalid:P` | E-HOST for each: no trailing-dot, subdomain, arbitrary-IP, IPv6 or suffix exception. |
| H08 | Actual Host `example.invalid:P`, Origin O, with `Forwarded: host=A;proto=http` and `X-Forwarded-Host: A` | E-HOST despite allowed forwarded values and Origin. |
| H09 | Before verified QA exception exists: a concrete unverified synthetic service name `unverified-pilot.invalid:8000` | E-HOST. Configuration/manual check requires zero internal aliases; the documented placeholder is not a value to enable. |
| H10 | Only after a runtime input packet independently verifies one existing authorized QA route, concrete service name S, service identity, access and QA/review network/data isolation: Host `S:8000` in QA, Origin `http://S:8000`, then absent Origin | Both default creates 201/+one; retain proof identities. Without prerequisites this conditional branch is UNAVAILABLE, never an invented enabled alias. No route or connection is selected/created by TS. |
| H11 | Under that verified QA configuration: `S:8001`; `other-S:8000`; `S.evil.invalid:8000`; `S:8000` against review configuration | E-HOST for each. No namespace wildcard, extra alias or review alias. |
| H12 | Under verified QA alias: Host `S:8000`, Origin O for published loopback authority; `http://S:18081`; `https://S:8000` | E-ORIGIN for each; QA admission has no global Origin bypass. |
| H13 | Health probe uses H01 or verified H10 admitted Host with absent Origin; then an unverified Host | Live `/healthz`: 200 `{status:"ok"}`, unchanged records; denied probe: E-HOST/unchanged. A health probe has no blanket exception. |

Header admission is separate from OPS-04's authenticated external-access proof. A client can spoof/omit headers; a 403 is not proof of network isolation. Preserve loopback publication and actual-port checks; do not expose or reconfigure any service to conduct these variants.

### SEC-03 — first-failure and route matrix (A/M/O, T1/O1)

Unless a row specifies otherwise, each case is matched POST `/api/items`. Define denied Host D=`example.invalid:P` and denied Origin X=`http://example.invalid`. A/O mean the admitted pair. Short invalid bytes are literal UTF-8 `{`. Oversized malformed bytes are `{` plus 16,384 ASCII spaces (16,385 total). Oversized valid JSON is the default create padded with ASCII spaces to 16,385 total. Boundary variants use exactly 16,384 bytes. Fault configurations require a separately accepted TC method and evidence; do not access storage to decide a rejection.

| Key | Competing defects / parameters | First result and record effect |
|---|---|---|
| P01 | D + X; body independently valid, oversized valid, oversized malformed, short malformed, wrong media, `{}`, `{"name":" "}` | E-HOST, S1=S0 for every body. Include the maximal combination D + X + oversized malformed + text/plain. |
| P02 | D + O, then D + absent Origin, with each P01 body | E-HOST, S1=S0. Origin cannot repair denied Host. |
| P03 | A + X with each P01 body; include oversized malformed + text/plain | E-ORIGIN, S1=S0; no eager size/media/parse/field rejection. |
| P04 | A + O, then A + absent Origin; 16,385-byte malformed body + text/plain | 413 E-SIZE, S1=S0: establish size before choosing media failure. |
| P05 | A + O; 16,384-byte malformed body + text/plain; short `{` with missing Content-Type | 415 E-MEDIA, S1=S0 for both. |
| P06 | A + O; 16,384-byte malformed body + application/json; short duplicate-key JSON with invalid name and unknown property | 400 E-JSON, S1=S0 for both; parsing precedes field validation. |
| P07 | A + O; JSON top-level `[]` | 422 E-OBJECT, S1=S0. |
| P08 | A + O; `{"extra":1}`; `{"extra":1,"name":null}`; `{"extra":1,"name":" "}` | 422 E-UNKNOWN for each, S1=S0; unknown property precedes missing/type/length. |
| P09 | A + O; `{}`; `{"name":null}`; name containing lone high surrogate plus 81 `a` scalars; `{"name":" "}` | Respectively 422 E-REQUIRED, E-TYPE, E-UNICODE, E-LENGTH; S1=S0. Existing field priority unchanged; API-05 remains required C0 FAIL, identical C1 oracle. |
| P10 | A + O; exactly 16,384-byte valid default create, padded with spaces | 201 Item, +one tuple. A size limit must not reject equality. |
| P11 | Verified unavailable storage (no transaction), with D+X, then A+X, then A+O+invalid name | Respectively E-HOST, E-ORIGIN, 422 E-LENGTH; S1=S0 and no admission-path readiness probe. Capture static/accepted instrumented evidence for probe ordering; response alone cannot prove no probe. |
| P12 | Same unavailable storage, A+O+valid create; then separately accepted precommit and postcommit internal-failure fixtures | 503 E-STORAGE/unchanged for unavailable storage. Internal failures use API-17's exact 500 E-INTERNAL and respective zero/one committed tuple. Do not extend rejection's no-write rule to 500. |
| P13 | Independently `/`, the exact published static-asset routes, GET `/api/items`, `/healthz`, `/readyz`, `/api/version`, GET `/api/no-such-route`, PUT `/api/items`, OPTIONS `/api/items`; each with D+X, then A+X | E-HOST then E-ORIGIN, before route/method handling or readiness; S1=S0. Repeat `/readyz` with proven not-ready store; admission still wins over 503. Bind asset paths to future candidate manifest. |
| P14 | Same relevant routes with A+O, then A+absent Origin, and valid ready state | Admission passes. `/` and published assets return their normal success; APIs/probes retain API-01/DATA-05 exact oracles. Unknown route 404 E-NOTFOUND, PUT and OPTIONS `/api/items` 405 E-METHOD, supported Allow set GET/POST; no CORS allowance and no writes. No invented static-asset content oracle before candidate identity. |
| P15 | HEAD on a dispatched route with D+X, then A+X | Denial 403, required denial headers, no Access-Control-Allow-* and no body bytes under HEAD semantics; unchanged records. Record code selection only if independently observable, never infer it from an absent body. |

At each rejection, check one exact first-failure body rather than accepting a set of possible codes. Matched-create body checks do not override admission on unknown routes or unsupported methods. Record each transport-inconclusive variant and remaining application obligation separately. Independent review/verification later determines closure; this author supplies no runtime PASS or source acceptance.
