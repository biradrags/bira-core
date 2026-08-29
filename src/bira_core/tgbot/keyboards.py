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
    """CallbackData to return user to the main menu."""


class CancelResetCD(CallbackData, prefix="cancel_reset"):
    """CallbackData to cancel and reset the current dialog."""


def build_cancel_back_keyboard() -> InlineKeyboardMarkup:
    """Back and cancel inline buttons for nested dialog steps."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data=ToMainMenuCD())
    builder.button(text="✖️ Отмена", callback_data=CancelResetCD())
    return builder.as_markup()


def build_tbank_payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    """Single URL button opening the T-Bank payment page."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить картой (T‑Bank)", url=payment_url)],
        ]
    )


def single_button_keyboard(
    text: str, callback_data: CallbackData
) -> InlineKeyboardMarkup:
    """One-row inline keyboard from text and CallbackData."""
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=callback_data)
    return builder.as_markup()
