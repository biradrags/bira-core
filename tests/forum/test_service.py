import sys
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.exceptions import TelegramBadRequest

from bira_core.forum import TOPIC_GONE_MARKERS, ForumTopics, is_topic_gone


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
async def test_ensure_topic_concurrent_single_create() -> None:
    import asyncio

    bot = AsyncMock()
    bot.create_forum_topic.return_value.message_thread_id = 42
    store = MemoryThreadStore()
    forum = ForumTopics(bot, -1001, store)

    await asyncio.gather(
        forum.send("user:1", "a", topic_name="Lead"),
        forum.send("user:1", "b", topic_name="Lead"),
    )

    bot.create_forum_topic.assert_awaited_once()


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


@pytest.mark.parametrize(
    "message",
    ["thread not found", "message thread not found", "TOPIC_DELETED", "topic_deleted"],
)
def test_is_topic_gone_covers_every_marker(message: str) -> None:
    exc = TelegramBadRequest(method="sendMessage", message=message)
    assert is_topic_gone(exc) is True


def test_is_topic_gone_false_for_other_errors() -> None:
    other = TelegramBadRequest(method="sendMessage", message="chat not found")
    assert is_topic_gone(other) is False
    assert is_topic_gone(RuntimeError("thread not found")) is False


def test_is_topic_gone_false_without_aiogram(monkeypatch: pytest.MonkeyPatch) -> None:
    """MAX-only установка без aiogram: не ImportError, а честное «не TG-топик»."""
    monkeypatch.setitem(sys.modules, "aiogram.exceptions", None)

    assert is_topic_gone(RuntimeError("thread not found")) is False


@pytest.mark.asyncio
async def test_chat_id_argument_overrides_constructor() -> None:
    """Форум свой на каждого владельца - чат приходит вызовом, не конструктором."""
    bot = AsyncMock()
    bot.create_forum_topic.return_value.message_thread_id = 5
    store = MemoryThreadStore()
    forum = ForumTopics(bot, -1001, store)

    await forum.send("owner:7:lead:1", "hi", topic_name="Lead", chat_id=-1002)

    assert bot.create_forum_topic.await_args.kwargs["chat_id"] == -1002
    assert bot.send_message.await_args.args[0] == -1002


@pytest.mark.asyncio
async def test_constructor_chat_used_when_argument_omitted() -> None:
    bot = AsyncMock()
    bot.create_forum_topic.return_value.message_thread_id = 5
    store = MemoryThreadStore()
    forum = ForumTopics(bot, -1001, store)

    await forum.send("lead:1", "hi", topic_name="Lead")

    assert bot.create_forum_topic.await_args.kwargs["chat_id"] == -1001
    assert bot.send_message.await_args.args[0] == -1001
