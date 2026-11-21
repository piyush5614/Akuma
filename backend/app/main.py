import os
from datetime import date, timedelta
from decimal import Decimal
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .core.config import settings
from .schemas import (
    AdminSettings,
    ChatRequest,
    ChatResponse,
    Crop,
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    Mandi,
    Meta,
    RecommendRequest,
    RecommendResponse,
    RegionPrice,
    Trend,
)
from .services.chat import RuleBasedChatProvider
from .services.freshness import freshness
from .services.pricing import calculate_costs, haversine_km
from .services.sell_wait import decide
from .services.store import CROPS, MANDIS, as_of, report_date

app = FastAPI(title="FairFarm API", version=settings.api_version)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
bearer = HTTPBearer(auto_error=False)
chat_provider = RuleBasedChatProvider()
admin_settings = AdminSettings(road_factor=settings.road_factor, transport_rate_per_quintal_km=settings.transport_rate, fee_pct=settings.fee_pct, shrinkage_pct_by_crop={"onion": Decimal("0.02"), "tomato": Decimal("0.03"), "soybean": Decimal("0.01")})


def envelope(data):
    return {"data": data, "data_as_of": as_of(), "is_demo": settings.is_demo}


def error(code: str, message: str, details: dict | None = None) -> JSONResponse:
    body = ErrorResponse(code=code, message=message, details=details or {}).model_dump(mode="json")
    return JSONResponse(status_code=400, content=body)


def admin_required(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return payload


def mandi_view(mandi: dict, crop_id: str) -> dict:
    report = report_date(mandi)
    return Mandi(id=mandi["id"], name=mandi["name"], district=mandi["district"], state=mandi["state"], location=mandi["location"], freshness=freshness(report), latest_report_date=report, modal_price_inr=mandi["prices"].get(crop_id)).model_dump()


@app.exception_handler(HTTPException)
async def http_error_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=ErrorResponse(code="HTTP_ERROR", message=str(exc.detail), details={}).model_dump(mode="json"))


@app.get("/api/v1/health")
def health():
    return envelope({"status": "ok"})


@app.get("/api/v1/meta")
def meta():
    return envelope(Meta(api_version=settings.api_version, min_app_version=settings.min_app_version, is_demo=True))


@app.get("/api/v1/crops")
def crops():
    return envelope([Crop(**crop) for crop in CROPS])


@app.get("/api/v1/mandis")
def mandis(crop_id: str, lat: float = Query(..., ge=-90, le=90), lng: float = Query(..., ge=-180, le=180), radius_km: float = Query(50, ge=5, le=300)):
    if crop_id not in {crop["id"] for crop in CROPS}:
        return error("UNKNOWN_CROP", "Crop was not found", {"crop_id": crop_id})
    result = []
    for mandi in MANDIS:
        distance = haversine_km(lat, lng, mandi["location"]["lat"], mandi["location"]["lng"])
        if distance <= Decimal(str(radius_km)):
            result.append(mandi_view(mandi, crop_id))
    return envelope(result)


@app.post("/api/v1/recommend")
def recommend(request: RecommendRequest):
    crop = next((crop for crop in CROPS if crop["id"] == request.crop_id), None)
    if not crop:
        return error("UNKNOWN_CROP", "Crop was not found", {"crop_id": request.crop_id})
    ranked, old = [], []
    shrinkage = admin_settings.shrinkage_pct_by_crop.get(request.crop_id, Decimal("0.02"))
    for mandi in MANDIS:
        distance = haversine_km(request.farmer_location.lat, request.farmer_location.lng, mandi["location"]["lat"], mandi["location"]["lng"])
        if distance > Decimal(str(request.radius_km)):
            continue
        view = mandi_view(mandi, request.crop_id)
        costs = calculate_costs(mandi["prices"][request.crop_id], distance, request.quantity_quintal, admin_settings.road_factor, admin_settings.transport_rate_per_quintal_km, admin_settings.fee_pct, shrinkage)
        item = {"mandi": view, "distance_km": distance, "costs": costs, "rank": 0}
        (old if view["freshness"] == "OLD" else ranked).append(item)
    ranked.sort(key=lambda item: (-item["costs"]["total_net_inr"], item["distance_km"]))
    old.sort(key=lambda item: item["distance_km"])
    for index, item in enumerate(ranked, 1):
        item["rank"] = index
    for index, item in enumerate(old, 1):
        item["rank"] = index
    result = RecommendResponse(crop_id=request.crop_id, quantity_quintal=request.quantity_quintal, recommendations=ranked, old_mandis=old, sell_or_wait=decide(Decimal(0), Decimal(0), Decimal(0), crop["perishability"] == "high"))
    return envelope(result)


