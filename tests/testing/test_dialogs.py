from operator import itemgetter

import pytest
from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, ListGroup, Row, Select, Url
from aiogram_dialog.widgets.text import Const, Format

from bira_core.testing.dialogs import assert_callback_data_fits

# intent_id (6) + CB_SEP (1) поверх данных виджета
INTENT_RESERVE = 7


class SG(StatesGroup):
    main = State()


def _dialog(*widgets: object) -> Dialog:
    return Dialog(Window(Const("t"), *widgets, state=SG.main))


def test_fitting_button_passes() -> None:
    dialog = _dialog(Row(Button(Const("b"), id="b" * (64 - INTENT_RESERVE))))

    assert_callback_data_fits(dialog)


def test_button_over_limit_by_one_byte_fails() -> None:
    dialog = _dialog(Button(Const("b"), id="b" * (65 - INTENT_RESERVE)))

    with pytest.raises(AssertionError, match="SG:main: 65 > 64 bytes"):
        assert_callback_data_fits(dialog)


def test_listgroup_item_id_counted_in_bytes() -> None:
    # 2 + 1 + 21 (кириллица) + 1 + 32 + 7 = 64
    dialog = _dialog(
        ListGroup(
            Button(Const("b"), id="x" * 32),
            id="lg",
            item_id_getter=itemgetter("key"),
            items="groups",
        )
    )

    assert_callback_data_fits(dialog, item_id="Казань-Сочи")
    with pytest.raises(AssertionError, match="65 > 64"):
        assert_callback_data_fits(dialog, item_id="Казань-Сочи!")


def test_select_uses_item_id_and_url_skipped() -> None:
    dialog = _dialog(
        Select(
            Format("{item}"),
            id="s" * 46,
            item_id_getter=str,
            items="items",
        ),
        Url(Const("u"), Const("https://example.com"), id="u" * 80),
    )

    assert_callback_data_fits(dialog)
    with pytest.raises(AssertionError, match="65 > 64"):
        assert_callback_data_fits(dialog, item_id="9" * 11)
