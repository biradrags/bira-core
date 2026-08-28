from __future__ import annotations

import asyncio
import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode

logger = logging.getLogger(__name__)


class TgDialogNotifier:
    DEFAULT_TTL_SEC = 5

    def __init__(self) -> None:
        self._pending_deletes: set[asyncio.Task[None]] = set()

    async def answer(
        self,
        message: Message,
        text: str,
        manager: DialogManager,
        *,
        delete_after: int = DEFAULT_TTL_SEC,
    ) -> None:
        manager.show_mode = ShowMode.EDIT
        sent = await message.answer(text)
        self.delayed_delete(sent, delete_after)

    async def warn(
        self,
        message: Message,
        text: str,
        manager: DialogManager,
        *,
        delete_after: int = DEFAULT_TTL_SEC,
    ) -> None:
        await self.answer(message, f"⚠️ {text}", manager, delete_after=delete_after)

    async def safe_callback_answer(
        self,
        callback: CallbackQuery,
        text: str,
        *,
        show_alert: bool = False,
    ) -> bool:
        try:
            await callback.answer(text, show_alert=show_alert)
        except TelegramBadRequest as exc:
            logger.warning(
                "cannot answer callback",
                extra={"platform": "tg", "callback_id": callback.id, "err": exc},
            )
            return False
        else:
            return True

    async def safe_delete(self, message: Message) -> bool:
        try:
            await message.delete()
        except TelegramBadRequest as exc:
            logger.warning(
                "cannot delete message",
                extra={
                    "platform": "tg",
                    "message_id": message.message_id,
                    "err": exc,
                },
            )
            return False
        else:
            return True

    async def safe_delete_message(self, message: Message) -> bool:
        return await self.safe_delete(message)

    def delayed_delete(self, message: Message, delay: float) -> None:
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
            await self.safe_delete(message)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("delayed delete failed", exc_info=True)
