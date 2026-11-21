from decimal import Decimal

from app.services.freshness import freshness
from app.services.sell_wait import decide


def test_freshness_bands():
    from datetime import date, timedelta
    today = date(2026, 11, 21)
    assert freshness(today, today) == "FRESH"
    assert freshness(today - timedelta(days=3), today) == "STALE"
    assert freshness(today - timedelta(days=8), today) == "OLD"
    assert freshness(None, today) == "NO_REPORT"


def test_wait_signal():
    result = decide(Decimal("1.2"), Decimal(-11), Decimal(0), False)
    assert result["decision"] == "WAIT"


def test_sell_signal():
    result = decide(Decimal("-1.2"), Decimal(0), Decimal(0), False)
    assert result["decision"] == "SELL_NOW"
