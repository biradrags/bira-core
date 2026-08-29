"""TG dialog notifier and delete helper."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode

from bira_core._tasks import DelayedDeleter

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
    """Delete if exists."""
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
        """Initialize instance."""
        self._bot = bot
        self._deleter = DelayedDeleter()

    async def answer(
        self,
        manager: DialogManager,
        text: str,
        *,
        ttl: float = DEFAULT_TTL_SEC,
    ) -> None:
        """Answer."""
        event = manager.event
        if not isinstance(event, Message):
            return
        manager.show_mode = ShowMode.EDIT
        sent = await event.answer(text)
        bot = self._bot or event.bot
        if bot is not None:

            async def _delete() -> None:
                await delete_if_exists(bot, sent.chat.id, sent.message_id)

            self._deleter.schedule(_delete, ttl)

    async def warn(
        self,
        manager: DialogManager,
        text: str,
        *,
        ttl: float = DEFAULT_TTL_SEC,
    ) -> None:
        """Warn."""
        await self.answer(manager, f"⚠️ {text}", ttl=ttl)

    async def delete(self, chat_id: int, message_id: int) -> bool:
        """Delete."""
        bot = self._bot
        if bot is None:
            return False
        return await delete_if_exists(bot, chat_id, message_id)

    async def ack(self, callback: CallbackQuery) -> bool:
        """Ack."""
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

    async def shutdown(self) -> None:
        """Shutdown."""
        await self._deleter.shutdown()
