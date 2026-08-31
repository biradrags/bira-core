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

    @property
    def last_used(self) -> float:
        """Timestamp of the last try_consume call."""
        return self._last

    def is_replenished(self) -> bool:
        """True when the bucket is back at full capacity."""
        return self._tokens >= self._capacity


class FloodGuard:
    """L1 ingress limiter: per-key plus global token buckets."""

    def __init__(
        self,
        *,
        per_key_rate: float,
        per_key_burst: int,
        global_rate: float,
        global_burst: int,
        max_keys: int = 10_000,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Configure per-key and global rate/burst limits plus key-table cap."""
        self._per_key = _PerKeyLimiter(per_key_burst, per_key_rate, max_keys=max_keys)
        self._global = TokenBucket(global_burst, global_rate)
        self._clock = clock

    def allow(self, key: str) -> bool:
        """Allow when both per-key and global buckets have tokens."""
        now = self._clock()
        if not self._per_key.allow(key, now):
            return False
        return self._global.try_consume(now)

    def tracked_keys(self) -> int:
        """Current size of the per-key table; for tests and health metrics."""
        return self._per_key.size


class _PerKeyLimiter:
    def __init__(
        self, capacity: float, refill_per_sec: float, *, max_keys: int
    ) -> None:
        self._capacity = capacity
        self._refill_per_sec = refill_per_sec
        self._max_keys = max_keys
        self._buckets: dict[str, TokenBucket] = {}

    @property
    def size(self) -> int:
        return len(self._buckets)

    def allow(self, key: str, now: float) -> bool:
        bucket = self._buckets.get(key)
        if bucket is None:
            # Без вытеснения таблица растёт на каждый новый ключ, а процесс на
            # Fly живёт неделями: флуд с разных аккаунтов = OOM того же бота.
            if len(self._buckets) >= self._max_keys:
                self._evict(now)
            bucket = TokenBucket(self._capacity, self._refill_per_sec)
            self._buckets[key] = bucket
        return bucket.try_consume(now)

    def _evict(self, now: float) -> None:
        replenished = [k for k, b in self._buckets.items() if b.is_replenished()]
        for key in replenished:
            del self._buckets[key]
        if len(self._buckets) < self._max_keys:
            return
        oldest = sorted(self._buckets, key=lambda k: self._buckets[k].last_used)
        for key in oldest[: len(self._buckets) // 2 or 1]:
            del self._buckets[key]
