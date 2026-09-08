from datetime import datetime
from zoneinfo import ZoneInfo

from bira_core.dt.timezone import (
    convert_to_timezone,
    get_timezone,
    is_timezone_aware,
    make_timezone_aware,
)


def test_bad_timezone_falls_back_to_utc() -> None:
    assert get_timezone("Not/AZone") == ZoneInfo("UTC")


def test_naive_becomes_aware() -> None:
    naive = datetime(2024, 1, 1, 12, 0, 0)  # noqa: DTZ001
    aware = make_timezone_aware(naive, "Europe/Moscow")
    assert is_timezone_aware(aware)


def test_aware_stays_unchanged() -> None:
    aware = datetime(2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
    same = make_timezone_aware(aware, "Europe/Moscow")
    assert same == aware


def test_convert_to_timezone() -> None:
    naive = datetime(2024, 1, 1, 12, 0, 0)  # noqa: DTZ001
    converted = convert_to_timezone(naive, "Europe/Moscow")
    assert converted.tzinfo is not None
