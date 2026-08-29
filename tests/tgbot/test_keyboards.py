from bira_core.tgbot.keyboards import (
    ToMainMenuCD,
    build_cancel_back_keyboard,
    build_tbank_payment_keyboard,
    single_button_keyboard,
)


def test_build_cancel_back_keyboard() -> None:
    markup = build_cancel_back_keyboard()
    texts = [btn.text for row in markup.inline_keyboard for btn in row]
    assert "🔙 Назад" in texts
    assert "✖️ Отмена" in texts


def test_build_tbank_payment_keyboard() -> None:
    markup = build_tbank_payment_keyboard("https://pay.example/t")
    btn = markup.inline_keyboard[0][0]
    assert btn.url == "https://pay.example/t"
    assert "T‑Bank" in btn.text


def test_single_button_keyboard() -> None:
    markup = single_button_keyboard("Go", ToMainMenuCD())
    assert len(markup.inline_keyboard) == 1
    assert markup.inline_keyboard[0][0].text == "Go"
