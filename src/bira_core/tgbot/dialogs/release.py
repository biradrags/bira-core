"""Eager release: транзакция апдейта закрывается перед каждым выходом aiogram_dialog
в Telegram (канон dialogs.md, «Eager release»)."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Protocol

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog.api.entities import NewMessage, OldMessage, ShowMode
from aiogram_dialog.manager.message_manager import MessageManager


class Releasable(Protocol):
    """DAO апдейта: release коммитит открытую транзакцию и возвращает коннект в пул."""

    async def release(self) -> None:
        """Закрыть транзакцию перед долгим I/O."""


# MessageManager получает от aiogram_dialog только bot - DAO апдейта доходит ContextVar-ом
_current: ContextVar[Releasable | None] = ContextVar("bira_release_dao", default=None)


@contextmanager
def bind_release(dao: Releasable) -> Iterator[None]:
    """DAO апдейта для release на время хендлера. Звать в InitMiddleware на `dp.update` с `data["dao"]`."""
    token = _current.set(dao)
    try:
        yield
    finally:
        _current.reset(token)


async def release_current() -> None:
    """Отпустить DAO текущего апдейта; вне апдейта - no-op."""
    dao = _current.get()
    if dao is not None:
        await dao.release()


class ReleasingMessageManager(MessageManager):
    """Отпускает транзакцию перед show_message, remove_kbd и answer_callback."""

    async def show_message(
        self, bot: Bot, new_message: NewMessage, old_message: OldMessage | None
    ) -> OldMessage:
        """Release, затем штатный show_message."""
        await release_current()
        return await super().show_message(bot, new_message, old_message)

    async def remove_kbd(
        self, bot: Bot, show_mode: ShowMode, old_message: OldMessage | None
    ) -> Message | None:
        """Release, затем штатный remove_kbd."""
        await release_current()
        return await super().remove_kbd(bot, show_mode, old_message)

    async def answer_callback(self, bot: Bot, callback_query: CallbackQuery) -> None:
        """Release, затем штатный answer_callback."""
        await release_current()
        await super().answer_callback(bot, callback_query)
