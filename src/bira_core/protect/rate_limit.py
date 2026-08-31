"""In-memory and Redis rate limiters."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

_MAX_FALLBACK_KEYS = 10_000


class RateLimitBackendUnavailable(Exception):
    """Raised when Redis backend is down and fail_open is disabled."""


class RateLimiter:
    """L2 Redis counter with optional in-process fallback on outage."""

    def __init__(
        self,
        redis: Redis,
        *,
        fail_open: bool,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Bind Redis client and whether to count locally when Redis is down."""
        self._redis = redis
        self._fail_open = fail_open
        self._clock = clock
        self._fallback: dict[str, tuple[int, float]] = {}

    async def allow(self, key: str, *, limit: int, window_s: int) -> bool:
        """Increment key in window; False when count exceeds limit."""
        try:
            async with self._redis.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.expire(key, window_s, nx=True)
                count, _ = await pipe.execute()
            return int(count) <= limit
        except (RedisError, ConnectionError, OSError) as exc:
            if not self._fail_open:
                raise RateLimitBackendUnavailable(str(exc)) from exc
            logger.warning("rate limit unavailable, fallback", extra={"key": key})
            return self._allow_locally(key, limit=limit, window_s=window_s)

    def _allow_locally(self, key: str, *, limit: int, window_s: int) -> bool:
        """Оконный счётчик в памяти: у каждой машины своё окно, общего нет."""
        now = self._clock()
        count, window_start = self._fallback.get(key, (0, now))
        if now - window_start >= window_s:
            count, window_start = 0, now
        count += 1
        if len(self._fallback) >= _MAX_FALLBACK_KEYS and key not in self._fallback:
            self._drop_expired(now, window_s)
        self._fallback[key] = (count, window_start)
        return count <= limit

    def _drop_expired(self, now: float, window_s: int) -> None:
        expired = [
            k for k, (_, start) in self._fallback.items() if now - start >= window_s
        ]
        for key in expired:
            del self._fallback[key]
