"""MAX bot helpers facade."""

try:
    from bira_core.maxbot.dialogs import (
        MaxDialogNotifier,
        cancel_delete,
        clear_stale_intent,
        register_stale_intent,
    )
    from bira_core.maxbot.filters import IsSuperAdmin
    from bira_core.maxbot.web import drop_webhook_subscriptions
except ImportError as e:  # pragma: no cover - путь без extra [max]
    e.add_note("pip install bira-core[max]")
    raise

# MaxBotProvider / create_max_dispatcher требуют dishka - bira_core.maxbot.di ([max,di]).
__all__ = [
    "IsSuperAdmin",
    "MaxDialogNotifier",
    "cancel_delete",
    "clear_stale_intent",
    "drop_webhook_subscriptions",
    "register_stale_intent",
]
