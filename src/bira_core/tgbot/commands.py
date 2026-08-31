"""Shared Telegram command handlers."""

import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message, ReplyKeyboardRemove

logger = logging.getLogger(__name__)

CANCEL_COMMAND = BotCommand(command="cancel", description="отмена начатого диалога")

__all__ = [
    "CANCEL_COMMAND",
    "cancel_command",
]


async def cancel_command(message: Message, state: FSMContext) -> None:
    """Clear FSM and remove reply keyboard when a dialog is active."""
    current_state = await state.get_state()
    if current_state is None:
        return
    logger.info("cancelling state", extra={"state": current_state})
    await state.clear()
    await message.reply(
        "Диалог прекращён, данные удалены",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
    )
