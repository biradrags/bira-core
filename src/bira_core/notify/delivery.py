"""Delivery result types."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FailureCategory(Enum):
    """Delivery outcome buckets for bulk send and metrics."""

    BLOCKED = "blocked"
    FLOOD_WAIT = "flood_wait"
    CHAT_NOT_FOUND = "chat_not_found"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class DeliveryFailure:
    """Structured send failure with category and optional retry_after."""

    category: FailureCategory
    raw: str
    retry_after: int | None = None


@dataclass(slots=True)
class DeliveryResult:
    """Either sent payload or classified failure, never both."""

    sent: Any | None = None
    failure: DeliveryFailure | None = None
