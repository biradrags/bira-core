from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Router

from bira_core.tgbot.dialogs.errors import clear_stale_intent, register_stale_intent


@pytest.mark.asyncio
async def test_clear_stale_intent_deletes_message() -> None:
    callback = MagicMock()
    callback.answer = AsyncMock()
    callback.message = MagicMock()
    callback.message.chat.id = 1
    callback.message.message_id = 2
    callback.bot = AsyncMock()
    callback.bot.delete_message = AsyncMock(return_value=True)
    error = MagicMock()
    error.update.callback_query = callback

    await clear_stale_intent(error)

    callback.answer.assert_awaited_once_with("Меню устарело")
    callback.bot.delete_message.assert_awaited_once_with(chat_id=1, message_id=2)


def test_register_stale_intent_on_router() -> None:
    router = Router()
    register_stale_intent(router)
    assert router.errors.handlers
