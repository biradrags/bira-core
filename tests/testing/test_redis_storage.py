import pytest
from aiogram.fsm.storage.base import StorageKey
from redis.asyncio import Redis

from bira_core.testing.redis import redis_storage

REDIS_URL = "redis://localhost:6399/0"
PREFIX = "bira_core_test_fsm"


async def test_storage_uses_destiny_and_cleans_prefix() -> None:
    key = StorageKey(bot_id=1, chat_id=2, user_id=3, destiny="aiogd:stack")

    async with redis_storage(REDIS_URL, prefix=PREFIX) as storage:
        await storage.set_state(key, "SG:main")
        assert await storage.get_state(key) == "SG:main"
        default_key = StorageKey(bot_id=1, chat_id=2, user_id=3)
        assert await storage.get_state(default_key) is None

    probe = Redis.from_url(REDIS_URL)
    assert [k async for k in probe.scan_iter(match=f"{PREFIX}:*")] == []
    await probe.aclose()


async def test_unreachable_redis_raises() -> None:
    with pytest.raises(RuntimeError, match="Redis unavailable"):
        async with redis_storage("redis://localhost:1/0", prefix=PREFIX):
            pass
