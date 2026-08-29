"""Dishka Redis client provider."""

from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from redis.asyncio.client import Redis

from bira_core.redis import make_redis_client


class RedisProvider(Provider):
    """Redis Provider."""

    scope = Scope.APP

    @provide
    async def redis(self, redis_url: str) -> AsyncIterable[Redis]:
        """Redis."""
        client = make_redis_client(redis_url)
        yield client
        await client.aclose()
