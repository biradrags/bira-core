"""Static check that aiogram_dialog keyboards fit the Telegram callback_data limit."""

from __future__ import annotations

from collections.abc import Iterator

from aiogram_dialog import Dialog, Window
from aiogram_dialog.api.entities.stack import id_to_str
from aiogram_dialog.utils import CB_SEP
from aiogram_dialog.widgets.kbd import Button, Group, Keyboard, ListGroup
from aiogram_dialog.widgets.kbd.base import Or

__all__ = ["assert_callback_data_fits"]

_TELEGRAM_CALLBACK_LIMIT = 64
# aiogram_dialog дописывает intent_id + CB_SEP; intent_id - base62 от new_int_id() < 1e10
_INTENT_RESERVE = len(id_to_str(10**10 - 1)) + len(CB_SEP)
_DEFAULT_ITEM_ID = "9" * 10


def assert_callback_data_fits(
    *dialogs: Dialog,
    item_id: str = _DEFAULT_ITEM_ID,
) -> None:
    """Walk keyboards without rendering; `item_id` (longest real getter key) fills item slots."""
    too_long: list[str] = []
    for dialog in dialogs:
        for state, window in dialog.windows.items():
            if not isinstance(window, Window):
                continue
            for data in _callbacks(window.keyboard, item_id, ""):
                size = len(data.encode()) + _INTENT_RESERVE
                if size > _TELEGRAM_CALLBACK_LIMIT:
                    too_long.append(f"{state.state}: {size} > 64 bytes ({data!r})")
    if too_long:
        raise AssertionError("callback_data over limit:\n" + "\n".join(too_long))


def _callbacks(widget: object, item_id: str, prefix: str) -> Iterator[str]:
    if isinstance(widget, ListGroup):
        nested = f"{prefix}{widget.widget_id}:{item_id}:"
        for child in widget.buttons:
            yield from _callbacks(child, item_id, nested)
        return
    if isinstance(widget, Or):
        for child in widget.widgets:
            yield from _callbacks(child, item_id, prefix)
        return
    # без return: у ScrollingGroup ещё свои кнопки пейджера "<id>:<page>"
    if isinstance(widget, Group):
        for child in widget.buttons:
            yield from _callbacks(child, item_id, prefix)
    if not isinstance(widget, Keyboard) or widget.widget_id is None:
        return
    # свой _process_item_callback - кнопки вида "<id>:<item>" (Select, пейджеры, Counter)
    if type(widget)._process_item_callback is not Keyboard._process_item_callback:
        yield f"{prefix}{widget.widget_id}:{item_id}"
    elif isinstance(widget, Button):
        yield f"{prefix}{widget.widget_id}"
