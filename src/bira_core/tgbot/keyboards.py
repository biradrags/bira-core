from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ToMainMenuCD(CallbackData, prefix="to_main_menu"):
    pass


class CancelResetCD(CallbackData, prefix="cancel_reset"):
    pass


def build_cancel_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data=ToMainMenuCD())
    builder.button(text="✖️ Отмена", callback_data=CancelResetCD())
    return builder.as_markup()


def build_tbank_payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить картой (T‑Bank)", url=payment_url)],
        ]
    )


def single_button_keyboard(
    text: str, callback_data: CallbackData
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=callback_data)
    return builder.as_markup()
