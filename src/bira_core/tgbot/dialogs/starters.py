import logging
from collections.abc import Sequence
from typing import Any

from aiogram import Router
from aiogram.dispatcher.event.handler import CallbackType
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram_dialog import BgManagerFactory, Data, DialogManager, ShowMode, StartMode

from bira_core.tgbot.dialogs.errors import StaleIntentNotifier

logger = logging.getLogger(__name__)


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
        if callback.bot is None or not isinstance(callback.message, Message):
            return
        if data is not None and callable(data):
            start_data = data(callback_data) if callback_data else None
        else:
            start_data = callback_data.model_dump() if callback_data else None

        bg = bg_manager_factory.bg(
            callback.bot,
            callback.from_user.id,
            callback.message.chat.id,
            thread_id=callback.message.message_thread_id,
            business_connection_id=callback.message.business_connection_id,
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
) -> None:
    async def start_dialog(
        message: Message,
        dialog_manager: DialogManager,
        notifier: StaleIntentNotifier,
    ) -> None:
        await notifier.safe_delete_message(message)
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
    current_state = await state.get_state()
    if current_state is None:
        return
    logger.info("Cancelling state %s", current_state)
    await state.clear()
    await message.reply(
        "Диалог прекращён, данные удалены",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
    )


def register_cancel_state(
    router: Router,
    *,
    commands: str | Sequence[str] = "cancel",
) -> None:
    router.message.register(cancel_state, Command(commands=commands))
