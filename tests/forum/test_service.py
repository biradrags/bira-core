from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.exceptions import TelegramBadRequest

from bira_core.forum import TOPIC_GONE_MARKERS, ForumTopics


class MemoryThreadStore:
    def __init__(self) -> None:
        self._data: dict[str, int] = {}

    async def get_thread_id(self, key: str) -> int | None:
        return self._data.get(key)

    async def set_thread_id(self, key: str, thread_id: int) -> None:
        self._data[key] = thread_id


@pytest.mark.asyncio
async def test_topic_gone_markers_union() -> None:
    assert "thread not found" in TOPIC_GONE_MARKERS
    assert "topic_deleted" in TOPIC_GONE_MARKERS
    assert "TOPIC_DELETED" in TOPIC_GONE_MARKERS
    assert "message thread not found" in TOPIC_GONE_MARKERS


@pytest.mark.asyncio
async def test_ensure_topic_creates_and_stores() -> None:
    bot = AsyncMock()
    bot.create_forum_topic.return_value.message_thread_id = 42
    store = MemoryThreadStore()
    forum = ForumTopics(bot, -1001, store)

    topic_id = await forum.ensure_topic("user:1", "Lead · test")

    assert topic_id == 42
    assert await store.get_thread_id("user:1") == 42
    bot.create_forum_topic.assert_awaited_once()


@pytest.mark.asyncio
async def test_ensure_topic_reuses_existing() -> None:
    bot = AsyncMock()
    store = MemoryThreadStore()
    await store.set_thread_id("user:1", 7)
    forum = ForumTopics(bot, -1001, store)

    topic_id = await forum.ensure_topic("user:1", "Lead · test")

    assert topic_id == 7
    bot.create_forum_topic.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_recovers_on_deleted_topic() -> None:
    bot = AsyncMock()
    store = MemoryThreadStore()
    await store.set_thread_id("user:1", 10)
    bot.send_message.side_effect = [
        TelegramBadRequest(method="sendMessage", message="thread not found"),
        MagicMock(message_id=99),
    ]
    bot.create_forum_topic.return_value.message_thread_id = 11
    forum = ForumTopics(bot, -1001, store)

    await forum.send("user:1", "hello", topic_name="Lead · test")

    assert await store.get_thread_id("user:1") == 11
    assert bot.create_forum_topic.await_count == 1
    assert bot.send_message.await_count == 2
