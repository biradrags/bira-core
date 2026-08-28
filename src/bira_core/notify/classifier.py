from __future__ import annotations

from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)

from bira_core.notify.delivery import DeliveryFailure, FailureCategory

_BLOCKED_BAD_REQUEST_MARKERS: tuple[str, ...] = (
    "business_peer_usage_missing",
    "user is deactivated",
)
_NOT_FOUND_BAD_REQUEST_MARKERS: tuple[str, ...] = (
    "chat not found",
    "message thread not found",
)


def classify_aiogram(exc: BaseException) -> DeliveryFailure:
    raw = str(exc)
    if isinstance(exc, TelegramForbiddenError):
        return DeliveryFailure(category=FailureCategory.BLOCKED, raw=raw)
    if isinstance(exc, TelegramRetryAfter):
        return DeliveryFailure(
            category=FailureCategory.FLOOD_WAIT,
            raw=raw,
            retry_after=exc.retry_after,
        )
    if isinstance(exc, TelegramBadRequest):
        raw_lower = raw.lower()
        if any(marker in raw_lower for marker in _BLOCKED_BAD_REQUEST_MARKERS):
            return DeliveryFailure(category=FailureCategory.BLOCKED, raw=raw)
        if any(marker in raw_lower for marker in _NOT_FOUND_BAD_REQUEST_MARKERS):
            return DeliveryFailure(category=FailureCategory.CHAT_NOT_FOUND, raw=raw)
        return DeliveryFailure(category=FailureCategory.OTHER, raw=raw)
    return DeliveryFailure(category=FailureCategory.OTHER, raw=raw)
