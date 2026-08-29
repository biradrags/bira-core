from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "bira_core"

CORE_PURE = [
    "log",
    "dt",
    "kbd",
    "auth",
    "web",
    "forum",
    "protect.flood_guard",
    "protect.heuristics",
]
SDK_NAMES = {"aiogram", "aiogram_dialog", "maxo"}

# Top-level third-party import roots allowed per module (most specific key wins).
IMPORT_ALLOWLISTS: dict[str, frozenset[str]] = {
    "log": frozenset(),
    "dt": frozenset(),
    "kbd": frozenset(),
    "auth": frozenset(),
    "_tasks": frozenset(),
    "rules_check": frozenset(),
    "web": frozenset({"aiohttp"}),
    "forum": frozenset(),
    "protect.flood_guard": frozenset(),
    "protect.heuristics": frozenset(),
    "protect.rate_limit": frozenset({"redis"}),
    "protect": frozenset({"aiohttp"}),
    "db": frozenset({"sqlalchemy", "pydantic"}),
    "db.alembic": frozenset({"alembic", "sqlalchemy"}),
    "redis": frozenset({"redis"}),
    "di": frozenset({"dishka"}),
    "di.db": frozenset({"dishka", "sqlalchemy"}),
    "di.redis": frozenset({"dishka", "redis"}),
    "di.notify": frozenset({"dishka"}),
    "di.warmup": frozenset({"dishka"}),
    "payments": frozenset({"tenacity"}),
    "notify": frozenset(),
    "notify.split": frozenset(),
    "notify.bulk": frozenset(),
    "notify.delivery": frozenset(),
    "notify.alerts": frozenset(),
    "notify.send": frozenset({"aiogram"}),
    "notify.classifier": frozenset({"aiogram"}),
    "tgbot": frozenset({"aiogram"}),
    "tgbot.commands": frozenset({"aiogram"}),
    "tgbot.errors": frozenset({"aiogram"}),
    "tgbot.filters": frozenset({"aiogram"}),
    "tgbot.keyboards": frozenset({"aiogram"}),
    "tgbot.last": frozenset({"aiogram"}),
    "tgbot.media_transfer": frozenset({"aiogram"}),
    "tgbot.web_bootstrap": frozenset({"aiogram"}),
    "tgbot.dialogs": frozenset({"aiogram", "aiogram_dialog"}),
    "tgbot.dialogs.debug": frozenset({"aiogram", "aiogram_dialog"}),
    "tgbot.dialogs.errors": frozenset({"aiogram", "aiogram_dialog"}),
    "tgbot.dialogs.notifier": frozenset({"aiogram", "aiogram_dialog"}),
    "tgbot.dialogs.starters": frozenset({"aiogram", "aiogram_dialog"}),
    "tgbot.dialogs.widgets": frozenset({"aiogram", "aiogram_dialog"}),
    "maxbot": frozenset({"maxo", "dishka"}),
    "maxbot._errors": frozenset(),
    "maxbot.di": frozenset({"dishka", "maxo"}),
    "maxbot.polling": frozenset({"maxo"}),
    "maxbot.filters": frozenset({"maxo"}),
    "maxbot.notifier": frozenset({"maxo"}),
    "maxbot.dialogs": frozenset({"maxo"}),
    "maxbot.web": frozenset({"maxo"}),
    "maxbot.errors": frozenset({"maxo"}),
    "testing": frozenset(),
    "testing.db": frozenset({"sqlalchemy", "pytest"}),
    "testing.providers": frozenset({"aiogram", "dishka", "maxo"}),
}

STDLIB_ROOTS = sys.stdlib_module_names


def _module_key(path: Path) -> str:
    rel = path.relative_to(SRC).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _allowed_imports(module_key: str) -> frozenset[str]:
    parts = module_key.split(".")
    for end in range(len(parts), 0, -1):
        key = ".".join(parts[:end])
        if key in IMPORT_ALLOWLISTS:
            return IMPORT_ALLOWLISTS[key]
    return frozenset()


def _top_level_import_roots(tree: ast.Module) -> set[str]:
    roots: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _module_files(mod: str) -> list[Path]:
    path = SRC / mod.replace(".", "/")
    if path.is_dir():
        return list(path.rglob("*.py"))
    return [path.with_suffix(".py")]


def test_core_modules_free_of_sdk_toplevel_imports() -> None:
    for mod in CORE_PURE:
        for py in _module_files(mod):
            tree = ast.parse(py.read_text())
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root = alias.name.split(".")[0]
                        assert root not in SDK_NAMES, f"{py}: import {root}"
                elif isinstance(node, ast.ImportFrom) and node.module:
                    root = node.module.split(".")[0]
                    assert root not in SDK_NAMES, f"{py}: from {root}"


def test_modules_respect_import_allowlists() -> None:
    for py in SRC.rglob("*.py"):
        module_key = _module_key(py)
        allowed = _allowed_imports(module_key)
        for root in _top_level_import_roots(ast.parse(py.read_text())):
            if root in STDLIB_ROOTS or root == "bira_core":
                continue
            if root == "aiohttp":
                continue
            assert root in allowed, (
                f"{py} ({module_key}): top-level import {root!r} "
                f"not in allowlist {sorted(allowed)}"
            )


def test_web_pure_import_without_aiogram() -> None:
    code = """
import bira_core.web
assert bira_core.web.CRON_PORT == 8081
assert callable(bira_core.web.create_cron_app)
assert callable(bira_core.web.fly_src_gate)
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
        env={k: v for k, v in __import__("os").environ.items() if k != "VIRTUAL_ENV"},
    )
    if result.returncode != 0:
        pytest.fail(f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}")
