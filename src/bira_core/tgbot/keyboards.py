"""Telegram keyboard builders."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

__all__ = [
    "CancelResetCD",
    "ToMainMenuCD",
    "build_cancel_back_keyboard",
    "build_tbank_payment_keyboard",
    "single_button_keyboard",
]


class ToMainMenuCD(CallbackData, prefix="to_main_menu"):
    """To Main Menu C D."""


class CancelResetCD(CallbackData, prefix="cancel_reset"):
    """Cancel Reset C D."""


def build_cancel_back_keyboard() -> InlineKeyboardMarkup:
    """Build cancel back keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data=ToMainMenuCD())
    builder.button(text="✖️ Отмена", callback_data=CancelResetCD())
    return builder.as_markup()


def build_tbank_payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    """Build tbank payment keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить картой (T‑Bank)", url=payment_url)],
        ]
    )


def single_button_keyboard(
    text: str, callback_data: CallbackData
) -> InlineKeyboardMarkup:
    """Single button keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=callback_data)
    return builder.as_markup()
