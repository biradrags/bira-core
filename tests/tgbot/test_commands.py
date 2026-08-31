from unittest.mock import AsyncMock, patch

import pytest
from aiogram.types import Chat, Message, User

from bira_core.tgbot.commands import CANCEL_COMMAND, cancel_command


@pytest.fixture
def message() -> Message:
    return Message(
        message_id=1,
        date=0,
        chat=Chat(id=42, type="private"),
        from_user=User(id=7, is_bot=False, first_name="T"),
    )


async def test_cancel_command_clears_state(message: Message) -> None:
    state = AsyncMock()
    state.get_state = AsyncMock(return_value="some:state")
    with patch.object(Message, "reply", new_callable=AsyncMock) as reply:
        await cancel_command(message, state)
        state.clear.assert_awaited_once()
        reply.assert_awaited_once()


async def test_cancel_command_without_state_is_silent(message: Message) -> None:
    state = AsyncMock()
    state.get_state = AsyncMock(return_value=None)
    with patch.object(Message, "reply", new_callable=AsyncMock) as reply:
        await cancel_command(message, state)
        state.clear.assert_not_awaited()
        reply.assert_not_awaited()


def test_command_constants() -> None:
    assert CANCEL_COMMAND.command == "cancel"
