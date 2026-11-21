from decimal import Decimal

from .common import APIModel, Coordinates


class RegionPrice(APIModel):
    region_id: str
    name: str
    location: Coordinates
    average_modal_price_inr: Decimal | None
    mandi_count: int
    freshness: str
