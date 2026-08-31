"""Outbound messaging facade."""

from importlib import import_module
from typing import Any

from bira_core.notify.alerts import Alerts
from bira_core.notify.bulk import BulkReport, send_bulk
from bira_core.notify.delivery import DeliveryFailure, DeliveryResult, FailureCategory
from bira_core.notify.sender import MessageSender
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

_TGBOT_EXPORTS = {
    "classify_aiogram": "bira_core.notify.classifier",
    "deliver": "bira_core.notify.send",
    "safe_send": "bira_core.notify.send",
}


def __getattr__(name: str) -> Any:
    module_path = _TGBOT_EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        module = import_module(module_path)
    except ImportError as e:
        e.add_note("pip install bira-core[tgbot]")
        raise
    return getattr(module, name)
