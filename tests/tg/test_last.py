from unittest.mock import AsyncMock, patch

import pytest
from aiogram.types import CallbackQuery, Chat, Message, User

from bira_core.tg.last import setup_last_router


@pytest.fixture
def callback() -> CallbackQuery:
    return CallbackQuery(
        id="1",
        from_user=User(id=1, is_bot=False, first_name="T"),
        chat_instance="x",
        message=Message(
            message_id=10,
            date=0,
            chat=Chat(id=1, type="private"),
        ),
    )


async def test_alert_strategy(callback: CallbackQuery) -> None:
    router = setup_last_router("alert")
    handler = router.callback_query.handlers[0].callback
    with patch.object(CallbackQuery, "answer", new_callable=AsyncMock) as answer:
        await handler(callback)
        answer.assert_awaited_once()
        assert answer.await_args.kwargs.get("show_alert") is True


async def test_delete_strategy(callback: CallbackQuery) -> None:
    router = setup_last_router("delete")
    bot = AsyncMock()
    handler = router.callback_query.handlers[0].callback
    with patch.object(CallbackQuery, "answer", new_callable=AsyncMock):
        await handler(callback, bot)
        bot.delete_message.assert_awaited_once()
