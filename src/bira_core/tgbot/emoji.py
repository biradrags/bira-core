"""Анимированные кастом-эмодзи стандартного набора `RestrictedEmoji`: символ → custom_emoji_id.

Рендер нужен владелец бота с Premium (или юзернейм с Fragment), иначе клиент показывает символ.
"""

import html
import json
from functools import cache
from importlib.resources import files
from typing import cast

__all__ = [
    "emoji_id",
    "tg_emoji",
]


def emoji_id(glyph: str) -> str | None:
    """Id кастом-эмодзи символа для `<tg-emoji>` и `icon_custom_emoji_id`; None - символа нет в наборе."""
    return _pack().get(glyph)


def tg_emoji(glyph: str) -> str:
    """HTML `<tg-emoji>` для символа; символ без id в наборе - просто экранированный символ."""
    eid = emoji_id(glyph)
    if eid is None:
        return html.escape(glyph)
    return f'<tg-emoji emoji-id="{html.escape(eid)}">{html.escape(glyph)}</tg-emoji>'


@cache
def _pack() -> dict[str, str]:
    raw = (
        files("bira_core.tgbot").joinpath("emoji_pack.json").read_text(encoding="utf-8")
    )
    return cast(dict[str, str], json.loads(raw))
