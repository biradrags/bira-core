from typing import Any

from bira_core.notify.bulk import BulkReport, send_bulk
from bira_core.notify.delivery import DeliveryFailure, DeliveryResult, FailureCategory
from bira_core.notify.split import split_message

__all__ = [
    "Alerts",
    "BulkReport",
    "DeliveryFailure",
    "DeliveryResult",
    "FailureCategory",
    "MessageSender",
    "classify_aiogram",
    "deliver",
    "safe_send",
    "send_bulk",
    "split_message",
]

_TGBOT_EXPORTS = frozenset(
    {
        "Alerts",
        "MessageSender",
        "classify_aiogram",
        "deliver",
        "safe_send",
    }
)


def __getattr__(name: str) -> Any:
    if name not in _TGBOT_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    if name in {"Alerts", "MessageSender", "deliver", "safe_send"}:
        try:
            from bira_core.notify import send as send_mod
        except ImportError as e:
            e.add_note("pip install bira-core[tgbot]")
            raise
        if name == "Alerts":
            from bira_core.notify.alerts import Alerts

            return Alerts
        return getattr(send_mod, name)
    if name == "classify_aiogram":
        try:
            from bira_core.notify import classifier as classifier_mod
        except ImportError as e:
            e.add_note("pip install bira-core[tgbot]")
            raise
        return classifier_mod.classify_aiogram
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
