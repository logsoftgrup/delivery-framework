# Delivery Lab API contract — v1

Normative for B1/B2/T1; operations support T2/O1/O2. Same-origin HTTP JSON on the loopback-bound service. Examples are synthetic. All JSON responses use `application/json`; APIs and HTML use `Cache-Control: no-store`. No pagination, filtering, update or delete route. No application authentication; host access controls in [runbook](runbook.md) are required. No wildcard CORS; accept create only as JSON and reject cross-origin browser requests.

## Request admission — OBS-01 amendment

### Denials and response contract

For application-handled requests, reject a disallowed Host with **HTTP 403**, `Content-Type: application/json`, `Cache-Control: no-store`, and this exact JSON value:

```json
{"error":{"code":"host_not_allowed","message":"Host is not allowed.","fields":[]}}
```

Reject a present, disallowed Origin with **HTTP 403**, the same response headers, and this exact JSON value:

```json
{"error":{"code":"origin_not_allowed","message":"Origin is not allowed.","fields":[]}}
```

These contain no extra members and no echoed Host/Origin. JSON property order and insignificant serialization whitespace remain immaterial under the accepted envelope rule. Neither response grants CORS access: emit no `Access-Control-Allow-*` headers. The bodies above are the literal create-API oracle; methods that suppress response bodies under HTTP semantics do not change the denial status/code selected internally. Both denials occur before body parsing, storage readiness probes or writes, and insert/change zero records.

### Host and Origin admission

Apply Host, then Origin admission before application route/method handling, including static assets and operational endpoints. The ordinary 404/405 and operational results are considered only after admission. This also ensures an OPTIONS request never obtains a CORS allowance; after passing admission it follows the existing unsupported-method contract.

For each instance, compare the parsed Host authority with its exact configured allowlist. Published review permits only `127.0.0.1:18080` and `localhost:18080`; published QA permits only `127.0.0.1:18081` and `localhost:18081`. DNS hostname comparison is ASCII case-insensitive and ports are numeric. Require the declared port; do not silently permit another port or the other instance's port. Missing, empty, malformed or multiple Host values reaching the application are denied as `host_not_allowed`. Do not admit trailing-dot aliases, subdomains, arbitrary IPs, IPv6 aliases, wildcard suffixes, or forwarded-host values. Transport/parser failures that prevent application dispatch are outside this application JSON contract and must be identified separately, not counted as this oracle.

For any admitted request carrying Origin, require exactly one serialized non-opaque HTTP origin whose scheme, normalized hostname and effective port equal the request's admitted origin. Use the actual configured HTTP scheme and admitted Host authority; do not derive a trusted origin from `Forwarded`/`X-Forwarded-*`. Compare by origin tuple, not string prefix or suffix. Thus `localhost` and `127.0.0.1` are different origins even when both are allowed Hosts; QA and review ports are also different origins. Empty Origin, literal `null`, malformed/multiple/list-valued Origin, scheme mismatch and any other cross-origin value are denied as `origin_not_allowed`. A valid same-origin Origin passes to subsequent checks. Applying present-Origin admission to all dispatched routes, rather than creates alone, is part of this amendment.

**Absent Origin passes Origin admission.** This permits local CLI/health and authorized QA clients that omit it. Host and all remaining checks still apply. This is neither authentication nor permission to expose the service: clients can omit/spoof headers, so the accepted host/network access controls remain required.

### Order and multiple failures

The first failing check wins; return one error and stop:

1. Host admission → 403 `host_not_allowed`.
2. Present-Origin admission → 403 `origin_not_allowed`; absent Origin passes.
3. For a matched `POST /api/items`, body exceeds 16,384 bytes → existing 413 `request_too_large`.
4. Existing media-type rule → 415 `unsupported_media_type`.
5. Existing UTF-8/JSON parse rule → 400 `invalid_json`.
6. Existing validation order → 422 `validation_error`: non-object; unknown property (even with name absent); missing name; non-string name; unpaired surrogate; trimmed scalar count outside 1–80.
7. Only after admission and successful validation may the operation reach storage/commit handling with the existing 503/500 rules.

Both Host and Origin denied, with any body defects: Host wins. Allowed Host plus denied Origin, even with oversize, wrong media, malformed JSON or invalid fields: Origin wins. Admitted Host/Origin plus an oversized wrong-media malformed invalid body: size wins. Within the remaining checks, media beats parsing, and parsing beats field validation. These are precedence definitions for this contract; formal scenarios and test code remain separately owned by Assurance.

The server can inspect headers to decide admission but must not let eager body parsing or eager media validation override those results. With admitted headers, establish whether the body exceeds the byte limit before choosing a media rejection. A valid wire request with several application failures therefore has the deterministic first-failure result above. Transport timeouts/disconnects/framing rejection remain outside this received-request oracle.

### Strictly limited internal QA access

