from unittest.mock import MagicMock

import pytest

from bira_core.tgbot.dialogs.widgets import AdaptiveGroup, ProgressSteps


class Btn:
    def __init__(self, text: str) -> None:
        self.text = text


@pytest.mark.asyncio
async def test_progress_steps_render_text() -> None:
    widget = ProgressSteps(4, 2)
    text = await widget._render_text({}, MagicMock())
    assert text == "🟥🟥⬜⬜ 2/4"


def test_adaptive_group_wraps_by_label_width() -> None:
    buttons = [Btn("A"), Btn("B"), Btn("long label here")]
    group = AdaptiveGroup(*buttons, max_row_chars=10)

    wrapped = group._wrap_kbd(buttons)

    assert [[b.text for b in row] for row in wrapped] == [
        ["A", "B"],
        ["long label here"],
    ]
