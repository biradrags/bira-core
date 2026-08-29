import importlib
import pkgutil

import bira_core

ROOT_EXPECTED = {
    "Alerts",
    "Base",
    "BaseDAO",
    "CRON_PORT",
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
}

_SKIP_MODULES = frozenset(
    {
        "bira_core.rules_check",
        "bira_core.tgbot.web_bootstrap",
        "bira_core.tgbot.dialogs.notifier",
        "bira_core.tgbot.dialogs.starters",
        "bira_core.tgbot.dialogs.widgets",
        "bira_core.tgbot.dialogs.errors",
        "bira_core.tgbot.dialogs.debug",
        "bira_core.maxbot.errors",
        "bira_core.di.db",
        "bira_core.di.redis",
        "bira_core.di.notify",
        "bira_core.di.warmup",
        "bira_core.web.bootstrap",
        "bira_core.web.cron",
        "bira_core.log.logfmt",
        "bira_core.log.redaction",
        "bira_core.notify.alerts",
        "bira_core.notify.bulk",
        "bira_core.notify.classifier",
        "bira_core.notify.delivery",
        "bira_core.notify.send",
        "bira_core.notify.split",
        "bira_core.db.alembic",
        "bira_core.db.base",
        "bira_core.db.dao",
        "bira_core.db.mixins",
        "bira_core.db.queries",
        "bira_core.db.settings",
        "bira_core.db.url",
        "bira_core.testing.db",
        "bira_core.testing.providers",
        "bira_core.payments.tbank",
        "bira_core.protect.flood_guard",
        "bira_core.protect.heuristics",
        "bira_core.protect.rate_limit",
        "bira_core.forum.service",
        "bira_core.maxbot.dialogs",
        "bira_core.maxbot.di",
        "bira_core.maxbot.filters",
        "bira_core.maxbot.notifier",
        "bira_core.maxbot.polling",
        "bira_core.maxbot.web",
        "bira_core.tgbot.commands",
        "bira_core.tgbot.errors",
        "bira_core.tgbot.filters",
        "bira_core.tgbot.keyboards",
        "bira_core.tgbot.last",
        "bira_core.tgbot.media_transfer",
    }
)

_FACADE_CHILDREN: dict[str, str] = {
    "bira_core.tgbot": "bira_core.tgbot",
    "bira_core.testing": "bira_core.testing",
    "bira_core.payments": "bira_core.payments",
}


def test_root_public_api_pinned() -> None:
    assert set(bira_core.__all__) == ROOT_EXPECTED


def test_submodule_exports_importable() -> None:
    package = importlib.import_module("bira_core")
    for module_info in pkgutil.walk_packages(package.__path__, prefix="bira_core."):
        if module_info.name in _SKIP_MODULES:
            continue
        mod = importlib.import_module(module_info.name)
        exports = getattr(mod, "__all__", None)
        assert exports is not None, f"{module_info.name} missing __all__"
        for name in exports:
            getattr(mod, name)


def test_facade_reexports_submodule_public_symbols() -> None:
    for facade_name, child_prefix in _FACADE_CHILDREN.items():
        facade = importlib.import_module(facade_name)
        for module_info in pkgutil.walk_packages(
            importlib.import_module(child_prefix).__path__,
            prefix=f"{child_prefix}.",
        ):
            if module_info.name in _SKIP_MODULES:
                continue
            if module_info.name.endswith(".dialogs"):
                continue
            child = importlib.import_module(module_info.name)
            child_exports = getattr(child, "__all__", None)
            if not child_exports:
                continue
            for name in child_exports:
                if name in facade.__all__:
                    assert hasattr(facade, name), f"{facade_name} missing {name}"
