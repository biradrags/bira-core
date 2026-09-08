"""Dishka Redis client provider."""

from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from redis.asyncio.client import Redis

from bira_core.redis.client import make_redis_client


class RedisProvider(Provider):
    """Dishka APP-scoped Redis client from redis_url."""

    scope = Scope.APP

    @provide
    async def redis(self, redis_url: str) -> AsyncIterable[Redis]:
        """Yield connected client; aclose on shutdown."""
        client = make_redis_client(redis_url)
        yield client
        await client.aclose()
