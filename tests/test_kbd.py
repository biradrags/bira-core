from bira_core.kbd import wrap_by_label_width


def test_wrap_short_labels_pack_together() -> None:
    labels = ["A", "B", "C"]
    rows = wrap_by_label_width(labels, row_chars=30)
    assert rows == [[0, 1, 2]]


def test_wrap_long_label_separate_row() -> None:
    labels = ["short", "this label is definitely too long for one row"]
    rows = wrap_by_label_width(labels, row_chars=10)
    assert len(rows) == 2
    assert rows[0] == [0]
    assert rows[1] == [1]
