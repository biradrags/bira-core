from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Router
from aiogram.types import CallbackQuery, Message

from bira_core.tgbot.dialogs.errors import clear_stale_intent, register_stale_intent


class _Notifier:
    def __init__(self) -> None:
        self.deleted = False

    async def safe_delete_message(self, message: Message) -> bool:
        self.deleted = True
        return True


@pytest.mark.asyncio
async def test_clear_stale_intent_deletes_message() -> None:
    notifier = _Notifier()
    callback = MagicMock(spec=CallbackQuery)
    callback.answer = AsyncMock()
    callback.message = MagicMock(spec=Message)
    callback.bot = None
    error = MagicMock()
    error.update.callback_query = callback

    await clear_stale_intent(error, notifier)

    callback.answer.assert_awaited_once_with("Меню устарело")
    assert notifier.deleted is True


def test_register_stale_intent_on_router() -> None:
    router = Router()
    register_stale_intent(router)
    assert router.errors.handlers
