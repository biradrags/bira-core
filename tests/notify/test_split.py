from bira_core.notify.split import split_message
import pytest


@pytest.mark.parametrize("n", [4095, 4096, 4097, 5000, 12290, 50000])
def test_every_part_fits_limit_with_numbering(n: int) -> None:
    parts = split_message("x" * n, limit=4096, numbering=True)
    assert all(len(p) <= 4096 for p in parts)
    if len(parts) == 1:
        content = parts[0]
    else:
        content = "".join(p.split("] ", 1)[1] for p in parts)
    assert content == "x" * n


def test_split_5000_numbered_both_parts_fit() -> None:
    parts = split_message("x" * 5000, limit=4096, numbering=True)
    assert len(parts) == 2
    assert all(len(p) <= 4096 for p in parts)


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
