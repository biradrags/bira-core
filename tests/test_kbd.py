from bira_core.kbd.wrap import DEFAULT_ROW_CHARS, wrap_by_label_width


class Btn:
    def __init__(self, text: str) -> None:
        self.text = text


def _texts(rows: list[list[Btn]]) -> list[list[str]]:
    return [[b.text for b in row] for row in rows]


def test_wraps_when_row_budget_exceeded() -> None:
    buttons = [Btn("aaaa"), Btn("bbbb"), Btn("cccc")]

    rows = wrap_by_label_width(buttons, 8)

    assert _texts(rows) == [["aaaa", "bbbb"], ["cccc"]]


def test_button_longer_than_budget_takes_own_row() -> None:
    buttons = [Btn("A"), Btn("B"), Btn("long label here")]

    rows = wrap_by_label_width(buttons, 10)

    assert _texts(rows) == [["A", "B"], ["long label here"]]


def test_everything_fits_in_one_row() -> None:
    buttons = [Btn("A"), Btn("B")]

    assert _texts(wrap_by_label_width(buttons, DEFAULT_ROW_CHARS)) == [["A", "B"]]


def test_empty_input_yields_no_rows() -> None:
    assert wrap_by_label_width([], DEFAULT_ROW_CHARS) == []
