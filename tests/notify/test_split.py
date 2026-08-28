from bira_core.notify.split import split_message


def test_split_numbering() -> None:
    text = "a\n" + "b" * 5000
    parts = split_message(text, limit=4096, numbering=True)
    assert len(parts) >= 2
    assert parts[0].startswith("[1/")


def test_split_hard_cut_long_line() -> None:
    text = "x" * 5000
    parts = split_message(text, limit=4096, numbering=False)
    assert all(len(p) <= 4096 for p in parts)
    assert sum(len(p) for p in parts) >= 5000
