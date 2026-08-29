"""In-memory flood guard for the webhook ingress layer."""

from __future__ import annotations

import time
from collections.abc import Callable


class TokenBucket:
    """Token Bucket."""

    def __init__(self, capacity: float, refill_per_sec: float) -> None:
        """Initialize instance."""
        self._capacity = float(capacity)
        self._refill_per_sec = float(refill_per_sec)
        self._tokens = float(capacity)
        self._last = 0.0

    def try_consume(self, now: float, amount: float = 1.0) -> bool:
        """Try consume."""
        elapsed = now - self._last
        if elapsed > 0:
            self._tokens = min(
                self._capacity, self._tokens + elapsed * self._refill_per_sec
            )
        self._last = now
        if self._tokens >= amount:
            self._tokens -= amount
            return True
        return False


class _PerKeyLimiter:
    def __init__(self, capacity: float, refill_per_sec: float) -> None:
        self._capacity = capacity
        self._refill_per_sec = refill_per_sec
        self._buckets: dict[str, TokenBucket] = {}

    def allow(self, key: str, now: float) -> bool:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = TokenBucket(self._capacity, self._refill_per_sec)
            self._buckets[key] = bucket
        return bucket.try_consume(now)


class FloodGuard:
    """Flood Guard."""

    def __init__(
        self,
        *,
        per_key_rate: float,
        per_key_burst: int,
        global_rate: float,
        global_burst: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialize instance."""
        self._per_key = _PerKeyLimiter(per_key_burst, per_key_rate)
        self._global = TokenBucket(global_burst, global_rate)
        self._clock = clock

    def allow(self, key: str) -> bool:
        """Allow."""
        now = self._clock()
        if not self._per_key.allow(key, now):
            return False
        return self._global.try_consume(now)
