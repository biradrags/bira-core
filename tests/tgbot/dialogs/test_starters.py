from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bira_core.tgbot.dialogs.starters import (
    cancel_state,
    register_business_handler,
    register_callback_starter,
    register_cancel_state,
    register_start_handler,
)


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


def test_register_cancel_state_adds_handler() -> None:
    router = Router()
    register_cancel_state(router, commands="stop")
    assert router.message.handlers


@pytest.mark.asyncio
async def test_start_handler_passes_data() -> None:
    router = Router()
    register_start_handler(state=_States.wait, router=router, data={"k": 1})
    handler = router.message.handlers[0].callback
    dm = AsyncMock()
    await handler(MagicMock(spec=Message), dm)
    dm.start.assert_awaited_once()
    assert dm.start.await_args.kwargs["data"] == {"k": 1}


@pytest.mark.asyncio
async def test_callback_starter_passes_static_data() -> None:
    router = Router()
    register_callback_starter(state=_States.wait, router=router, data={"k": 2})
    handler = router.callback_query.handlers[0].callback
    callback = MagicMock()
    callback.answer = AsyncMock()
    callback.bot = MagicMock()
    callback.from_user = MagicMock()
    callback.from_user.id = 1
    callback.message = MagicMock()
    callback.message.chat.id = 1
    callback.message.message_thread_id = None
    callback.message.business_connection_id = None
    bg = AsyncMock()
    factory = MagicMock()
    factory.bg.return_value = bg
    await handler(callback, factory, None)
    bg.start.assert_awaited_once()
    assert bg.start.await_args.kwargs["data"] == {"k": 2}


@pytest.mark.asyncio
async def test_business_handler_delete_on_start() -> None:
    router = Router()
    register_business_handler(state=_States.wait, router=router, delete_on_start=True)
    handler = router.business_message.handlers[0].callback
    message = MagicMock()
    message.bot = AsyncMock()
    message.chat = MagicMock()
    message.chat.id = 1
    message.message_id = 2
    message.bot.delete_message = AsyncMock()
    dm = AsyncMock()
    await handler(message, dm)
    message.bot.delete_message.assert_awaited_once()
