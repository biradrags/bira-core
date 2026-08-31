from typing import Self

import pytest
from redis.exceptions import RedisError

from bira_core.protect.rate_limit import RateLimitBackendUnavailable, RateLimiter


class BrokenRedis:
    def pipeline(self, transaction: bool = True) -> Self:
        return self

    async def __aenter__(self) -> Self:
        raise RedisError("down")

    async def __aexit__(self, *exc: object) -> None:
        return None


def _limiter(clock, *, fail_open: bool = True) -> RateLimiter:
    return RateLimiter(BrokenRedis(), fail_open=fail_open, clock=clock)  # type: ignore[arg-type]


async def test_fallback_window_resets_after_window_elapses() -> None:
    now = 0.0
    limiter = _limiter(lambda: now)

    assert await limiter.allow("k", limit=1, window_s=1) is True
    assert await limiter.allow("k", limit=1, window_s=1) is False

    now += 2
    assert await limiter.allow("k", limit=1, window_s=1) is True


async def test_fallback_counts_within_window() -> None:
    limiter = _limiter(lambda: 100.0)

    assert await limiter.allow("k", limit=2, window_s=60) is True
    assert await limiter.allow("k", limit=2, window_s=60) is True
    assert await limiter.allow("k", limit=2, window_s=60) is False


async def test_fail_closed_raises_instead_of_counting() -> None:
    limiter = _limiter(lambda: 0.0, fail_open=False)

    with pytest.raises(RateLimitBackendUnavailable):
        await limiter.allow("k", limit=1, window_s=1)
