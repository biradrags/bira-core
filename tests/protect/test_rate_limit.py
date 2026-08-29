import os

import pytest
from redis.asyncio import Redis

from bira_core.protect.rate_limit import RateLimitBackendUnavailable, RateLimiter

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6399/0")


@pytest.fixture
async def redis_client() -> Redis:
    client = Redis.from_url(REDIS_URL, decode_responses=True)
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


async def test_hit_limit(redis_client: Redis) -> None:
    limiter = RateLimiter(redis_client, fail_open=False)
    assert await limiter.allow("k", limit=2, window_s=60) is True
    assert await limiter.allow("k", limit=2, window_s=60) is True
    assert await limiter.allow("k", limit=2, window_s=60) is False


async def test_fail_open_fallback(redis_client: Redis) -> None:
    broken = Redis.from_url("redis://127.0.0.1:1/0", decode_responses=True)
    limiter = RateLimiter(broken, fail_open=True)
    assert await limiter.allow("k", limit=1, window_s=60) is True
    assert await limiter.allow("k", limit=1, window_s=60) is False


async def test_fail_closed_raises() -> None:
    broken = Redis.from_url("redis://127.0.0.1:1/0", decode_responses=True)
    limiter = RateLimiter(broken, fail_open=False)
    with pytest.raises(RateLimitBackendUnavailable):
        await limiter.allow("k", limit=1, window_s=60)
