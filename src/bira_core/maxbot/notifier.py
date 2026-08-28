from __future__ import annotations

import asyncio
import logging

from maxo.bot import Bot
from maxo.dialogs import DialogManager, ShowMode
from maxo.enums import TextFormat
from maxo.errors import MaxBotBadRequestError
from maxo.routing.updates import MessageCallback, MessageCreated

logger = logging.getLogger(__name__)


class MaxDialogNotifier:
    DEFAULT_TTL_SEC = 5

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._pending_deletes: set[asyncio.Task[None]] = set()

    async def answer(
        self,
        message: MessageCreated,
        text: str,
        manager: DialogManager,
        *,
        delete_after: int = DEFAULT_TTL_SEC,
    ) -> None:
        chat_id = message.message.recipient.chat_id
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
            self.delayed_delete(sent_mid, delete_after)

    async def warn(
        self,
        message: MessageCreated,
        text: str,
        manager: DialogManager,
        *,
        delete_after: int = DEFAULT_TTL_SEC,
    ) -> None:
        await self.answer(message, f"⚠️ {text}", manager, delete_after=delete_after)

    async def safe_callback_answer(
        self, manager: DialogManager, notification: str
    ) -> bool:
        event = manager.event
        if isinstance(event, MessageCallback):
            await event.callback_answer(notification=notification)
            return True
        return False

    async def safe_delete(self, message_id: str) -> bool:
        try:
            await self._bot.delete_message(message_id=message_id)
        except MaxBotBadRequestError as exc:
            msg = str(exc.message or "")
            if (
                "message to delete not found" in msg
                or "message can't be deleted" in msg
            ):
                return False
            logger.warning(
                "unexpected MaxBotBadRequestError on delete",
                extra={"platform": "max", "message_id": message_id, "err": exc},
            )
            raise
        else:
            return True

    async def shutdown(self) -> None:
        for task in list(self._pending_deletes):
            task.cancel()
        if self._pending_deletes:
            await asyncio.gather(*self._pending_deletes, return_exceptions=True)

    def delayed_delete(self, message_id: str, delay: float) -> None:
        if delay <= 0:
            return
        task = asyncio.create_task(self._delete_after(message_id, delay))
        self._pending_deletes.add(task)
        task.add_done_callback(self._pending_deletes.discard)

    async def _delete_after(self, message_id: str, delay: float) -> None:
        try:
            await asyncio.sleep(delay)
            await self.safe_delete(message_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("delayed delete failed", exc_info=True)
