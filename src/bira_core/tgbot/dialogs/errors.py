"""Stale-intent cleanup for dialogs."""

import logging
from collections.abc import Awaitable, Callable
from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.types.error_event import ErrorEvent
from aiogram_dialog.api.exceptions import OutdatedIntent, UnknownIntent, UnknownState

from bira_core.tgbot.dialogs.notifier import delete_if_exists

logger = logging.getLogger(__name__)


async def clear_stale_intent(error: ErrorEvent) -> None:
    """Clear stale intent."""
    callback = error.update.callback_query
    if callback is None:
        return
    await callback.answer("Меню устарело")
    message = callback.message
    if message is None:
        return
    bot = callback.bot
    if bot is None:
        return
    if getattr(message, "message_id", None) is not None and await delete_if_exists(
        bot, message.chat.id, message.message_id
    ):
        return
    with suppress(TelegramBadRequest):
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=None,
        )


def register_stale_intent(
    router: Router,
    *,
    handler: Callable[[ErrorEvent], Awaitable[None]] | None = None,
) -> None:
    """Вешать на отдельный router до include в основной (канон dialogs.md)."""

    stale_handler = handler or clear_stale_intent

    async def _handler(error: ErrorEvent) -> None:
        await stale_handler(error)

    router.errors.register(
        _handler,
        ExceptionTypeFilter(UnknownIntent, UnknownState, OutdatedIntent),
    )
