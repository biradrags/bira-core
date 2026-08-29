"""bira-core: fleet plumbing for aiogram bots."""

from typing import Any

from bira_core.log import (
    LogfmtFormatter,
    ProbeAccessFilter,
    RedactionFilter,
    setup_logging,
)

__all__: list[str] = [
    "CRON_PORT",
    "Alerts",
    "Base",
    "BaseDAO",
    "DbDsn",
    "DbProvider",
    "IsSuperAdmin",
    "LogfmtFormatter",
    "MessageSender",
    "NotifierProvider",
    "ProbeAccessFilter",
    "RedactionFilter",
    "RedisProvider",
    "attach_cron_site",
    "build_url",
    "create_app",
    "create_cron_app",
    "cron_protocol",
    "fly_src_gate",
    "is_superadmin",
    "register_error_handlers",
    "run_polling",
    "run_webhook",
    "safe_send",
    "setup_logging",
    "warm_up",
]

_EXPORTS: dict[str, tuple[str, str]] = {
    "build_url": ("bira_core.db", "build_url"),
    "DbDsn": ("bira_core.db", "DbDsn"),
    "Base": ("bira_core.db", "Base"),
    "BaseDAO": ("bira_core.db", "BaseDAO"),
    "is_superadmin": ("bira_core.tgbot", "is_superadmin"),
    "IsSuperAdmin": ("bira_core.tgbot", "IsSuperAdmin"),
    "register_error_handlers": ("bira_core.tgbot", "register_error_handlers"),
    "safe_send": ("bira_core.notify", "safe_send"),
    "MessageSender": ("bira_core.notify", "MessageSender"),
    "Alerts": ("bira_core.notify", "Alerts"),
    "CRON_PORT": ("bira_core.web", "CRON_PORT"),
    "attach_cron_site": ("bira_core.web", "attach_cron_site"),
    "create_cron_app": ("bira_core.web", "create_cron_app"),
    "fly_src_gate": ("bira_core.web", "fly_src_gate"),
    "cron_protocol": ("bira_core.web", "cron_protocol"),
    "create_app": ("bira_core.web", "create_app"),
    "run_webhook": ("bira_core.web", "run_webhook"),
    "run_polling": ("bira_core.web", "run_polling"),
    "DbProvider": ("bira_core.di", "DbProvider"),
    "RedisProvider": ("bira_core.di", "RedisProvider"),
    "NotifierProvider": ("bira_core.di", "NotifierProvider"),
    "warm_up": ("bira_core.di", "warm_up"),
}


def __getattr__(name: str) -> Any:
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr = target
    try:
        module = __import__(module_name, fromlist=[attr])
    except ImportError as e:
        if module_name.startswith("bira_core.db"):
            e.add_note("pip install bira-core[db]")
        elif module_name.startswith("bira_core.di"):
            e.add_note("pip install bira-core[di]")
        raise
    return getattr(module, attr)
