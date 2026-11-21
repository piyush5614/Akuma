from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import yaml
from pydantic import BaseModel, Field

from ..core.config import settings
from .freshness import freshness
from .pricing import calculate_costs, haversine_km
from .sell_wait import decide
from .store import CROPS, MANDIS, report_date


class ToolContext(BaseModel):
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    crop_id: str | None = None
    quantity_quintal: Decimal | None = Field(default=None, gt=0, le=10000)


class BestMandisArgs(BaseModel):
    crop: str
    quantity_quintal: Decimal = Field(default=Decimal(1), gt=0, le=10000)
    radius_km: float = Field(default=300, ge=5, le=300)


class MandiPriceArgs(BaseModel):
    crop: str
    mandi: str


class TrendArgs(MandiPriceArgs):
    days: int = Field(default=7, ge=1, le=60)


class CropArgs(BaseModel):
    crop: str


class CropSuggestionsArgs(BaseModel):
    water_availability: str = Field(default="medium", pattern="^(low|medium|high)$")


class TermArgs(BaseModel):
    term: str = Field(min_length=1, max_length=80)


class ToolDefinition:
    def __init__(self, name: str, arguments: type[BaseModel], handler: Callable[[BaseModel, ToolContext], dict[str, Any]]):
        self.name = name
        self.arguments = arguments
        self.handler = handler


def _crop(crop_id: str) -> dict[str, Any]:
    crop = next((item for item in CROPS if item["id"] == crop_id), None)
    if crop is None:
        raise ValueError("Unknown crop")
    return crop


def _mandi(mandi_id: str) -> dict[str, Any]:
    mandi = next((item for item in MANDIS if item["id"] == mandi_id), None)
    if mandi is None:
        raise ValueError("Unknown mandi")
    return mandi


def _find_best(args: BestMandisArgs, context: ToolContext) -> dict[str, Any]:
    if context.lat is None or context.lng is None:
        raise ValueError("Location is required to find nearby mandis")
    crop = _crop(args.crop)
    shrinkage = {"onion": Decimal("0.02"), "tomato": Decimal("0.03"), "soybean": Decimal("0.01")}.get(args.crop, Decimal("0.02"))
    rows = []
    for mandi in MANDIS:
        distance = haversine_km(context.lat, context.lng, mandi["location"]["lat"], mandi["location"]["lng"])
        view_freshness = freshness(report_date(mandi))
        if distance <= Decimal(str(args.radius_km)) and view_freshness in {"FRESH", "STALE"}:
            costs = calculate_costs(mandi["prices"][args.crop], distance, args.quantity_quintal, settings.road_factor, settings.transport_rate, settings.fee_pct, shrinkage)
            rows.append({"mandi_id": mandi["id"], "name": mandi["name"], "distance_km": str(distance), "freshness": view_freshness, "modal_price_inr": str(mandi["prices"][args.crop]), "costs": {key: str(value) for key, value in costs.items()}})
    rows.sort(key=lambda row: (-Decimal(row["costs"]["total_net_inr"]), Decimal(row["distance_km"])))
    return {"crop_id": crop["id"], "quantity_quintal": str(args.quantity_quintal), "recommendations": rows[:5], "is_demo": True, "data_as_of": date.today().isoformat()}


def _get_price(args: MandiPriceArgs, _: ToolContext) -> dict[str, Any]:
    mandi = _mandi(args.mandi)
    crop = _crop(args.crop)
    return {"crop_id": crop["id"], "mandi_id": mandi["id"], "mandi_name": mandi["name"], "modal_price_inr": str(mandi["prices"][args.crop]), "freshness": freshness(report_date(mandi)), "reported_on": report_date(mandi).isoformat(), "is_demo": True}


def _get_trend(args: TrendArgs, context: ToolContext) -> dict[str, Any]:
    mandi = _mandi(args.mandi)
    _crop(args.crop)
    base = mandi["prices"][args.crop]
    return {"crop_id": args.crop, "mandi_id": mandi["id"], "points": [{"reported_on": (date.today() - timedelta(days=offset)).isoformat(), "modal_price_inr": str(base + Decimal(offset * 5))} for offset in range(args.days)], "is_demo": True}


def _get_sell_wait(args: CropArgs, _: ToolContext) -> dict[str, Any]:
    crop = _crop(args.crop)
    return decide(Decimal(0), Decimal(0), Decimal(0), crop["perishability"] == "high") | {"is_demo": True, "data_as_of": date.today().isoformat()}


def _get_seasonality(args: CropArgs, _: ToolContext) -> dict[str, Any]:
    crop = _crop(args.crop)
    base = MANDIS[0]["prices"].get(crop["id"], Decimal(0))
    return {"crop_id": crop["id"], "months": [{"month": month, "price_index": "1.00", "median_modal_price_inr": str(base)} for month in range(1, 13)], "best_months": [1, 2], "worst_months": [7, 8], "is_demo": True}


def _get_crop_suggestions(args: CropSuggestionsArgs, _: ToolContext) -> dict[str, Any]:
    return {"water_availability": args.water_availability, "crops": [{"crop_id": crop["id"], "risk_adjusted_midpoint_inr_per_acre": "100000", "price_range_inr_per_quintal": ["1800", "3200"], "source": "DEMO"} for crop in CROPS], "is_demo": True}


def _load_kb(language: str) -> list[dict[str, Any]]:
    path = __file__.replace("chat_tools.py", f"chat/kb/{language}.yaml")
    with open(path, encoding="utf-8") as file:
        return yaml.safe_load(file)["entries"]


def _knowledge(args: TermArgs, context: ToolContext) -> dict[str, Any]:
    query = args.term.lower()
    entries = _load_kb(getattr(context, "language", "en") if hasattr(context, "language") else "en")
    match = next((entry for entry in entries if query in " ".join(entry["keywords"]).lower()), None)
    return {"term": args.term, "text": match["text"] if match else None, "found": match is not None, "is_demo": True}


TOOLS = {
    "find_best_mandis": ToolDefinition("find_best_mandis", BestMandisArgs, _find_best),
    "get_mandi_price": ToolDefinition("get_mandi_price", MandiPriceArgs, _get_price),
    "get_price_trend": ToolDefinition("get_price_trend", TrendArgs, _get_trend),
    "get_sell_or_wait": ToolDefinition("get_sell_or_wait", CropArgs, _get_sell_wait),
    "get_seasonality": ToolDefinition("get_seasonality", CropArgs, _get_seasonality),
    "get_crop_suggestions": ToolDefinition("get_crop_suggestions", CropSuggestionsArgs, _get_crop_suggestions),
    "explain_term": ToolDefinition("explain_term", TermArgs, _knowledge),
    "app_help": ToolDefinition("app_help", TermArgs, _knowledge),
}


class ToolRegistry:
    def __init__(self, definitions: dict[str, ToolDefinition] | None = None):
        self.definitions = definitions or TOOLS

    def invoke(self, name: str, arguments: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        definition = self.definitions.get(name)
        if definition is None:
            raise ValueError("Unknown chat tool")
        validated = definition.arguments.model_validate(arguments)
        return definition.handler(validated, context)

    def definitions_for_provider(self) -> list[dict[str, Any]]:
        return [{"name": definition.name, "parameters": definition.arguments.model_json_schema()} for definition in self.definitions.values()]
