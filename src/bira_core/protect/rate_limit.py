from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class RateLimitBackendUnavailable(Exception):
    pass


class RateLimiter:
    def __init__(self, redis: Redis, *, fail_open: bool) -> None:
        self._redis = redis
        self._fail_open = fail_open
        self._fallback: dict[str, int] = {}

    async def hit(self, key: str, *, limit: int, window_s: int) -> bool:
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


class UsageGate:
    def __init__(
        self,
        limiter: RateLimiter,
        *,
        limit: int,
        window_s: int,
        key_fn: Callable[..., str],
    ) -> None:
        self._limiter = limiter
        self._limit = limit
        self._window_s = window_s
        self._key_fn = key_fn

    async def check(self, *args: Any, **kwargs: Any) -> bool:
        key = self._key_fn(*args, **kwargs)
        return await self._limiter.hit(key, limit=self._limit, window_s=self._window_s)
