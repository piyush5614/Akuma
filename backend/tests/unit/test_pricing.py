from decimal import Decimal

from app.services.pricing import calculate_costs


def test_net_price_math():
    costs = calculate_costs(Decimal(2400), Decimal(10), Decimal(2), Decimal("1.3"), Decimal("0.60"), Decimal("0.01"), Decimal("0.02"))
    assert costs["road_km"] == Decimal("13.00")
    assert costs["transport_inr"] == Decimal("7.80")
    assert costs["fee_inr"] == Decimal("24.00")
    assert costs["shrinkage_inr"] == Decimal("48.00")
    assert costs["net_per_quintal_inr"] == Decimal("2320.20")
    assert costs["total_net_inr"] == Decimal("4640.40")
