from dataclasses import dataclass
from enum import Enum
from typing import Any


class FailureCategory(Enum):
    BLOCKED = "blocked"
    FLOOD_WAIT = "flood_wait"
    CHAT_NOT_FOUND = "chat_not_found"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class DeliveryFailure:
    category: FailureCategory
    raw: str
    retry_after: int | None = None


@dataclass(slots=True)
class DeliveryResult:
    sent: Any | None = None
    failure: DeliveryFailure | None = None
