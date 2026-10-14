from bira_core.tgbot.emoji import emoji_id, tg_emoji


def test_known_glyph_has_numeric_id() -> None:
    eid = emoji_id("✅")
    assert eid is not None
    assert eid.isdigit()


def test_unknown_glyph_has_no_id() -> None:
    assert emoji_id("no-such-glyph") is None


def test_tg_emoji_wraps_known_glyph() -> None:
    eid = emoji_id("✅")
    assert tg_emoji("✅") == f'<tg-emoji emoji-id="{eid}">✅</tg-emoji>'


def test_tg_emoji_falls_back_to_escaped_glyph() -> None:
    assert tg_emoji("<b>") == "&lt;b&gt;"


def test_pack_ships_with_package() -> None:
    from bira_core.tgbot.emoji import _pack

    pack = _pack()
    assert len(pack) >= 900
    assert all(value.isdigit() for value in pack.values())
