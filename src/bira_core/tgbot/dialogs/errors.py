import logging
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Protocol, runtime_checkable

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import Message
from aiogram.types.error_event import ErrorEvent
from aiogram_dialog.api.exceptions import OutdatedIntent, UnknownIntent, UnknownState

logger = logging.getLogger(__name__)


@runtime_checkable
class StaleIntentNotifier(Protocol):
    async def safe_delete_message(self, message: Message) -> bool: ...


async def clear_stale_intent(
    error: ErrorEvent,
    notifier: StaleIntentNotifier | None = None,
) -> None:
    callback = error.update.callback_query
    if callback is None:
        return
    await callback.answer("Меню устарело")
    if callback.message is None:
        return
    if notifier is None:
        return
    if not isinstance(callback.message, Message):
        bot = callback.bot
        if bot is None:
            return
        with suppress(TelegramBadRequest):
            await bot.edit_message_reply_markup(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=None,
            )
        return
    if await notifier.safe_delete_message(callback.message):
        return
    bot = callback.bot
    if bot is None:
        return
    with suppress(TelegramBadRequest):
        await bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None,
        )


def register_stale_intent(
    router: Router,
    *,
    notifier: StaleIntentNotifier | None = None,
    handler: Callable[[ErrorEvent, StaleIntentNotifier | None], Awaitable[None]]
    | None = None,
) -> None:
    stale_handler = handler or clear_stale_intent

    async def _handler(error: ErrorEvent) -> None:
        await stale_handler(error, notifier)

    router.errors.register(
        _handler,
        ExceptionTypeFilter(UnknownIntent, UnknownState, OutdatedIntent),
    )
