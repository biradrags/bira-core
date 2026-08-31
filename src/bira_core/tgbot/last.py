"""Stale callback button handlers."""

import contextlib
import logging
from typing import Literal

from aiogram import Bot, Router, types

logger = logging.getLogger(__name__)

__all__ = ["setup_last_router"]


def setup_last_router(strategy: Literal["alert", "delete"]) -> Router:
    """Router that answers or deletes stale unsupported callbacks."""
    router = Router(name="bira_core.last")
    handler = _not_supported_alert if strategy == "alert" else _not_supported_delete
    router.callback_query.register(handler)
    return router


async def _not_supported_alert(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(
        "Эта кнопка не поддерживается или не предназначена для Вас.",
        show_alert=True,
    )
    logger.warning(
        "user pressed unsupported button",
        extra={
            "user_id": callback_query.from_user.id,
            "data": callback_query.data,
        },
    )


async def _not_supported_delete(callback_query: types.CallbackQuery, bot: Bot) -> None:
    await callback_query.answer()
    if callback_query.message:
        with contextlib.suppress(Exception):
            await bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
            )
    logger.debug(
        "deleted stale dialog message",
        extra={
            "platform_id": (
                callback_query.from_user.id if callback_query.from_user else None
            ),
        },
    )