The only additional Host authority is `<verified-pilot-service-name>:8000` in the QA instance, and only after the existing authorized QA route, service identity, network/instance isolation and access are independently verified and recorded. The placeholder is not an authorized hostname. Until those concrete values/proofs exist, enable no internal alias. The corresponding same-origin tuple is `http://<verified-pilot-service-name>:8000`; absent Origin is also permitted under the same general rule. No global Origin bypass, QA-only skip of admission, wildcard service namespace, additional hostname, public listener or review-instance alias is authorized. Health probes must use an admitted Host; they do not require another blanket exception. This contract does not select/create a QA connection or prove runtime reachability.

The published ports remain subject to the existing actual-port verification gate. If either actual port differs, stop release and obtain an explicit contract/configuration amendment with affected re-examination; do not silently expand the allowlist or claim a verified service route.

## Resources and schemas

`GET /api/items` → 200 `{"items":[Item,...]}`. Includes every committed item in ascending `created_at`, then ascending lowercase ASCII `id`; ties use the ID, never unspecified database row order. Read uses one snapshot. JSON object property order is not significant; list order is significant. GET has no write/seed side effect.

`POST /api/items` accepts the JSON object `{"name":"  Pilot notebook  "}` → 201 with the Item object directly (no wrapper):

```json
{"id":"9b5c7a02-c916-4d65-a71a-210f8c7b82d0","name":"Pilot notebook","created_at":"2026-11-17T12:00:00.000000Z"}
```

The server generates lowercase UUIDv4 IDs and UTC timestamps with exactly six fractional digits. They are immutable. Creation time is assigned on insertion; clock changes may affect chronological arrival order, but sorting always follows stored time then ID. Name duplicates are allowed and receive different IDs. Return 201 only after the transaction commits durably. The response is the stored value.

