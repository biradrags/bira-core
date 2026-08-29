from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode

logger = logging.getLogger(__name__)

_MESSAGE_GONE_MARKERS = (
    "message to delete not found",
    "message can't be deleted",
    "message not found",
)
_QUERY_TOO_OLD_MARKERS = (
    "query is too old",
    "query id is invalid",
)


async def delete_if_exists(bot: Bot, chat_id: int, message_id: int) -> bool:
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except TelegramBadRequest as exc:
        text = str(exc).lower()
        if any(marker in text for marker in _MESSAGE_GONE_MARKERS):
            return False
        raise
    else:
        return True


class TgDialogNotifier:
    """Тихие delete/ack — только известные маркеры «уже удалено» / «query is too old»."""

    DEFAULT_TTL_SEC = 5.0

    def __init__(self, bot: Bot | None = None) -> None:
        self._bot = bot
        self._pending_deletes: set[asyncio.Task[None]] = set()

    async def answer(
        self,
        manager: DialogManager,
        text: str,
        *,
        ttl: float = DEFAULT_TTL_SEC,
    ) -> None:
        event = manager.event
        if not isinstance(event, Message):
            return
        manager.show_mode = ShowMode.EDIT
        sent = await event.answer(text)
        self._schedule_delete(sent, ttl)

    async def warn(
        self,
        manager: DialogManager,
        text: str,
        *,
        ttl: float = DEFAULT_TTL_SEC,
    ) -> None:
        await self.answer(manager, f"⚠️ {text}", ttl=ttl)

    async def delete(self, chat_id: int, message_id: int) -> bool:
        bot = self._bot
        if bot is None:
            return False
        return await delete_if_exists(bot, chat_id, message_id)

    async def ack(self, callback: CallbackQuery) -> bool:
        try:
            await callback.answer()
        except TelegramBadRequest as exc:
            text = str(exc).lower()
            if any(marker in text for marker in _QUERY_TOO_OLD_MARKERS):
                return False
            logger.warning(
                "cannot answer callback",
                extra={"platform": "tg", "callback_id": callback.id, "err": exc},
            )
            return False
        else:
            return True

    def _schedule_delete(self, message: Message, delay: float) -> None:
        if delay <= 0:
            return
        task = asyncio.create_task(self._delete_after(message, delay))
        self._pending_deletes.add(task)
        task.add_done_callback(self._pending_deletes.discard)

    async def shutdown(self) -> None:
        for task in list(self._pending_deletes):
            task.cancel()
        if self._pending_deletes:
            await asyncio.gather(*self._pending_deletes, return_exceptions=True)

    async def _delete_after(self, message: Message, delay: float) -> None:
        try:
            await asyncio.sleep(delay)
            bot = self._bot or message.bot
            if bot is None:
                return
            await delete_if_exists(bot, message.chat.id, message.message_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("delayed delete failed", exc_info=True)
