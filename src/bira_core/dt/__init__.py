from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "UTC"


def get_timezone(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except KeyError:
        return ZoneInfo(DEFAULT_TIMEZONE)


def now_in_timezone(timezone_name: str | None = None) -> datetime:
    tz = get_timezone(timezone_name or DEFAULT_TIMEZONE)
    return datetime.now(tz)


def convert_to_timezone(dt: datetime, timezone_name: str) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(DEFAULT_TIMEZONE))
    target_tz = get_timezone(timezone_name)
    return dt.astimezone(target_tz)


def is_timezone_aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


def make_timezone_aware(
    dt: datetime, timezone_name: str = DEFAULT_TIMEZONE
) -> datetime:
    if is_timezone_aware(dt):
        return dt
    tz = get_timezone(timezone_name)
    return dt.replace(tzinfo=tz)
