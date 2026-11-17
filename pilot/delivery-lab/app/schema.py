"""Published OpenAPI describes the accepted contract, including API-05 rejection."""


def openapi():
    def ref(name):
        return {"$ref": "#/components/schemas/" + name}

    def obj(properties, required=None):
        return {"type": "object", "additionalProperties": False, "properties": properties,
                "required": required if required is not None else list(properties)}

    text = {"type": "string"}
    schemas = {
        "CreateInput": obj({"name": text}),
        "Item": obj({
            "id": {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"},
            "name": {"type": "string", "minLength": 1, "maxLength": 80},
            "created_at": {"type": "string", "format": "date-time", "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$"},
        }),
        "ItemList": obj({"items": {"type": "array", "items": ref("Item")}}),
        "Error": obj({"error": obj({"code": text, "message": text, "fields": {
            "type": "array", "items": obj({"field": text, "code": text, "message": text})}})}),
        "Version": obj({"source_commit": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                        "build_id": {"type": "string", "minLength": 1},
                        "contract_version": {"const": "1"}, "schema_version": {"const": 1}}),
    }

    def response(description, schema):
        return {"description": description, "content": {"application/json": {"schema": schema}}}

    def operation(success, schema, description):
        responses = {str(success): response(description, schema)}
        for status, message in [(400, "invalid_json"), (403, "host_not_allowed or origin_not_allowed"),
                                (404, "not_found"), (405, "method_not_allowed"), (413, "request_too_large"),
                                (415, "unsupported_media_type"), (422, "validation_error"),
                                (500, "internal_error; commit may be uncertain"),
                                (503, "storage_unavailable; no inserted record")]:
            responses[str(status)] = response(message, ref("Error"))
        return {"responses": responses}

    create = operation(201, ref("Item"), "Committed item")
    create["requestBody"] = {"required": True, "content": {"application/json": {"schema": ref("CreateInput")}}}
    create["description"] = ("Trim the exact BASE-3 Unicode set, then require 1–80 Unicode scalars. "
                             "Unknown fields, nonstrings and unpaired surrogates are rejected. "
                             "Duplicate object keys and non-JSON constants are invalid JSON. "
                             "Admission precedence: Host, present Origin, 16384-byte size, media, UTF-8/JSON, fields, storage. "
                             "No automatic retry after an uncertain create. C0 deliberately violates only whitespace-only API validation; this contract remains unchanged.")
    ready = operation(200, obj({"status": {"const": "ready"}}), "Storage ready")
    ready["responses"]["503"] = response("Storage not ready", obj({"status": {"const": "not_ready"}}))
    return {"openapi": "3.1.0", "info": {"title": "Delivery Lab", "version": "1"},
            "paths": {"/api/items": {"get": operation(200, ref("ItemList"), "Ordered committed items"), "post": create},
                      "/api/version": {"get": operation(200, ref("Version"), "Immutable build identity")},
                      "/healthz": {"get": operation(200, obj({"status": {"const": "ok"}}), "Process liveness")},
                      "/readyz": {"get": ready}}, "components": {"schemas": schemas}}
