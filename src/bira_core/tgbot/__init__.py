"""Telegram bot helpers facade."""

from bira_core.tgbot.commands import (
    CANCEL_COMMAND,
    CHAT_ID_COMMAND,
    cancel_command,
    chat_id_command,
    register_debug_commands,
)
from bira_core.tgbot.errors import register_error_handlers
from bira_core.tgbot.filters import IsServiceChat, IsSuperAdmin, is_superadmin
from bira_core.tgbot.keyboards import (
    CancelResetCD,
    ToMainMenuCD,
    build_cancel_back_keyboard,
    build_tbank_payment_keyboard,
    single_button_keyboard,
)
from bira_core.tgbot.last import setup_last_router
from bira_core.tgbot.media_transfer import (
    TransferResult,
    download_file_for_transfer,
    extract_content,
    get_media_label,
    transfer_message,
)

__all__ = [
    "CANCEL_COMMAND",
    "CHAT_ID_COMMAND",
    "CancelResetCD",
    "IsServiceChat",
    "IsSuperAdmin",
    "ToMainMenuCD",
    "TransferResult",
    "build_cancel_back_keyboard",
    "build_tbank_payment_keyboard",
    "cancel_command",
    "chat_id_command",
    "download_file_for_transfer",
    "extract_content",
    "get_media_label",
    "is_superadmin",
    "register_debug_commands",
    "register_error_handlers",
    "setup_last_router",
    "single_button_keyboard",
    "transfer_message",
]
