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


def test_root_public_api_pinned() -> None:
    assert set(bira_core.__all__) == ROOT_EXPECTED


def test_submodule_exports_importable() -> None:
    package = importlib.import_module("bira_core")
    skip = {"bira_core.rules_check"}
    for module_info in pkgutil.walk_packages(package.__path__, prefix="bira_core."):
        if module_info.name in skip:
            continue
        mod = importlib.import_module(module_info.name)
        exports = getattr(mod, "__all__", None)
        if not exports:
            continue
        for name in exports:
            getattr(mod, name)
