from datetime import UTC, datetime, timedelta

from app.services.chat_rate_limit import ChatRateLimiter
from app.services.chat_sessions import ChatSessionStore


def test_session_keeps_only_market_context():
    store = ChatSessionStore()
    session_id, _ = store.start_or_get(None)
    store.update(session_id, crop_id="onion", quantity_quintal=10, last_recommendation_id="rec-1")

    same_id, values = store.start_or_get(session_id)
    assert same_id == session_id
    assert values == {"crop_id": "onion", "quantity_quintal": 10, "last_recommendation_id": "rec-1"}


def test_expired_session_is_replaced():
    store = ChatSessionStore()
    session_id, _ = store.start_or_get(None)
    store._sessions[session_id] = (datetime.now(UTC) - timedelta(minutes=31), {"crop_id": "onion"})

    new_id, values = store.start_or_get(session_id)
    assert new_id != session_id
    assert values == {}


def test_rate_limiter_returns_retry_after():
    limiter = ChatRateLimiter(limit=1, window_seconds=60)
    assert limiter.allow("device")[0]
    allowed, retry_after = limiter.allow("device")
    assert not allowed
    assert retry_after > 0
