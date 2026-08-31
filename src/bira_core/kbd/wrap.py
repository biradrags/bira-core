"""Row wrapping for inline keyboards by cumulative label width."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

DEFAULT_ROW_CHARS = 30

__all__ = [
    "DEFAULT_ROW_CHARS",
    "wrap_by_label_width",
]


def wrap_by_label_width(buttons: Sequence[Any], max_row_chars: int) -> list[list[Any]]:
    """Group flat buttons into rows so each row's labels fit max_row_chars.

    Кнопка длиннее лимита занимает строку целиком - обрезки не делаем.
    """
    rows: list[list[Any]] = []
    row: list[Any] = []
    row_len = 0
    for button in buttons:
        length = len(getattr(button, "text", "") or "")
        if row and row_len + length > max_row_chars:
            rows.append(row)
            row, row_len = [], 0
        row.append(button)
        row_len += length
    if row:
        rows.append(row)
    return rows
