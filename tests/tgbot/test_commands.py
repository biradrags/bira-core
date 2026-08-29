from unittest.mock import AsyncMock, patch

import pytest
from aiogram.types import Chat, Message, User

from bira_core.tgbot.commands import (
    CANCEL_COMMAND,
    CHAT_ID_COMMAND,
    cancel_command,
    chat_id_command,
    register_debug_commands,
)
from bira_core.tgbot.filters import IsServiceChat


@pytest.fixture
def message() -> Message:
    return Message(
        message_id=1,
        date=0,
        chat=Chat(id=42, type="private"),
        from_user=User(id=7, is_bot=False, first_name="T"),
    )


async def test_chat_id_command_replies(message: Message) -> None:
    with patch.object(Message, "reply", new_callable=AsyncMock) as reply:
        await chat_id_command(message)
        reply.assert_awaited_once()
        assert "42" in reply.await_args.args[0]


async def test_cancel_command_clears_state(message: Message) -> None:
    state = AsyncMock()
    state.get_state = AsyncMock(return_value="some:state")
    with patch.object(Message, "reply", new_callable=AsyncMock) as reply:
        await cancel_command(message, state)
        state.clear.assert_awaited_once()
        reply.assert_awaited_once()


async def test_is_service_chat_matches() -> None:
    filt = IsServiceChat(42)
    msg = Message(message_id=1, date=0, chat=Chat(id=42, type="private"))
    assert await filt(msg) is True


def test_command_constants() -> None:
    assert CANCEL_COMMAND.command == "cancel"
    assert CHAT_ID_COMMAND.command == "chat_id"


async def test_register_debug_commands() -> None:
    bot = AsyncMock()
    await register_debug_commands(bot, [1, 2])
    assert bot.set_my_commands.await_count == 2
