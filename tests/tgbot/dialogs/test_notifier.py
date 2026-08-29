from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from bira_core.tgbot.dialogs.notifier import TgDialogNotifier


@pytest.mark.asyncio
async def test_answer_sets_edit_mode_and_schedules_delete() -> None:
    notifier = TgDialogNotifier()
    message = MagicMock(spec=Message)
    sent = MagicMock(spec=Message)
    message.answer = AsyncMock(return_value=sent)
    manager = MagicMock()

    await notifier.answer(message, "hi", manager, delete_after=0)

    assert manager.show_mode is not None
    message.answer.assert_awaited_once_with("hi")


@pytest.mark.asyncio
async def test_safe_callback_answer_handles_bad_request() -> None:
    notifier = TgDialogNotifier()
    callback = MagicMock(spec=CallbackQuery)
    callback.id = "cb1"
    callback.answer = AsyncMock(
        side_effect=TelegramBadRequest(method="x", message="old")
    )

    ok = await notifier.safe_callback_answer(callback, "nope")

    assert ok is False
