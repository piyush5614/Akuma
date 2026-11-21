import os
from datetime import date, timedelta
from decimal import Decimal
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .core.config import settings
from .schemas import (
    AdminSettings,
    ChatFeedbackRequest,
    ChatFeedbackResponse,
    ChatRequest,
    ChatResponse,
    ChatStarter,
    Crop,
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    Mandi,
    Meta,
    NextCropRequest,
    NextCropSuggestion,
    RecommendRequest,
    RecommendResponse,
    RegionPrice,
    SaathiChatRequest,
    SaathiChatResponse,
    Trend,
)
from .services.chat import RuleBasedChatProvider
from .services.chat_orchestrator import ChatOrchestrator
from .services.chat_rate_limit import ChatRateLimiter
from .services.chat_sessions import ChatSessionStore
from .services.chat_tools import ToolContext
from .services.freshness import freshness
from .services.pricing import calculate_costs, haversine_km
from .services.sell_wait import decide
from .services.store import CROPS, MANDIS, as_of, report_date

app = FastAPI(title="FairFarm API", version=settings.api_version)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
bearer = HTTPBearer(auto_error=False)
chat_provider = RuleBasedChatProvider()
saathi_orchestrator = ChatOrchestrator()
chat_sessions = ChatSessionStore()
chat_rate_limiter = ChatRateLimiter()
chat_feedback: list[dict[str, str | None]] = []
saathi_events: list[dict[str, object]] = []
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


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=ErrorResponse(code="VALIDATION_ERROR", message="Request validation failed", details={"errors": exc.errors()}).model_dump(mode="json"))


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
    result = [_crop_profit_row(crop, water_availability) for crop in CROPS]
    return envelope(result)


def _crop_profit_row(crop: dict, water_availability: str) -> dict:
    water_need = {"vegetable": "medium", "grain": "low", "fruit": "high"}[crop["category"]]
    fit = "high" if water_need == water_availability or water_availability == "high" else "medium" if water_availability == "medium" else "low"
    midpoint = {"high": Decimal(125000), "medium": Decimal(105000), "low": Decimal(85000)}[fit]
    return {"crop_id": crop["id"], "price_range_inr_per_quintal": [Decimal(1800), Decimal(3200)], "yield_range_quintal_per_acre": [Decimal(40), Decimal(80)], "cost_inr_per_acre": Decimal(70000), "risk_adjusted_midpoint_inr_per_acre": midpoint, "water_fit": fit, "herd_warning": False, "source": "DEMO"}


@app.post("/api/v1/insights/next-crops")
def next_crops(request: NextCropRequest):
    history = set(request.crop_history)
    candidates = [crop for crop in CROPS if crop["category"] == request.category and crop["id"] not in history]
    suggestions = []
    for crop in candidates:
        profit = _crop_profit_row(crop, request.water_availability)
        reasons = [
            f"Fits your {request.category} preference",
            f"Water fit is {profit['water_fit']} for your stated availability",
        ]
        if history:
            reasons.append("Keeps your current crop experience in the same category")
        suggestions.append(NextCropSuggestion(crop=profit, reason="; ".join(reasons), reasons=reasons))
    suggestions.sort(key=lambda item: (-item.crop.risk_adjusted_midpoint_inr_per_acre, item.crop.crop_id))
    return envelope(suggestions[:5])


@app.get("/api/v1/insights/backtest")
def backtest(crop_id: str):
    return envelope({"crop_id": crop_id, "window_days": 365, "rule_hit_rate": Decimal("0.0"), "baseline_hit_rate": Decimal("0.0"), "sample_count": 0, "measured_only": True})


@app.get("/api/v1/regions/prices")
def regions(crop_id: str):
    result = [RegionPrice(region_id=mandi["id"], name=mandi["district"], location=mandi["location"], average_modal_price_inr=mandi["prices"].get(crop_id), mandi_count=1, freshness=freshness(report_date(mandi))) for mandi in MANDIS]
    return envelope(result)


