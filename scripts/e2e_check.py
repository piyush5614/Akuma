"""Black-box smoke and consistency checks for a running FairFarm API."""

import json
import os
import time
import urllib.error
import urllib.request
from decimal import Decimal

BASE_URL = os.getenv("FAIRFARM_API_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")
ORIGIN = os.getenv("FAIRFARM_WEB_ORIGIN", "http://localhost:5173")


def parse_body(raw: bytes) -> dict:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def call(method: str, path: str, payload: dict | None = None, headers: dict | None = None) -> tuple[int, dict, dict]:
    request_headers = {"Accept": "application/json", **(headers or {})}
    body = None
    if payload is not None:
        body = json.dumps(payload).encode()
        request_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw = response.read()
            return response.status, parse_body(raw), dict(response.headers)
    except urllib.error.HTTPError as response:
        raw = response.read()
        return response.code, parse_body(raw), dict(response.headers)


def main() -> int:
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            if call("GET", "/health")[0] == 200:
                break
        except urllib.error.URLError:
            time.sleep(1)
    else:
        print(f"E2E blocked: API did not become healthy at {BASE_URL}")
        return 2

    checks: list[str] = []
    status, health, _ = call("GET", "/health")
    assert status == 200 and health["data"]["status"] == "ok"
    checks.append("health")
    for path in ("/meta", "/crops", "/mandis?crop_id=onion&lat=18.52&lng=73.86&radius_km=300", "/insights/seasonality?crop_id=onion", "/insights/crop-profit", "/insights/backtest?crop_id=onion", "/regions/prices?crop_id=onion"):
        status, body, _ = call("GET", path)
        assert status == 200 and {"data", "data_as_of", "is_demo"} <= body.keys()
        checks.append(path.split("?")[0])
    status, login, _ = call("POST", "/auth/login", {"email": "admin@example.com", "password": os.getenv("ADMIN_PASSWORD", "change-me")})
    assert status == 200
    token = login["data"]["access_token"]
    auth = {"Authorization": f"Bearer {token}"}
    for path in ("/admin/summary", "/admin/settings", "/admin/queries"):
        status, _, _ = call("GET", path, headers=auth)
        assert status == 200
        checks.append(path)
    status, _, _ = call("PUT", "/admin/settings", {"road_factor": "1.3", "transport_rate_per_quintal_km": "0.60", "fee_pct": "0.01", "shrinkage_pct_by_crop": {"onion": "0.02"}}, auth)
    assert status == 200
    for language in ("en", "mr", "hi"):
        status, body, _ = call("POST", "/chat", {"message": "Which mandi pays more?", "language": language})
        assert status == 200 and all(body["data"]["answer"].get(code) for code in ("en", "mr", "hi"))
    sample_totals = []
    for quantity in (1, 5, 10, 25, 100):
        status, body, _ = call("POST", "/recommend", {"crop_id": "onion", "quantity_quintal": quantity, "farmer_location": {"lat": 18.52, "lng": 73.86}, "radius_km": 300})
        assert status == 200
        recommendations = body["data"]["recommendations"]
        assert all(Decimal(recommendations[i]["costs"]["total_net_inr"]) >= Decimal(recommendations[i + 1]["costs"]["total_net_inr"]) for i in range(len(recommendations) - 1))
        sample_totals.append(Decimal(recommendations[0]["costs"]["total_net_inr"]))
    status, trend, _ = call("GET", "/mandis/pune/trend?crop_id=onion")
    assert status == 200 and trend["data"]["points"]
    status, _, headers = call("OPTIONS", "/crops", headers={"Origin": ORIGIN, "Access-Control-Request-Method": "GET"})
    assert status == 200 and "access-control-allow-origin" in {key.lower(): value for key, value in headers.items()}
    status, error_body, _ = call("POST", "/recommend", {"crop_id": "onion", "quantity_quintal": 0, "farmer_location": {"lat": 18.52, "lng": 73.86}})
    assert status == 422 and {"code", "message", "details"} <= error_body.keys()
    print(f"E2E passed: {len(checks)} endpoint groups, 5 recommendation samples, 3 languages, CORS, ranking, and validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
