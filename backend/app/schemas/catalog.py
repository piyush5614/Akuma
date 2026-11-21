from datetime import date
from decimal import Decimal

from pydantic import Field

from .common import APIModel, Coordinates, LocalizedText


class Crop(APIModel):
    id: str
    name: LocalizedText
    category: str = Field(pattern="^(vegetable|grain|fruit)$")
    unit: str = "quintal"
    perishability: str = Field(pattern="^(low|medium|high)$")


class Mandi(APIModel):
    id: str
    name: str
    district: str
    state: str = "Maharashtra"
    location: Coordinates
    approximate_location: bool = True
    freshness: str = Field(pattern="^(FRESH|STALE|OLD|NO_REPORT)$")
    latest_report_date: date | None = None
    modal_price_inr: Decimal | None = None


class TrendPoint(APIModel):
    reported_on: date
    modal_price_inr: Decimal
    arrivals_quintal: Decimal | None = None


class Trend(APIModel):
    mandi_id: str
    crop_id: str
    points: list[TrendPoint]
