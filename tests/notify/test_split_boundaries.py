import pytest

from bira_core.notify.split import split_message

LIMIT = 4096


@pytest.mark.parametrize(
    "size",
    [
        LIMIT - 1,
        LIMIT,
        LIMIT + 1,
        404_713,  # ровно на переходе 99 -> 100 частей, префикс растёт до 3 цифр
        408_801,
        4_100_000,  # 4 цифры в номере
    ],
)
def test_no_part_exceeds_limit(size: int) -> None:
    parts = split_message("x" * size, limit=LIMIT, numbering=True)

    assert max(len(part) for part in parts) <= LIMIT


def test_numbering_matches_actual_part_count() -> None:
    parts = split_message("x" * 408_801, limit=LIMIT, numbering=True)

    total = len(parts)
    assert parts[0].startswith(f"[1/{total}] ")
    assert parts[-1].startswith(f"[{total}/{total}] ")
