"""In-memory flood guard for the webhook ingress layer."""

from __future__ import annotations

import time
from collections.abc import Callable


class TokenBucket:
    """Per-key token bucket with refill rate and capacity."""

    def __init__(self, capacity: float, refill_per_sec: float) -> None:
        """Set bucket capacity and tokens-per-second refill."""
        self._capacity = float(capacity)
        self._refill_per_sec = float(refill_per_sec)
        self._tokens = float(capacity)
        self._last = 0.0

    def try_consume(self, now: float, amount: float = 1.0) -> bool:
        """Consume tokens if available; refill since last call."""
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
    """L1 ingress limiter: per-key plus global token buckets."""

    def __init__(
        self,
        *,
        per_key_rate: float,
        per_key_burst: int,
        global_rate: float,
        global_burst: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Configure per-key and global rate/burst limits."""
        self._per_key = _PerKeyLimiter(per_key_burst, per_key_rate)
        self._global = TokenBucket(global_burst, global_rate)
        self._clock = clock

    def allow(self, key: str) -> bool:
        """Allow when both per-key and global buckets have tokens."""
        now = self._clock()
        if not self._per_key.allow(key, now):
            return False
        return self._global.try_consume(now)
