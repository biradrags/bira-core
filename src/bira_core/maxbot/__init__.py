"""MAX bot helpers facade."""

from importlib import import_module
from typing import Any

try:
    from bira_core.maxbot.dialogs import (
        MaxDialogNotifier,
        cancel_delete,
        clear_stale_intent,
        register_stale_intent,
    )
    from bira_core.maxbot.filters import IsSuperAdmin
    from bira_core.maxbot.polling import (
        MaxPollingManager,
        SecondaryBotFactory,
        run_long_polling,
        stop_max_polling,
    )
    from bira_core.maxbot.web import drop_webhook_subscriptions
except ImportError as e:  # pragma: no cover - путь без extra [max]
    e.add_note("pip install bira-core[max]")
    raise

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

_DI_EXPORTS = {
    "MaxBotProvider": "bira_core.maxbot.di",
    "create_max_dispatcher": "bira_core.maxbot.di",
}


def __getattr__(name: str) -> Any:
    module_path = _DI_EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        module = import_module(module_path)
    except ImportError as e:
        e.add_note("pip install bira-core[max,di]")
        raise
    return getattr(module, name)
