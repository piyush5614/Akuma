from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4


class ChatSessionStore:
    def __init__(self, ttl_minutes: int = 30):
        self.ttl = timedelta(minutes=ttl_minutes)
        self._sessions: dict[str, tuple[datetime, dict[str, object]]] = {}

    def start_or_get(self, session_id: str | None) -> tuple[str, dict[str, object]]:
        now = datetime.now(UTC)
        if session_id:
            item = self._sessions.get(session_id)
            if item and now - item[0] < self.ttl:
                return session_id, dict(item[1])
            self._sessions.pop(session_id, None)
        new_id = uuid4().hex
        self._sessions[new_id] = (now, {})
        return new_id, {}

    def update(self, session_id: str, *, crop_id: str | None, quantity_quintal: float | None, last_recommendation_id: str | None) -> None:
        self._sessions[session_id] = (
            datetime.now(UTC),
            {
                "crop_id": crop_id,
                "quantity_quintal": quantity_quintal,
                "last_recommendation_id": last_recommendation_id,
            },
        )

    def size(self) -> int:
        return len(self._sessions)
