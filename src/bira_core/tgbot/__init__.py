"""Telegram bot helpers facade."""

try:
    from bira_core.tgbot.commands import CANCEL_COMMAND, cancel_command
    from bira_core.tgbot.errors import register_error_handlers
    from bira_core.tgbot.filters import IsSuperAdmin, is_superadmin
    from bira_core.tgbot.keyboards import (
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
except ImportError as e:  # pragma: no cover - путь без extra [tgbot]
    e.add_note("pip install bira-core[tgbot]")
    raise

__all__ = [
    "CANCEL_COMMAND",
    "IsSuperAdmin",
    "TransferResult",
    "build_tbank_payment_keyboard",
    "cancel_command",
    "download_file_for_transfer",
    "extract_content",
    "get_media_label",
    "is_superadmin",
    "register_error_handlers",
    "setup_last_router",
    "single_button_keyboard",
    "transfer_message",
]
