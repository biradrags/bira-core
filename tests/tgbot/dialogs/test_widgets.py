from unittest.mock import MagicMock

import pytest

from bira_core.kbd import wrap_by_label_width
from bira_core.tgbot.dialogs.widgets import AdaptiveGroup, ProgressSteps


@pytest.mark.asyncio
async def test_progress_steps_render_text() -> None:
    widget = ProgressSteps(4, 2)
    text = await widget._render_text({}, MagicMock())
    assert text == "🟥🟥⬜⬜ 2/4"


def test_adaptive_group_wrap_matches_kbd() -> None:
    labels = ["A", "B", "long label here"]
    expected = wrap_by_label_width(labels, row_chars=10)

    class Btn:
        def __init__(self, text: str) -> None:
            self.text = text

    buttons = [Btn(t) for t in labels]
    group = AdaptiveGroup(*buttons, max_row_chars=10)
    wrapped = group._wrap_kbd(buttons)
    assert len(wrapped) == len(expected)
