from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta


class ChatRateLimiter:
    def __init__(self, limit: int = 30, window_seconds: int = 60):
        self.limit = limit
        self.window = timedelta(seconds=window_seconds)
        self._requests: dict[str, deque[datetime]] = defaultdict(deque)

    def allow(self, key: str) -> tuple[bool, int]:
        now = datetime.now(UTC)
        requests = self._requests[key]
        while requests and now - requests[0] >= self.window:
            requests.popleft()
        if len(requests) >= self.limit:
            retry_after = max(1, int((self.window - (now - requests[0])).total_seconds()))
            return False, retry_after
        requests.append(now)
        return True, 0
