"""Telegram keyboard builders."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

__all__ = [
    "build_tbank_payment_keyboard",
    "single_button_keyboard",
]


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
