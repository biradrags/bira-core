"""In-memory and Redis rate limiters."""

from __future__ import annotations

import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class RateLimitBackendUnavailable(Exception):
    """Rate Limit Backend Unavailable."""


class RateLimiter:
    """Rate Limiter."""

    def __init__(self, redis: Redis, *, fail_open: bool) -> None:
        """Initialize instance."""
        self._redis = redis
        self._fail_open = fail_open
        self._fallback: dict[str, int] = {}

    async def allow(self, key: str, *, limit: int, window_s: int) -> bool:
        """Allow."""
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
            self._fallback[key] = self._fallback.get(key, 0) + 1
            return self._fallback[key] <= limit
