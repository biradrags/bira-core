"""bira-core: fleet plumbing for aiogram bots."""

from typing import Any

from bira_core.log import RedactionFilter, setup_logging

__all__: list[str] = [
    "Alerts",
    "Base",
    "BaseDAO",
    "DbDsn",
    "DbProvider",
    "IsSuperAdmin",
    "MessageSender",
    "NotifierProvider",
    "RedactionFilter",
    "RedisProvider",
    "build_url",
    "create_app",
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
    "is_superadmin": ("bira_core.tg", "is_superadmin"),
    "IsSuperAdmin": ("bira_core.tg", "IsSuperAdmin"),
    "register_error_handlers": ("bira_core.tg", "register_error_handlers"),
    "safe_send": ("bira_core.notify", "safe_send"),
    "MessageSender": ("bira_core.notify", "MessageSender"),
    "Alerts": ("bira_core.notify", "Alerts"),
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