@app.get("/api/v1/mandis/{mandi_id}/trend")
def trend(mandi_id: str, crop_id: str, days: int = Query(7, ge=1, le=365)):
    mandi = next((item for item in MANDIS if item["id"] == mandi_id), None)
    if not mandi or crop_id not in mandi["prices"]:
        return error("NOT_FOUND", "Mandi or crop was not found")
    points = [{"reported_on": date.today() - timedelta(days=offset), "modal_price_inr": mandi["prices"][crop_id] + Decimal(str(offset * 5)), "arrivals_quintal": Decimal(100)} for offset in range(days)]
    return envelope(Trend(mandi_id=mandi_id, crop_id=crop_id, points=points))


@app.get("/api/v1/insights/seasonality")
def seasonality(crop_id: str):
    months = [{"month": month, "price_index": Decimal("1.00"), "median_modal_price_inr": MANDIS[0]["prices"].get(crop_id, Decimal(0))} for month in range(1, 13)]
    return envelope({"crop_id": crop_id, "months": months, "best_months": [1, 2], "worst_months": [7, 8]})


@app.get("/api/v1/insights/crop-profit")
def crop_profit(water_availability: str = Query("medium", pattern="^(low|medium|high)$")):
    result = [{"crop_id": crop["id"], "price_range_inr_per_quintal": [Decimal(1800), Decimal(3200)], "yield_range_quintal_per_acre": [Decimal(40), Decimal(80)], "cost_inr_per_acre": Decimal(70000), "risk_adjusted_midpoint_inr_per_acre": Decimal(100000), "water_fit": water_availability, "herd_warning": False, "source": "DEMO"} for crop in CROPS]
    return envelope(result)


@app.get("/api/v1/insights/backtest")
def backtest(crop_id: str):
    return envelope({"crop_id": crop_id, "window_days": 365, "rule_hit_rate": Decimal("0.0"), "baseline_hit_rate": Decimal("0.0"), "sample_count": 0, "measured_only": True})


@app.get("/api/v1/regions/prices")
def regions(crop_id: str):
    result = [RegionPrice(region_id=mandi["id"], name=mandi["district"], location=mandi["location"], average_modal_price_inr=mandi["prices"].get(crop_id), mandi_count=1, freshness=freshness(report_date(mandi))) for mandi in MANDIS]
    return envelope(result)


@app.post("/api/v1/chat")
def chat(request: ChatRequest):
    return envelope(ChatResponse(**chat_provider.answer(request.message, request.language)))


@app.post("/api/v1/auth/login")
def login(request: LoginRequest):
    if request.email != "admin@example.com" or request.password != os.getenv("ADMIN_PASSWORD", "change-me"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": request.email, "role": "admin"}, settings.jwt_secret, algorithm="HS256")
    return envelope(LoginResponse(access_token=token, expires_in_seconds=3600))


@app.get("/api/v1/admin/summary")
def admin_summary(_=Depends(admin_required)):
    return envelope({"mandi_count": len(MANDIS), "crop_count": len(CROPS), "report_count": len(MANDIS) * len(CROPS), "fresh_report_pct": Decimal("0.33"), "query_count": 0})


@app.get("/api/v1/admin/settings")
def get_settings(_=Depends(admin_required)):
    return envelope(admin_settings)


@app.put("/api/v1/admin/settings")
def update_settings(updated: AdminSettings, _=Depends(admin_required)):
    global admin_settings
    admin_settings = updated
    return envelope(admin_settings)


@app.post("/api/v1/admin/data/import")
async def import_data(file: UploadFile = File(...), _=Depends(admin_required)):
    content = await file.read()
    if not content:
        return error("EMPTY_IMPORT", "The uploaded CSV is empty")
    return envelope({"imported_records": max(0, len(content.splitlines()) - 1), "skipped_records": 0, "errors": []})


@app.get("/api/v1/admin/queries")
def queries(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), _=Depends(admin_required)):
    return envelope({"items": [], "total": 0})
