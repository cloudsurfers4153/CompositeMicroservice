import json
import os

import requests

# Target composite health endpoint; override via COMPOSITE_HEALTH_URL
COMPOSITE_HEALTH_URL = os.getenv(
    "COMPOSITE_HEALTH_URL",
    "https://compositemicroservice-608197196549.us-central1.run.app/composite/health",
)


def ping(request):
    """
    HTTP-triggered Cloud Function that probes the composite /health endpoint and
    returns the response (status + body). Minimal but verifies reachability.
    """
    try:
        resp = requests.get(COMPOSITE_HEALTH_URL, timeout=5)
        body_is_json = resp.headers.get("content-type", "").startswith("application/json")
        payload = {
            "target": COMPOSITE_HEALTH_URL,
            "status_code": resp.status_code,
            "body": resp.json() if body_is_json else resp.text,
        }
        return json.dumps(payload), resp.status_code, {"Content-Type": "application/json"}
    except Exception as exc:  # pragma: no cover - defensive path
        return (
            json.dumps({"target": COMPOSITE_HEALTH_URL, "error": str(exc)}),
            500,
            {"Content-Type": "application/json"},
        )
