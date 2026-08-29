#!/usr/bin/env python3
"""Per-extra import smoke: verify each optional dependency slice installs in isolation."""

from __future__ import annotations

import argparse
import importlib
import sys

SMOKES: dict[str, list[str]] = {
    "core": [
        "bira_core.log",
        "bira_core.dt",
        "bira_core.kbd",
        "bira_core.web",
    ],
    "db": ["bira_core.db"],
    "di": ["bira_core.di"],
    "redis": ["bira_core.redis"],
    "tgbot": ["bira_core.tgbot", "bira_core.notify.send"],
    "dialogs": ["bira_core.tgbot.dialogs"],
    "max": ["bira_core.maxbot"],
    "payments": ["bira_core.payments"],
    "protect": ["bira_core.protect"],
    "alembic": ["bira_core.db.alembic"],
}

ATTR_CHECKS: dict[str, list[tuple[str, str]]] = {
    "core": [
        ("bira_core.web", "CRON_PORT"),
        ("bira_core.web", "create_cron_app"),
    ],
    "db": [("bira_core.db", "BaseDAO")],
    "di": [("bira_core.di", "warm_up")],
    "redis": [("bira_core.redis", "make_redis_client")],
    "tgbot": [
        ("bira_core.web", "create_app"),
        ("bira_core.notify", "safe_send"),
    ],
    "dialogs": [("bira_core.tgbot.dialogs", "register_stale_intent")],
    "max": [("bira_core.maxbot", "run_long_polling")],
    "payments": [("bira_core.payments", "TBankClient")],
    "protect": [("bira_core.protect", "RateLimiter")],
    "alembic": [("bira_core.db", "run_migrations")],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("extra", choices=sorted(SMOKES))
    args = parser.parse_args()
    extra = args.extra

    for mod in SMOKES[extra]:
        importlib.import_module(mod)

    for mod_name, attr in ATTR_CHECKS.get(extra, []):
        mod = importlib.import_module(mod_name)
        getattr(mod, attr)

    print(f"smoke ok: {extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
