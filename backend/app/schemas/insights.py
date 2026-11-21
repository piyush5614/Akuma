from decimal import Decimal

from pydantic import Field

from .common import APIModel


class SeasonalityMonth(APIModel):
    month: int = Field(ge=1, le=12)
    price_index: Decimal
    median_modal_price_inr: Decimal


class Seasonality(APIModel):
    crop_id: str
    months: list[SeasonalityMonth]
    best_months: list[int]
    worst_months: list[int]


class CropProfit(APIModel):
    crop_id: str
    price_range_inr_per_quintal: tuple[Decimal, Decimal]
    yield_range_quintal_per_acre: tuple[Decimal, Decimal]
    cost_inr_per_acre: Decimal
    risk_adjusted_midpoint_inr_per_acre: Decimal
    water_fit: str = Field(pattern="^(low|medium|high)$")
    herd_warning: bool
    source: str


class NextCropRequest(APIModel):
    category: str = Field(pattern="^(vegetable|grain|fruit)$")
    crop_history: list[str] = Field(default_factory=list, max_length=20)
    water_availability: str = Field(default="medium", pattern="^(low|medium|high)$")


class NextCropSuggestion(APIModel):
    crop: CropProfit
    reason: str
    reasons: list[str]


class Backtest(APIModel):
    crop_id: str
    window_days: int
    rule_hit_rate: Decimal
    baseline_hit_rate: Decimal
    sample_count: int
    measured_only: bool = True