Published structural schemas (JSON Schema 2020-12 notation):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$defs": {
    "CreateInput": {
      "type": "object", "additionalProperties": false,
      "required": ["name"], "properties": {"name": {"type": "string"}}
    },
    "Item": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "name", "created_at"],
      "properties": {
        "id": {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"},
        "name": {"type": "string", "minLength": 1, "maxLength": 80},
        "created_at": {"type": "string", "format": "date-time", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{6}Z$"}
      }
    },
    "ItemList": {
      "type": "object", "additionalProperties": false,
      "required": ["items"], "properties": {"items": {"type": "array", "items": {"$ref": "#/$defs/Item"}}}
    }
  }
}
```

`CreateInput` describes raw structure only: the following trim/scalar/count semantics are mandatory beyond that schema. The stored Item schema applies after trimming. The API implementation must publish matching OpenAPI without changing this contract; default FastAPI validation responses are not the specified public error shape.

## Validation and error priority

After Host and present-Origin admission and routing to `POST /api/items`, apply the body checks (413, 415, 400 and 422 rows) in the listed order and return only the first rejection, before any database write. These rejected checks change no records. The storage and unexpected-failure rows describe execution outcomes after validation; their database-effect rules are specified below. In particular, a 500 response does not guarantee that no commit occurred. No silent string conversion. A JSON string containing an unpaired surrogate is a field validation error. Input must be valid UTF-8; duplicate object keys, NaN/Infinity and empty bodies count as malformed JSON. Maximum request body is 16,384 UTF-8 bytes before parsing (including whitespace); do not use a byte limit as the name length rule.

Trim only these code points from both ends, repeatedly: U+0009–U+000D, U+0020, U+0085, U+00A0, U+1680, U+2000–U+200A, U+2028, U+2029, U+202F, U+205F, U+3000. This explicit set is stable regardless of runtime Unicode version. U+200B and U+FEFF are not trimmed. Preserve interior whitespace and every other scalar, including combining marks, non-Latin and astral characters; no normalization, case folding or grapheme-based count. After trimming, count Unicode scalar code points: an astral symbol counts as one; `e` plus a combining accent counts as two. UI must use the same set and count; JavaScript string length/HTML maxlength alone are insufficient. Accepted names, including control/markup-looking characters, are rendered as text, with line wrapping and no HTML interpretation.

Application error responses use the common envelope below (subject to the HTTP/parser and body-suppression boundary above), except for the explicitly specified not-ready response from `GET /readyz`: its 503 body is exactly `{"status":"not_ready"}`, as defined under Operational endpoints. That readiness response has no `error` member. In the common envelope, `fields` is empty for non-field errors:

```json
{"error":{"code":"validation_error","message":"Check the request fields.","fields":[{"field":"name","code":"name_length","message":"Enter 1–80 characters after trimming surrounding whitespace."}]}}
```

Common error envelope: object with only `error`; error contains string `code`, string `message`, array `fields`; each field entry contains only string `field`, `code`, `message`. For validation, one entry only. Property order is immaterial. Never echo submitted names, internal exceptions, SQL or paths in errors.

| Order / condition | HTTP | error.code / error.message | fields entry (field; code; message) |
|---|---|---|---|
| Body exceeds 16,384 bytes | 413 | `request_too_large` / `Request body is too large.` | empty |
| Content-Type absent or not application/json (optional charset=utf-8 accepted) | 415 | `unsupported_media_type` / `Use application/json.` | empty |
| Invalid UTF-8 / malformed JSON / duplicate keys | 400 | `invalid_json` / `Send a valid JSON object.` | empty |
| Top-level value is not an object | 422 | `validation_error` / `Check the request fields.` | `$`; `object_required`; `Send an object with a name field.` |
| Any property besides name (even if name missing) | 422 | as above | `$`; `unknown_fields`; `Only the name field is allowed.` |
| name missing | 422 | as above | `name`; `name_required`; `Enter a name.` |
| name not a string, including null, bool, number, list, object | 422 | as above | `name`; `name_type`; `Name must be text.` |
| Unpaired surrogate in name | 422 | as above | `name`; `name_unicode`; `Use valid Unicode text.` |
| Trimmed scalar count outside 1–80 | 422 | as above | `name`; `name_length`; `Enter 1–80 characters after trimming surrounding whitespace.` |
| Storage not ready or locked beyond 5 seconds before any write, or a verified transaction rollback | 503 | `storage_unavailable` / `Items are temporarily unavailable. Try again.` | empty |
| Unexpected failure | 500 | `internal_error` / `Something went wrong. Check the list before trying again.` | empty |

After successful Host and Origin admission, unknown route: 404 `not_found` / `This route does not exist.`; unsupported method on a known route: 405 `method_not_allowed` / `This method is not supported.` with HTTP Allow; both use empty fields. Errors in `GET /api/items` use the same storage/internal envelope. Rejected Host/Origin/validation/media/size/parse requests insert zero records. An items-API `storage_unavailable` 503 also guarantees no inserted record: issue it only when the write transaction never began or its rollback is confirmed. If commit or rollback cannot be confirmed, do not report that definite-rejection 503. A transport failure, timeout or unexpected 500 can leave commit outcome unknown, including a commit followed by response-construction failure; those outcomes do not guarantee an unchanged database. Follow the reconciliation rule below even when the server returned a parseable 500 envelope. Retry timing is user-controlled; there is no automatic POST retry and no idempotency key contract.

## Boundary and failure expectations

After trimming, `""`, ASCII-only whitespace and combinations of the listed non-ASCII trim characters fail. One scalar and 80 scalars succeed; 81 fail. Surrounding trim characters do not count toward 80; interior ones do. Test both precomposed and combining text, astral symbols and markup-looking text. A well-formed object with duplicate name values across separate requests creates distinct records; duplicate JSON property keys in one request are 400.

A single UI submission sends one POST while submit is disabled. After 201, refresh the list, show the stored ID once and announce success. If that refresh fails, acknowledge that the create succeeded and offer list refresh; do not resend POST. If response/commit is uncertain, preserve input, announce uncertainty, refresh the list first, then let the person inspect the latest list before deliberately choosing “Create another item”. Name matches cannot prove identity because duplicates are valid. If reconciliation GET fails, keep create disabled until refresh succeeds or the page is reloaded and its initial GET succeeds. Never claim the uncertain create failed or automatically repeat it.

A controlled API failure demonstration is a QA browser interception of POST with synthetic 503 `storage_unavailable` before forwarding, or an equivalent isolated QA-only method approved in TC. No public failure toggle/endpoint in review. Ambiguous failure is a separate test: delay/drop response after a possible commit and demonstrate reconciliation. TC owns executable fault injection and reset implementation.

## Persistence, seed and identity

SQLite `items(id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL)` plus schema/seed metadata. On initialization of an uninitialized empty item store, insert “Sample notebook”, “Sample cable”, “Sample adapter” and the initialized marker in one transaction. Generate distinct IDs server-side and ordered timestamps; preserve those values thereafter. A nonempty store is never reseeded. An initialized store, even if empty from an isolated QA fixture operation, is never reseeded on ordinary restart. Seed/schema setup is a startup operation; GET is read-only. Reset exists only as an operator action in QA, not an API route. Record the fixture snapshot's IDs, names, times and SHA-256 in independent evidence. Use the same named data volume across restarts; no acknowledged create may disappear in the demonstrated process/container restart.

## Operational endpoints

These results apply only after Host and present-Origin admission; denied requests do not run readiness/storage probes. Health clients must send an admitted Host and may omit Origin.

| Endpoint | Success | Failure / contract |
|---|---|---|
| `GET /healthz` | 200 `{"status":"ok"}` | Process liveness only; does not assert database readiness. |
| `GET /readyz` | 200 `{"status":"ready"}` | 503 `{"status":"not_ready"}` until initialization complete, expected schema present and a read plus rolled-back write probe succeeds within 5 s. Never insert a persisted probe item. |
| `GET /api/version` | 200 object below | Immutable build metadata; no credentials, host paths, environment dump or inferred digest. Startup fails readiness if required identity is absent. |

```json
{"source_commit":"0123456789abcdef0123456789abcdef01234567","build_id":"synthetic-example-build","contract_version":"1","schema_version":1}
```

Version object has only these four required properties. `source_commit` is the full lowercase 40-hex commit compiled into the image, `build_id` is a nonempty non-secret identifier tied to the build record, `contract_version` is string `1`, `schema_version` is integer 1. The example is not an actual build. Actual OCI manifest digest, config digest, platform, archive SHA-256 and deployed configuration belong in the external deployment manifest; `/api/version` alone cannot prove which image is running.
