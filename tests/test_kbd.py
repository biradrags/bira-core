from bira_core.kbd import _wrap_indices, wrap_by_label_width


def test_wrap_short_labels_pack_together() -> None:
    labels = ["A", "B", "C"]
    rows = _wrap_indices(labels, row_chars=30)
    assert rows == [[0, 1, 2]]


def test_wrap_long_label_separate_row() -> None:
    labels = ["short", "this label is definitely too long for one row"]
    rows = _wrap_indices(labels, row_chars=10)
    assert len(rows) == 2
    assert rows[0] == [0]
    assert rows[1] == [1]


def test_wrap_by_label_width_buttons() -> None:
    class Btn:
        def __init__(self, text: str) -> None:
            self.text = text

    buttons = [Btn("A"), Btn("B"), Btn("long label")]
    rows = wrap_by_label_width(buttons, 10)
    assert len(rows) == 2
