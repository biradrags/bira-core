from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bira_core.dialogs.starters import cancel_state, register_cancel_state


class _States(StatesGroup):
    wait = State()


@pytest.mark.asyncio
async def test_cancel_state_clears_fsm() -> None:
    message = MagicMock(spec=Message)
    message.reply = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    state.get_state.return_value = _States.wait
    dialog_manager = AsyncMock()

    await cancel_state(message, state, dialog_manager)

    dialog_manager.reset_stack.assert_awaited_once_with(remove_keyboard=True)
    state.clear.assert_awaited_once()
    message.reply.assert_awaited_once()


def test_register_cancel_state_adds_handler() -> None:
    router = Router()
    register_cancel_state(router, commands="stop")
    assert router.message.handlers
