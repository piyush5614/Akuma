from decimal import Decimal

from pydantic import Field

from .catalog import Mandi
from .common import APIModel, Coordinates, LocalizedText


class RecommendRequest(APIModel):
    crop_id: str
    quantity_quintal: Decimal = Field(ge=Decimal("0.1"), le=Decimal("10000"))
    farmer_location: Coordinates
    radius_km: float = Field(default=50, ge=5, le=300)


class CostBreakdown(APIModel):
    road_km: Decimal
    transport_inr: Decimal
    fee_inr: Decimal
    shrinkage_inr: Decimal
    net_per_quintal_inr: Decimal
    total_net_inr: Decimal


class MandiRecommendation(APIModel):
    mandi: Mandi
    distance_km: Decimal
    costs: CostBreakdown
    rank: int


class SellWait(APIModel):
    decision: str = Field(pattern="^(WAIT|SELL_NOW|UNSURE)$")
    reason_codes: list[str]
    reason: LocalizedText
    disclaimer: str = "Guidance, not a guarantee"


class RecommendResponse(APIModel):
    crop_id: str
    quantity_quintal: Decimal
    recommendations: list[MandiRecommendation]
    old_mandis: list[MandiRecommendation]
    sell_or_wait: SellWait
