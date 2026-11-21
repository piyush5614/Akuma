from decimal import ROUND_HALF_UP, Decimal
from math import asin, cos, radians, sin, sqrt


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> Decimal:
    radius = 6371.0
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    value = sin(delta_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lng / 2) ** 2
    return Decimal(str(2 * radius * asin(sqrt(value)))).quantize(Decimal("0.01"))


def calculate_costs(
    modal_price: Decimal,
    distance_km: Decimal,
    quantity_quintal: Decimal,
    road_factor: Decimal,
    transport_rate: Decimal,
    fee_pct: Decimal,
    shrinkage_pct: Decimal,
) -> dict[str, Decimal]:
    road_km = distance_km * road_factor
    transport = road_km * transport_rate
    fee = modal_price * fee_pct
    shrinkage = modal_price * shrinkage_pct
    net = modal_price - transport - fee - shrinkage
    return {
        "road_km": road_km.quantize(Decimal("0.01")),
        "transport_inr": transport.quantize(Decimal("0.01")),
        "fee_inr": fee.quantize(Decimal("0.01")),
        "shrinkage_inr": shrinkage.quantize(Decimal("0.01")),
        "net_per_quintal_inr": net.quantize(Decimal("0.01")),
        "total_net_inr": (net * quantity_quintal).quantize(Decimal("0.01")),
    }


def display_rupees(value: Decimal) -> int:
    return int(value.quantize(Decimal(1), rounding=ROUND_HALF_UP))
