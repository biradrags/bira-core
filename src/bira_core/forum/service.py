"""Forum topic ensure/send with per-key locking."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)

TOPIC_GONE_MARKERS = frozenset(
    {
        "thread not found",
        "topic_deleted",
        "TOPIC_DELETED",
        "message thread not found",
    }
)


@runtime_checkable
class ThreadStore(Protocol):
    """Persist forum thread_id per logical key (DAO-backed in consumer)."""

    async def get_thread_id(self, key: str) -> int | None:
        """Return stored thread_id or None before first topic creation."""
        ...

    async def set_thread_id(self, key: str, thread_id: int) -> None:
        """Persist thread_id after ensure_topic creates or recreates a topic."""
        ...


def _is_topic_gone(exc: BaseException) -> bool:
    from aiogram.exceptions import TelegramBadRequest

    if not isinstance(exc, TelegramBadRequest):
        return False
    text = str(exc).lower()
    return any(marker.lower() in text for marker in TOPIC_GONE_MARKERS)


class ForumTopics:
    """Forum Topics."""

    def __init__(
        self,
        bot: Any,
        forum_chat_id: int,
        store: ThreadStore,
        *,
        call_timeout: float = 15,
    ) -> None:
        """Initialize instance."""
        self._bot = bot
        self._forum_chat_id = forum_chat_id
        self._store = store
        self._call_timeout = call_timeout
        self._locks: dict[str, asyncio.Lock] = {}

    async def ensure_topic(self, key: str, name: str) -> int:
        """Create topic once per key under per-key lock (concurrent-safe)."""
        topic_id = await self._store.get_thread_id(key)
        if topic_id is not None:
            return topic_id
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            topic_id = await self._store.get_thread_id(key)
            if topic_id is not None:
                return topic_id
            topic_id = await self._create_topic(name)
            await self._store.set_thread_id(key, topic_id)
            return topic_id

    async def send(
        self,
        key: str,
        text: str,
        *,
        topic_name: str,
        **kwargs: Any,
    ) -> Any:
        """Send to forum topic; recreate topic if Telegram reports it gone."""
        from aiogram.exceptions import TelegramBadRequest

        topic_id = await self.ensure_topic(key, topic_name)
        try:
            return await self._send_to_topic(topic_id, text, **kwargs)
        except TelegramBadRequest as exc:
            if not _is_topic_gone(exc):
                raise
            logger.warning(
                "forum topic gone, recreating",
                extra={"key": key, "topic_id": topic_id},
            )
            topic_id = await self._create_topic(topic_name)
            await self._store.set_thread_id(key, topic_id)
            return await self._send_to_topic(topic_id, text, **kwargs)

    async def _create_topic(self, name: str) -> int:
        topic = await asyncio.wait_for(
            self._bot.create_forum_topic(
                chat_id=self._forum_chat_id,
                name=name[:128],
            ),
            timeout=self._call_timeout,
        )
        return int(topic.message_thread_id)

    async def _send_to_topic(
        self,
        topic_id: int,
        text: str,
        **kwargs: Any,
    ) -> Any:
        return await asyncio.wait_for(
            self._bot.send_message(
                self._forum_chat_id,
                text,
                message_thread_id=topic_id,
                **kwargs,
            ),
            timeout=self._call_timeout,
        )
