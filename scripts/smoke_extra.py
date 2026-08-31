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
        "bira_core.forum",
        "bira_core.auth",
        "bira_core.protect.flood_guard",
        "bira_core.protect.heuristics",
        "bira_core.redis",
    ],
    "db": [
        "bira_core.db",
        "bira_core.db.base",
        "bira_core.db.dao",
        "bira_core.db.mixins",
        "bira_core.db.queries",
        "bira_core.db.settings",
        "bira_core.db.url",
    ],
    "di": [
        "bira_core.di",
        "bira_core.di.db",
        "bira_core.di.notify",
        "bira_core.di.redis",
        "bira_core.di.warmup",
    ],
    "redis": [
        "bira_core.redis",
        "bira_core.redis.client",
    ],
    "tgbot": [
        "bira_core.tgbot",
        "bira_core.tgbot.commands",
        "bira_core.tgbot.errors",
        "bira_core.tgbot.filters",
        "bira_core.tgbot.keyboards",
        "bira_core.tgbot.last",
        "bira_core.tgbot.media_transfer",
        "bira_core.tgbot.web_bootstrap",
        "bira_core.notify",
        "bira_core.notify.split",
        "bira_core.notify.bulk",
        "bira_core.notify.delivery",
    ],
    "dialogs": [
        "bira_core.tgbot.dialogs",
        "bira_core.tgbot.dialogs.debug",
        "bira_core.tgbot.dialogs.errors",
        "bira_core.tgbot.dialogs.notifier",
        "bira_core.tgbot.dialogs.starters",
        "bira_core.tgbot.dialogs.widgets",
    ],
    "max": [
        "bira_core.maxbot",
        "bira_core.maxbot.dialogs",
        "bira_core.maxbot.errors",
        "bira_core.maxbot.filters",
        "bira_core.maxbot.notifier",
        "bira_core.maxbot.polling",
        "bira_core.maxbot.web",
    ],
    "payments": [
        "bira_core.payments",
        "bira_core.payments.tbank",
    ],
    "protect": [
        "bira_core.protect",
        "bira_core.protect.flood_guard",
        "bira_core.protect.heuristics",
        "bira_core.protect.rate_limit",
    ],
    "alembic": [
        "bira_core.db.alembic",
    ],
}

ATTR_CHECKS: dict[str, list[tuple[str, str]]] = {
    "core": [
        ("bira_core.web", "CRON_PORT"),
        ("bira_core.web", "create_cron_app"),
        ("bira_core.web", "fly_src_gate"),
        ("bira_core.log", "setup_logging"),
        ("bira_core.kbd", "wrap_by_label_width"),
        ("bira_core.forum", "ForumTopics"),
        ("bira_core.auth", "is_superadmin"),
        ("bira_core.protect.flood_guard", "FloodGuard"),
    ],
    "db": [
        ("bira_core.db", "BaseDAO"),
        ("bira_core.db", "build_url"),
    ],
    "di": [
        ("bira_core.di", "warm_up"),
        ("bira_core.di", "DbProvider"),
    ],
    "redis": [
        ("bira_core.redis", "make_redis_client"),
    ],
    "tgbot": [
        ("bira_core.web", "create_app"),
        ("bira_core.notify", "safe_send"),
        ("bira_core.notify", "split_message"),
    ],
    "dialogs": [
        ("bira_core.tgbot.dialogs", "register_stale_intent"),
    ],
    "max": [
        ("bira_core.maxbot", "run_long_polling"),
    ],
    "payments": [
        ("bira_core.payments", "TBankClient"),
    ],
    "protect": [
        ("bira_core.protect", "RateLimiter"),
        ("bira_core.protect", "FloodGuard"),
    ],
    "alembic": [
        ("bira_core.db", "run_migrations"),
    ],
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
