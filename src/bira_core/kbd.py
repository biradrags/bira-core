"""Keyboard row wrapping by label width."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

DEFAULT_ROW_CHARS = 30

__all__ = [
    "DEFAULT_ROW_CHARS",
    "wrap_by_label_width",
]


def wrap_by_label_width(buttons: Sequence[Any], max_row_chars: int) -> list[list[Any]]:
    """Group flat buttons into rows by cumulative label width."""
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


def _wrap_indices(
    labels: Sequence[str], *, row_chars: int = DEFAULT_ROW_CHARS
) -> list[list[int]]:
    rows: list[list[int]] = []
    row: list[int] = []
    row_len = 0
    for idx, label in enumerate(labels):
        length = len(label)
        if row and row_len + length > row_chars:
            rows.append(row)
            row, row_len = [], 0
        row.append(idx)
        row_len += length
    if row:
        rows.append(row)
    return rows
