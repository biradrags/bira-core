from typing import Any

from bira_core.web.bootstrap import attach_cron_site, create_cron_app
from bira_core.web.cron import CRON_PORT, cron_protocol, fly_src_gate

__all__ = [
    "CRON_PORT",
    "attach_cron_site",
    "create_app",
    "create_cron_app",
    "cron_protocol",
    "fly_src_gate",
    "run_polling",
    "run_webhook",
]

_TGBOT_EXPORTS = frozenset({"create_app", "run_polling", "run_webhook"})


def __getattr__(name: str) -> Any:
    if name not in _TGBOT_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        from bira_core.tgbot import web_bootstrap as mod
    except ImportError as e:
        e.add_note("pip install bira-core[tgbot]")
        raise
    return getattr(mod, name)
