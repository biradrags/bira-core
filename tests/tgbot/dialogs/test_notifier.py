from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from bira_core.tgbot.dialogs.notifier import TgDialogNotifier, delete_if_exists


@pytest.mark.asyncio
async def test_answer_sets_edit_mode_and_schedules_delete() -> None:
    notifier = TgDialogNotifier()
    message = MagicMock(spec=Message)
    sent = MagicMock(spec=Message)
    message.answer = AsyncMock(return_value=sent)
    manager = MagicMock()
    manager.event = message

    await notifier.answer(manager, "hi", ttl=0)

    assert manager.show_mode is not None
    message.answer.assert_awaited_once_with("hi")


@pytest.mark.asyncio
async def test_ack_handles_query_too_old() -> None:
    notifier = TgDialogNotifier()
    callback = MagicMock(spec=CallbackQuery)
    callback.id = "cb1"
    callback.answer = AsyncMock(
        side_effect=TelegramBadRequest(method="x", message="query is too old")
    )

    ok = await notifier.ack(callback)

    assert ok is False


@pytest.mark.asyncio
async def test_delete_if_exists_swallows_gone_message() -> None:
    bot = AsyncMock()
    bot.delete_message = AsyncMock(
        side_effect=TelegramBadRequest(
            method="deleteMessage", message="message to delete not found"
        )
    )
    assert await delete_if_exists(bot, 1, 2) is False