@app.post("/api/v1/chat")
def chat(request: SaathiChatRequest | ChatRequest, http_request: Request):
    if isinstance(request, ChatRequest):
        return envelope(ChatResponse(**chat_provider.answer(request.message, request.language)))

    client_key = request.client.device_id or (http_request.client.host if http_request.client else "unknown")
    allowed, retry_after = chat_rate_limiter.allow(client_key)
    if not allowed:
        response = error("RATE_LIMITED", "Too many chat requests", {"retry_after_seconds": retry_after})
        response.headers["Retry-After"] = str(retry_after)
        return response

    session_id, stored = chat_sessions.start_or_get(request.session_id)
    context = request.context.model_copy(
        update={
            "crop_id": request.context.crop_id or stored.get("crop_id"),
            "quantity_quintal": request.context.quantity_quintal or stored.get("quantity_quintal"),
            "last_recommendation_id": request.context.last_recommendation_id or stored.get("last_recommendation_id"),
        }
    )
    result = saathi_orchestrator.answer(
        request.message,
        ToolContext(lat=context.lat, lng=context.lng, crop_id=context.crop_id, quantity_quintal=context.quantity_quintal),
        request.ui_language,
    )
    chat_sessions.update(
        session_id,
        crop_id=context.crop_id,
        quantity_quintal=context.quantity_quintal,
        last_recommendation_id=context.last_recommendation_id,
    )
    request_id = http_request.headers.get("X-Request-ID") or os.urandom(8).hex()
    saathi_events.append(
        {
            "request_id": request_id,
            "language": result.language,
            "intent": result.intent,
            "fallback_used": result.fallback_used,
            "grounded": result.grounded,
            "message": saathi_orchestrator.redact_for_log(request.message),
        }
    )
    response = SaathiChatResponse(
        session_id=session_id,
        reply={"text": result.text, "speak_text": result.text, "language": result.language, "script": result.script},
        cards=[],
        chips=["Show today's price", "Should I sell now?"],
        meta={
            "intent": result.intent,
            "tools_used": list(result.tools_used),
            "data_as_of": as_of().isoformat(),
            "is_demo": result.is_demo,
            "confidence": 0.9 if result.grounded else 0.4,
            "grounded": result.grounded,
            "fallback_used": result.fallback_used,
            "request_id": request_id,
        },
    )
    return envelope(response)


@app.get("/api/v1/chat/starters")
def chat_starters(lang: str = Query("en", pattern="^(en|mr|hi)$")):
    starters = {
        "en": [
            ChatStarter(label="Best nearby mandi", message="Which nearby mandi gives the best net return?"),
            ChatStarter(label="Today's price", message="What is today's onion price?"),
            ChatStarter(label="Sell or wait", message="Should I sell my onion now or wait?"),
            ChatStarter(label="Explain net profit", message="What does net profit mean?"),
        ],
        "mr": [
            ChatStarter(label="जवळची चांगली मंडी", message="जवळच्या कोणत्या मंडीत चांगला निव्वळ परतावा मिळेल?"),
            ChatStarter(label="आजचा भाव", message="आज कांद्याचा भाव किती आहे?"),
            ChatStarter(label="विकू की थांबू", message="कांदा आता विकू का थांबू?"),
            ChatStarter(label="निव्वळ नफा", message="निव्वळ नफा म्हणजे काय?"),
        ],
        "hi": [
            ChatStarter(label="पास की अच्छी मंडी", message="पास की कौन सी मंडी अच्छा शुद्ध रिटर्न देगी?"),
            ChatStarter(label="आज का भाव", message="आज प्याज का भाव कितना है?"),
            ChatStarter(label="बेचें या रुकें", message="प्याज अभी बेचूं या रुकूं?"),
            ChatStarter(label="शुद्ध लाभ", message="शुद्ध लाभ का मतलब क्या है?"),
        ],
    }
    return envelope(starters[lang])


@app.post("/api/v1/chat/feedback")
def chat_feedback_endpoint(request: ChatFeedbackRequest):
    chat_feedback.append(request.model_dump())
    return envelope(ChatFeedbackResponse(accepted=True))


@app.get("/api/v1/admin/saathi/metrics")
def saathi_metrics(_=Depends(admin_required)):
    total = len(saathi_events)
    language_counts = {language: sum(event["language"] == language for event in saathi_events) for language in ("en", "mr", "hi")}
    intent_counts: dict[str, int] = {}
    for event in saathi_events:
        intent = str(event["intent"])
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    unanswered = [event["message"] for event in saathi_events if event["intent"] == "unknown"][-20:]
    up = sum(item["rating"] == "up" for item in chat_feedback)
    down = sum(item["rating"] == "down" for item in chat_feedback)
    return envelope(
        {
            "messages_per_day": {"today": total},
            "messages_by_language": language_counts,
            "top_intents": intent_counts,
            "fallback_rate": round(sum(bool(event["fallback_used"]) for event in saathi_events) / total, 3) if total else 0,
            "refusal_rate": round(sum(event["intent"] in {"out_of_scope", "distress"} for event in saathi_events) / total, 3) if total else 0,
            "grounding_failure_count": sum(not bool(event["grounded"]) for event in saathi_events),
            "thumbs_ratio": {"up": up, "down": down},
            "unanswered_questions": unanswered,
            "provider": os.getenv("CHAT_PROVIDER", "rules"),
            "mode": os.getenv("CHAT_MODE", "auto"),
        }
    )


@app.post("/api/v1/admin/saathi/test")
def saathi_test(request: SaathiChatRequest, _=Depends(admin_required)):
    result = saathi_orchestrator.answer(
        request.message,
        ToolContext(
            lat=request.context.lat,
            lng=request.context.lng,
            crop_id=request.context.crop_id,
            quantity_quintal=request.context.quantity_quintal,
        ),
        request.ui_language,
    )
    return envelope(
        {
            "reply": result.text,
            "language": result.language,
            "intent": result.intent,
            "tools_used": list(result.tools_used),
            "tool_results": list(result.tool_results),
            "grounded": result.grounded,
            "fallback_used": result.fallback_used,
        }
    )


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
