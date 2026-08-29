import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message, ReplyKeyboardRemove
from aiogram.utils.markdown import html_decoration as hd  # type: ignore[attr-defined]

logger = logging.getLogger(__name__)

CANCEL_COMMAND = BotCommand(command="cancel", description="отмена начатого диалога")
CHAT_ID_COMMAND = BotCommand(
    command="chat_id", description="узнать chat_id данного чата"
)

__all__ = [
    "CANCEL_COMMAND",
    "CHAT_ID_COMMAND",
    "cancel_command",
    "chat_id_command",
    "register_debug_commands",
]


async def chat_id_command(message: Message) -> None:
    text = f"🆔 ID этого чата: {hd.pre(str(message.chat.id))}"
    if message.message_thread_id:
        text += f"\n📝 ID этой подтемы: {hd.pre(str(message.message_thread_id))}"
    if message.reply_to_message and message.reply_to_message.from_user:
        text += (
            f"\n👤 ID {hd.bold(message.reply_to_message.from_user.full_name)}: "
            f"{hd.pre(str(message.reply_to_message.from_user.id))}"
        )
    if message.reply_to_message:
        text += f"\n💬 ID сообщения: {hd.pre(str(message.reply_to_message.message_id))}"
    if message.from_user:
        text += f"\n🫵 Ваш ID: {hd.pre(str(message.from_user.id))}"
    await message.reply(text, disable_notification=True, parse_mode=ParseMode.HTML)


async def cancel_command(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logger.info("cancelling state", extra={"state": current_state})
    await state.clear()
    await message.reply(
        "Диалог прекращён, данные удалены",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
    )


async def register_debug_commands(bot: Bot, superusers: list[int]) -> None:
    from aiogram.exceptions import TelegramBadRequest
    from aiogram.types import BotCommandScopeChat

    for chat_id in superusers:
        try:
            await bot.set_my_commands(
                commands=[CHAT_ID_COMMAND, CANCEL_COMMAND],
                scope=BotCommandScopeChat(chat_id=chat_id),
            )
        except TelegramBadRequest:
            logger.exception("error setting commands", extra={"chat_id": chat_id})
