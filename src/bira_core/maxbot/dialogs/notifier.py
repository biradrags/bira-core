"""MAX dialog notifier with TTL feedback."""

from __future__ import annotations

import logging

from maxo.bot import Bot
from maxo.dialogs import DialogManager, ShowMode
from maxo.enums import TextFormat
from maxo.errors import MaxBotBadRequestError
from maxo.types import MessageCallback, MessageCreated

from bira_core._tasks import DelayedDeleter
from bira_core.maxbot._errors import is_message_gone

logger = logging.getLogger(__name__)

_QUERY_TOO_OLD_MARKERS = ("query is too old",)


class MaxDialogNotifier:
    """Тихие delete/ack — только известные маркеры «уже удалено» / «query is too old»."""

    DEFAULT_TTL_SEC = 5.0

    def __init__(self, bot: Bot) -> None:
        """Hold MaxBot used for send/delete/ack in dialogs."""
        self._bot = bot
        self._deleter = DelayedDeleter()

    async def answer(
        self,
        manager: DialogManager,
        text: str,
        *,
        ttl: float = DEFAULT_TTL_SEC,
    ) -> None:
        """Send feedback and schedule TTL delete of the new message."""
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

            async def _delete() -> None:
                await self.delete(0, sent_mid)

            self._deleter.schedule(_delete, ttl)

    async def warn(
        self,
        manager: DialogManager,
        text: str,
        *,
        ttl: float = DEFAULT_TTL_SEC,
    ) -> None:
        """answer() with a warning prefix."""
        await self.answer(manager, f"⚠️ {text}", ttl=ttl)

    async def delete(self, chat_id: int, message_id: str) -> bool:
        """delete_message; False only for known «message gone» markers."""
        try:
            await self._bot.delete_message(message_id=message_id)
        except MaxBotBadRequestError as exc:
            if is_message_gone(exc):
                return False
            logger.warning(
                "unexpected MaxBotBadRequestError on delete",
                extra={"platform": "max", "message_id": message_id, "err": exc},
            )
            raise
        else:
            return True

    async def ack(self, callback: MessageCallback) -> bool:
        """callback_answer(); False only for «query is too old» class."""
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
        """Cancel pending TTL delete tasks."""
        await self._deleter.shutdown()
