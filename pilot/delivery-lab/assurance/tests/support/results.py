"""Conservative result classification. The evidence bundle remains authoritative."""
def classify(exit_code, report, collected, attempt_id):
    if not report or report.get("attempt_id") != attempt_id:
        return "UNKNOWN"
    results = report.get("results", [])
    classes = {r.get("classification") for r in results if r.get("outcome") == "failed"}
    if "FAIL" in classes:
        return "FAIL"
    if "UNAVAILABLE" in classes:
        return "UNAVAILABLE"
    called = [r for r in results if r.get("phase") == "call"]
    if exit_code != 0 or not collected or report.get("collected") != len(collected):
        return "UNKNOWN"
    if len(set(collected)) != len(collected) or sorted(r["id"] for r in called) != sorted(collected):
        return "UNKNOWN"
    if any(r["outcome"] != "passed" for r in results):
        return "UNKNOWN"
    return "PASS"
