"""Timezone conversion utilities."""

from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "UTC"


def get_timezone(timezone_name: str) -> ZoneInfo:
    """Resolve timezone name with UTC fallback."""
    try:
        return ZoneInfo(timezone_name)
    except KeyError:
        return ZoneInfo(DEFAULT_TIMEZONE)


def now_in_timezone(timezone_name: str | None = None) -> datetime:
    """Current time in named timezone."""
    tz = get_timezone(timezone_name or DEFAULT_TIMEZONE)
    return datetime.now(tz)


def convert_to_timezone(dt: datetime, timezone_name: str) -> datetime:
    """Convert aware or naive datetime to target timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(DEFAULT_TIMEZONE))
    target_tz = get_timezone(timezone_name)
    return dt.astimezone(target_tz)


def is_timezone_aware(dt: datetime) -> bool:
    """True when datetime carries a fixed UTC offset."""
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


def make_timezone_aware(
    dt: datetime, timezone_name: str = DEFAULT_TIMEZONE
) -> datetime:
    """Attach timezone to naive datetime."""
    if is_timezone_aware(dt):
        return dt
    tz = get_timezone(timezone_name)
    return dt.replace(tzinfo=tz)
