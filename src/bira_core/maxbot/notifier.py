from __future__ import annotations

import asyncio
import logging

from maxo.bot import Bot
from maxo.dialogs import DialogManager, ShowMode
from maxo.enums import TextFormat
from maxo.errors import MaxBotBadRequestError
from maxo.routing.updates import MessageCallback, MessageCreated

logger = logging.getLogger(__name__)

_MESSAGE_GONE_MARKERS = (
    "message to delete not found",
    "message can't be deleted",
)
_QUERY_TOO_OLD_MARKERS = ("query is too old",)


class MaxDialogNotifier:
    """Тихие delete/ack — только известные маркеры «уже удалено» / «query is too old»."""

    DEFAULT_TTL_SEC = 5.0

    def __init__(self, bot: Bot) -> None:
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
        if not isinstance(event, MessageCreated):
            return
        chat_id = event.message.recipient.chat_id
        if chat_id is None:
            return
        manager.show_mode = ShowMode.EDIT
        sent = await self._bot.send_message(
            chat_id=chat_id,
            text=text,
            format=TextFormat.HTML,
        )
        sent_mid = (
            sent.message.body.mid
            if sent is not None
            and sent.message is not None
            and sent.message.body is not None
            else None
        )
        if sent_mid is not None:
            self._schedule_delete(sent_mid, ttl)

    async def warn(
        self,
        manager: DialogManager,
        text: str,
        *,
        ttl: float = DEFAULT_TTL_SEC,
    ) -> None:
        await self.answer(manager, f"⚠️ {text}", ttl=ttl)

    async def delete(self, chat_id: int, message_id: str) -> bool:
        try:
            await self._bot.delete_message(message_id=message_id)
        except MaxBotBadRequestError as exc:
            msg = str(exc.message or "").lower()
            if any(marker in msg for marker in _MESSAGE_GONE_MARKERS):
                return False
            logger.warning(
                "unexpected MaxBotBadRequestError on delete",
                extra={"platform": "max", "message_id": message_id, "err": exc},
            )
            raise
        else:
            return True

    async def ack(self, callback: MessageCallback) -> bool:
        try:
            await callback.callback_answer()
        except MaxBotBadRequestError as exc:
            msg = str(exc.message or "").lower()
            if any(marker in msg for marker in _QUERY_TOO_OLD_MARKERS):
                return False
            logger.warning(
                "cannot answer callback",
                extra={"platform": "max", "err": exc},
            )
            return False
        else:
            return True

    async def shutdown(self) -> None:
        for task in list(self._pending_deletes):
            task.cancel()
        if self._pending_deletes:
            await asyncio.gather(*self._pending_deletes, return_exceptions=True)

    def _schedule_delete(self, message_id: str, delay: float) -> None:
        if delay <= 0:
            return
        task = asyncio.create_task(self._delete_after(message_id, delay))
        self._pending_deletes.add(task)
        task.add_done_callback(self._pending_deletes.discard)

    async def _delete_after(self, message_id: str, delay: float) -> None:
        try:
            await asyncio.sleep(delay)
            await self.delete(0, message_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("delayed delete failed", exc_info=True)
