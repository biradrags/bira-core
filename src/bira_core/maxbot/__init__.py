"""MAX bot helpers facade."""

from bira_core.maxbot.di import MaxBotProvider, create_max_dispatcher
from bira_core.maxbot.dialogs import cancel_delete
from bira_core.maxbot.errors import clear_stale_intent, register_stale_intent
from bira_core.maxbot.filters import IsSuperAdmin
from bira_core.maxbot.notifier import MaxDialogNotifier
from bira_core.maxbot.polling import (
    MaxPollingManager,
    SecondaryBotFactory,
    run_long_polling,
    stop_max_polling,
)
from bira_core.maxbot.web import drop_webhook_subscriptions

__all__ = [
    "IsSuperAdmin",
    "MaxBotProvider",
    "MaxDialogNotifier",
    "MaxPollingManager",
    "SecondaryBotFactory",
    "cancel_delete",
    "clear_stale_intent",
    "create_max_dispatcher",
    "drop_webhook_subscriptions",
    "register_stale_intent",
    "run_long_polling",
    "stop_max_polling",
]
