#!/usr/bin/env python3
"""Per-extra import smoke: карта модулей строится обходом пакета, не руками.

Ручной список отставал от дерева и однажды пропустил три падающих фасада -
поэтому здесь только корни, а состав берётся из pkgutil.walk_packages.
"""

from __future__ import annotations

import argparse
import importlib
import pkgutil
import sys

# Корни, которые обязаны импортироваться при установке данного extra.
EXTRA_ROOTS: dict[str, list[str]] = {
    "core": [],
    "db": ["bira_core.db"],
    "di": ["bira_core.di"],
    "redis": ["bira_core.redis"],
    "tgbot": ["bira_core.tgbot", "bira_core.notify"],
    "dialogs": ["bira_core.tgbot.dialogs"],
    "max": ["bira_core.maxbot"],
    "payments": ["bira_core.payments"],
    "protect": ["bira_core.protect"],
    "alembic": ["bira_core.db.alembic"],
    "testing": [],
}

# Подмодули, живущие за ДРУГИМ extra: при установке только своего они законно
# недоступны (bira_core.di.db нужен [db], bira_core.tgbot.dialogs - [dialogs]).
EXTRA_SKIP: dict[str, tuple[str, ...]] = {
    "di": ("bira_core.di.db", "bira_core.di.redis"),
    "tgbot": ("bira_core.tgbot.dialogs",),
    "max": ("bira_core.maxbot.di",),
}

# Символы, которые потребитель реально импортирует по документации.
ATTR_CHECKS: dict[str, list[tuple[str, str]]] = {
    "core": [
        ("bira_core.web", "CRON_PORT"),
        ("bira_core.web", "create_cron_app"),
        ("bira_core.web", "fly_src_gate"),
        ("bira_core.web", "health_handler"),
        ("bira_core.log", "setup_logging"),
        ("bira_core.kbd", "wrap_by_label_width"),
        ("bira_core.tls", "russian_trusted_ssl_context"),
        ("bira_core.forum", "ForumTopics"),
        ("bira_core.auth", "is_superadmin"),
        ("bira_core.notify", "Alerts"),
        ("bira_core.notify", "MessageSender"),
        ("bira_core.notify", "split_message"),
        ("bira_core.protect", "FloodGuard"),
    ],
    "db": [("bira_core.db", "BaseDAO"), ("bira_core.db", "build_url")],
    "di": [("bira_core.di", "warm_up")],
    "redis": [("bira_core.redis", "make_redis_client")],
    "tgbot": [
        ("bira_core.tgbot.web_bootstrap", "create_app"),
        ("bira_core.notify.send", "safe_send"),
        ("bira_core.tgbot", "cancel_command"),
        ("bira_core.tgbot", "IsLikelyBot"),
    ],
    "dialogs": [("bira_core.tgbot.dialogs", "register_stale_intent")],
    "max": [
        ("bira_core.maxbot", "run_long_polling"),
        ("bira_core.maxbot", "register_stale_intent"),
    ],
    "payments": [("bira_core.payments", "TBankClient")],
    "protect": [("bira_core.protect.rate_limit", "RateLimiter")],
    "alembic": [("bira_core.db", "run_migrations")],
    "testing": [],
}


# Чистые фасады: без единого стороннего пакета, импортируются при голой установке.
PURE_FACADES = ("log", "dt", "kbd", "tls", "auth", "web", "forum", "notify", "protect", "testing")

# Фасад слоя импортируется ⇔ стоит его extra; без него - ImportError с подсказкой.
EXTRA_FACADES = {
    "db": "db",
    "di": "di",
    "redis": "redis",
    "tgbot": "tgbot",
    "maxbot": "max",
    "payments": "payments",
}


def core_facades() -> list[str]:
    """Чистые фасады: обязаны импортироваться без единого extra."""
    return ["bira_core"] + [f"bira_core.{name}" for name in PURE_FACADES]


def check_facade_hint(name: str, extra: str) -> None:
    """Без своего extra фасад обязан кидать ImportError с командой установки."""
    try:
        importlib.import_module(f"bira_core.{name}")
    except ImportError as e:
        notes = " ".join(getattr(e, "__notes__", []))
        if f"bira-core[{extra}]" not in notes:
            raise AssertionError(
                f"bira_core.{name}: ImportError без подсказки про [{extra}]"
            ) from e


def submodules(root: str) -> list[str]:
    module = importlib.import_module(root)
    path = getattr(module, "__path__", None)
    if path is None:
        return [root]
    return [root] + [
        info.name for info in pkgutil.walk_packages(path, prefix=f"{root}.")
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("extra", choices=sorted(EXTRA_ROOTS))
    extra = parser.parse_args().extra

    for name in core_facades():
        importlib.import_module(name)

    for name, required_extra in EXTRA_FACADES.items():
        if required_extra == extra:
            importlib.import_module(f"bira_core.{name}")
        else:
            check_facade_hint(name, required_extra)

    skip = EXTRA_SKIP.get(extra, ())
    for root in EXTRA_ROOTS[extra]:
        for name in submodules(root):
            if name.startswith(skip):
                continue
            importlib.import_module(name)

    for module_name, attr in ATTR_CHECKS[extra]:
        getattr(importlib.import_module(module_name), attr)

    print(f"smoke ok: {extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
