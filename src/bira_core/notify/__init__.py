"""Outbound messaging facade - кросс-платформенная часть."""

from bira_core.notify.alerts import Alerts
from bira_core.notify.bulk import BulkReport, send_bulk
from bira_core.notify.delivery import DeliveryFailure, DeliveryResult, FailureCategory
from bira_core.notify.sender import MessageSender
from bira_core.notify.split import split_message

# aiogram-функции не ре-экспортируются - фасад обязан импортироваться без aiogram:
# deliver / safe_send - bira_core.notify.send, classify_aiogram - bira_core.notify.classifier.
__all__ = [
    "Alerts",
    "BulkReport",
    "DeliveryFailure",
    "DeliveryResult",
    "FailureCategory",
    "MessageSender",
    "send_bulk",
    "split_message",
]
