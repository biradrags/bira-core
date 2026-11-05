"""aiogram RedisStorage for tests with the destiny key builder aiogram_dialog requires."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from redis.exceptions import ConnectionError as RedisConnectionError

from bira_core.redis.client import make_redis_client

__all__ = ["redis_storage"]


@asynccontextmanager
async def redis_storage(url: str, *, prefix: str) -> AsyncIterator[RedisStorage]:
    """Ping Redis (RuntimeError, not skip), yield destiny-keyed RedisStorage; drop `prefix:*` on exit."""
    client = make_redis_client(url)
    try:
        await client.ping()
    except (RedisConnectionError, OSError) as e:
        await client.aclose()
        msg = "Redis unavailable for tests: start it (make docker-up) or fix the URL"
        raise RuntimeError(msg) from e
    # без destiny aiogram_dialog схлопывает стек и контексты в один ключ
    key_builder = DefaultKeyBuilder(prefix=prefix, with_destiny=True)
    storage = RedisStorage(client, key_builder=key_builder)
    try:
        yield storage
    finally:
        keys = [key async for key in client.scan_iter(match=f"{prefix}:*", count=1000)]
        if keys:
            await client.delete(*keys)
        await storage.close()
