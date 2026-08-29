import logging
from collections.abc import Sequence
from typing import Any

from aiogram import Router
from aiogram.dispatcher.event.handler import CallbackType
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import BgManagerFactory, Data, DialogManager, ShowMode, StartMode

from bira_core.tgbot.commands import cancel_command
from bira_core.tgbot.dialogs.notifier import delete_if_exists

logger = logging.getLogger(__name__)


def _resolve_start_data(
    data: Data,
    callback_data: CallbackData | None,
) -> Any:
    if data is not None and callable(data):
        return data(callback_data) if callback_data else data(None)
    if data is not None:
        return data
    return callback_data.model_dump() if callback_data else None


def register_start_handler(
    *filters: CallbackType,
    state: State,
    router: Router,
    mode: StartMode = StartMode.NORMAL,
    show_mode: ShowMode = ShowMode.AUTO,
    data: Data = None,
) -> None:
    async def start_dialog(
        message: Message,
        dialog_manager: DialogManager,
    ) -> None:
        await dialog_manager.start(state, mode=mode, data=data, show_mode=show_mode)

    router.message.register(
        start_dialog,
        *filters,
    )


def register_callback_starter(
    *filters: CallbackType,
    state: State,
    router: Router,
    mode: StartMode = StartMode.NORMAL,
    show_mode: ShowMode = ShowMode.AUTO,
    data: Data = None,
) -> None:
    async def start_dialog(
        callback: CallbackQuery,
        bg_manager_factory: BgManagerFactory,
        callback_data: CallbackData | None = None,
        **kwargs: Any,
    ) -> None:
        await callback.answer()
        message = callback.message
        if callback.bot is None or message is None or not hasattr(message, "chat"):
            return
        start_data = _resolve_start_data(data, callback_data)

        bg = bg_manager_factory.bg(
            callback.bot,
            callback.from_user.id,
            message.chat.id,
            thread_id=getattr(message, "message_thread_id", None),
            business_connection_id=getattr(message, "business_connection_id", None),
        )
        await bg.start(state, mode=mode, show_mode=show_mode, data=start_data)

    router.callback_query.register(
        start_dialog,
        *filters,
    )


def register_business_handler(
    *filters: CallbackType,
    state: State,
    router: Router,
    mode: StartMode = StartMode.NORMAL,
    show_mode: ShowMode = ShowMode.AUTO,
    data: Data = None,
    delete_on_start: bool = False,
) -> None:
    async def start_dialog(
        message: Message,
        dialog_manager: DialogManager,
    ) -> None:
        if delete_on_start and message.bot is not None:
            await delete_if_exists(message.bot, message.chat.id, message.message_id)
        await dialog_manager.start(state, mode=mode, data=data, show_mode=show_mode)

    router.business_message.register(
        start_dialog,
        *filters,
    )


async def cancel_state(
    message: Message,
    state: FSMContext,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.reset_stack(remove_keyboard=True)
    await cancel_command(message, state)


def register_cancel_state(
    router: Router,
    *,
    commands: str | Sequence[str] = "cancel",
) -> None:
    router.message.register(cancel_state, Command(commands=commands))
