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

__all__ = ["TOPIC_GONE_MARKERS", "ForumTopics", "ThreadStore", "is_topic_gone"]


@runtime_checkable
class ThreadStore(Protocol):
    """Persist forum thread_id per logical key (DAO-backed in consumer)."""

    async def get_thread_id(self, key: str) -> int | None:
        """Return stored thread_id or None before first topic creation."""
        ...

    async def set_thread_id(self, key: str, thread_id: int) -> None:
        """Persist thread_id after ensure_topic creates or recreates a topic."""
        ...


class ForumTopics:
    """Ensure forum topics per logical key and resend after topic deletion."""

    def __init__(
        self,
        bot: Any,
        forum_chat_id: int,
        store: ThreadStore,
        *,
        call_timeout: float = 15,
    ) -> None:
        """Wire bot, default forum chat, and DAO-backed thread store."""
        self._bot = bot
        self._forum_chat_id = forum_chat_id
        self._store = store
        self._call_timeout = call_timeout
        self._locks: dict[str, asyncio.Lock] = {}

    def _chat(self, chat_id: int | None) -> int:
        return self._forum_chat_id if chat_id is None else chat_id

    async def ensure_topic(
        self, key: str, name: str, *, chat_id: int | None = None
    ) -> int:
        """Create topic once per key under per-key lock (concurrent-safe).

        ``chat_id`` перекрывает чат конструктора - для ботов, у которых форум свой
        на каждого владельца. Ключ тогда обязан включать чат, иначе два владельца
        делят одну запись в store.
        """
        topic_id = await self._store.get_thread_id(key)
        if topic_id is not None:
            return topic_id
        async with self._locks.setdefault(key, asyncio.Lock()):
            topic_id = await self._store.get_thread_id(key)
            if topic_id is not None:
                return topic_id
            topic_id = await self._create_topic(name, self._chat(chat_id))
            await self._store.set_thread_id(key, topic_id)
            return topic_id

    async def send(
        self,
        key: str,
        text: str,
        *,
        topic_name: str,
        chat_id: int | None = None,
        **kwargs: Any,
    ) -> Any:
        """Send to forum topic; recreate topic if Telegram reports it gone."""
        from aiogram.exceptions import TelegramBadRequest

        chat = self._chat(chat_id)
        topic_id = await self.ensure_topic(key, topic_name, chat_id=chat)
        try:
            return await self._send_to_topic(topic_id, text, chat, **kwargs)
        except TelegramBadRequest as exc:
            if not is_topic_gone(exc):
                raise
            logger.warning(
                "forum topic gone, recreating",
                extra={"key": key, "topic_id": topic_id},
            )
            topic_id = await self._recreate_topic(
                key, topic_name, stale_id=topic_id, chat_id=chat
            )
            return await self._send_to_topic(topic_id, text, chat, **kwargs)

    async def _recreate_topic(
        self, key: str, name: str, *, stale_id: int, chat_id: int
    ) -> int:
        """Пересоздать топик под тем же локом, что и ensure_topic.

        Без общего лока два конкурентных send создают два топика, и сообщение
        проигравшей гонки уходит в тот, на который store уже не ссылается.
        """
        async with self._locks.setdefault(key, asyncio.Lock()):
            current = await self._store.get_thread_id(key)
            if current is not None and current != stale_id:
                return current
            topic_id = await self._create_topic(name, chat_id)
            await self._store.set_thread_id(key, topic_id)
            return topic_id

    async def _create_topic(self, name: str, chat_id: int) -> int:
        # wait_for на каждый вызов Telegram: suspend-рантайм может заморозить
        # процесс посреди запроса, а зависшая корутина держала бы лок ключа.
        topic = await asyncio.wait_for(
            self._bot.create_forum_topic(
                chat_id=chat_id,
                name=name[:128],
            ),
            timeout=self._call_timeout,
        )
        return int(topic.message_thread_id)

    async def _send_to_topic(
        self,
        topic_id: int,
        text: str,
        chat_id: int,
        **kwargs: Any,
    ) -> Any:
        return await asyncio.wait_for(
            self._bot.send_message(
                chat_id,
                text,
                message_thread_id=topic_id,
                **kwargs,
            ),
            timeout=self._call_timeout,
        )


def is_topic_gone(exc: BaseException) -> bool:
    """True когда Telegram сказал, что топика больше нет.

    Публичная: распознать «топик удалён» нужно и тем, кто его не пересоздаёт,
    а скипает или гасит доставку. Без aiogram в процессе TelegramBadRequest
    взяться неоткуда - ответ False, а не ImportError.
    """
    try:
        from aiogram.exceptions import TelegramBadRequest
    except ImportError:
        return False

    if not isinstance(exc, TelegramBadRequest):
        return False
    text = str(exc).lower()
    return any(marker.lower() in text for marker in TOPIC_GONE_MARKERS)
