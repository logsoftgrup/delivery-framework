# Delivery Lab API contract — v1

Normative for B1/B2/T1; operations support T2/O1/O2. Same-origin HTTP JSON on the loopback-bound service. Examples are synthetic. All JSON responses use `application/json`; APIs and HTML use `Cache-Control: no-store`. No pagination, filtering, update or delete route. No application authentication; host access controls in [runbook](runbook.md) are required. No wildcard CORS; accept create only as JSON and reject cross-origin browser requests.

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

Process in this order; return only the first error in the table, with no database changes. No silent string conversion. A JSON string containing an unpaired surrogate is a field validation error. Input must be valid UTF-8; duplicate object keys, NaN/Infinity and empty bodies count as malformed JSON. Maximum request body is 16,384 UTF-8 bytes before parsing (including whitespace); do not use a byte limit as the name length rule.

Trim only these code points from both ends, repeatedly: U+0009–U+000D, U+0020, U+0085, U+00A0, U+1680, U+2000–U+200A, U+2028, U+2029, U+202F, U+205F, U+3000. This explicit set is stable regardless of runtime Unicode version. U+200B and U+FEFF are not trimmed. Preserve interior whitespace and every other scalar, including combining marks, non-Latin and astral characters; no normalization, case folding or grapheme-based count. After trimming, count Unicode scalar code points: an astral symbol counts as one; `e` plus a combining accent counts as two. UI must use the same set and count; JavaScript string length/HTML maxlength alone are insufficient. Accepted names, including control/markup-looking characters, are rendered as text, with line wrapping and no HTML interpretation.

Every failure body has exactly this envelope; `fields` is empty for non-field errors:

```json
{"error":{"code":"validation_error","message":"Check the request fields.","fields":[{"field":"name","code":"name_length","message":"Enter 1–80 characters after trimming surrounding whitespace."}]}}
```

Envelope: object with only `error`; error contains string `code`, string `message`, array `fields`; each field entry contains only string `field`, `code`, `message`. For validation, one entry only. Property order is immaterial. Never echo submitted names, internal exceptions, SQL or paths in errors.

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
| Storage not ready, locked beyond 5 seconds, or transaction rolled back | 503 | `storage_unavailable` / `Items are temporarily unavailable. Try again.` | empty |
| Unexpected failure | 500 | `internal_error` / `Something went wrong. Check the list before trying again.` | empty |

Unknown route: 404 `not_found` / `This route does not exist.`; unsupported method on a known route: 405 `method_not_allowed` / `This method is not supported.` with HTTP Allow; both use empty fields. Errors in GET use the same storage/internal envelope. Rejected validation/media/size/parse requests and explicit rolled-back 503 responses insert zero records. A transport failure, timeout or unexpected 500 can leave commit outcome unknown; see recovery below. Retry timing is user-controlled; there is no automatic POST retry and no idempotency key contract.

## Boundary and failure expectations

After trimming, `""`, ASCII-only whitespace and combinations of the listed non-ASCII trim characters fail. One scalar and 80 scalars succeed; 81 fail. Surrounding trim characters do not count toward 80; interior ones do. Test both precomposed and combining text, astral symbols and markup-looking text. A well-formed object with duplicate name values across separate requests creates distinct records; duplicate JSON property keys in one request are 400.

A single UI submission sends one POST while submit is disabled. After 201, refresh the list, show the stored ID once and announce success. If that refresh fails, acknowledge that the create succeeded and offer list refresh; do not resend POST. If response/commit is uncertain, preserve input, announce uncertainty, refresh the list first, then let the person inspect the latest list before deliberately choosing “Create another item”. Name matches cannot prove identity because duplicates are valid. If reconciliation GET fails, keep create disabled until refresh succeeds or the page is reloaded and its initial GET succeeds. Never claim the uncertain create failed or automatically repeat it.

A controlled API failure demonstration is a QA browser interception of POST with synthetic 503 `storage_unavailable` before forwarding, or an equivalent isolated QA-only method approved in TC. No public failure toggle/endpoint in review. Ambiguous failure is a separate test: delay/drop response after a possible commit and demonstrate reconciliation. TC owns executable fault injection and reset implementation.

## Persistence, seed and identity

SQLite `items(id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL)` plus schema/seed metadata. On initialization of an uninitialized empty item store, insert “Sample notebook”, “Sample cable”, “Sample adapter” and the initialized marker in one transaction. Generate distinct IDs server-side and ordered timestamps; preserve those values thereafter. A nonempty store is never reseeded. An initialized store, even if empty from an isolated QA fixture operation, is never reseeded on ordinary restart. Seed/schema setup is a startup operation; GET is read-only. Reset exists only as an operator action in QA, not an API route. Record the fixture snapshot's IDs, names, times and SHA-256 in independent evidence. Use the same named data volume across restarts; no acknowledged create may disappear in the demonstrated process/container restart.

## Operational endpoints

| Endpoint | Success | Failure / contract |
|---|---|---|
| `GET /healthz` | 200 `{"status":"ok"}` | Process liveness only; does not assert database readiness. |
| `GET /readyz` | 200 `{"status":"ready"}` | 503 `{"status":"not_ready"}` until initialization complete, expected schema present and a read plus rolled-back write probe succeeds within 5 s. Never insert a persisted probe item. |
| `GET /api/version` | 200 object below | Immutable build metadata; no credentials, host paths, environment dump or inferred digest. Startup fails readiness if required identity is absent. |

```json
{"source_commit":"0123456789abcdef0123456789abcdef01234567","build_id":"synthetic-example-build","contract_version":"1","schema_version":1}
```

Version object has only these four required properties. `source_commit` is the full lowercase 40-hex commit compiled into the image, `build_id` is a nonempty non-secret identifier tied to the build record, `contract_version` is string `1`, `schema_version` is integer 1. The example is not an actual build. Actual OCI manifest digest, config digest, platform, archive SHA-256 and deployed configuration belong in the external deployment manifest; `/api/version` alone cannot prove which image is running.
