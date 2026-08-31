from aiogram.filters.callback_data import CallbackData

from bira_core.tgbot.keyboards import (
    build_tbank_payment_keyboard,
    single_button_keyboard,
)


class SampleCD(CallbackData, prefix="sample"):
    pass


def test_build_tbank_payment_keyboard() -> None:
    markup = build_tbank_payment_keyboard("https://pay.example/t")
    btn = markup.inline_keyboard[0][0]
    assert btn.url == "https://pay.example/t"
    assert "T‑Bank" in btn.text


def test_single_button_keyboard() -> None:
    markup = single_button_keyboard("Go", SampleCD())
    assert len(markup.inline_keyboard) == 1
    assert markup.inline_keyboard[0][0].text == "Go"
