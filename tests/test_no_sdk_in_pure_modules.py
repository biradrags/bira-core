from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "bira_core"

CORE_PURE = [
    "log",
    "dt",
    "kbd",
    "tls",
    "auth",
    "web",
    "notify.sender",
    "notify.alerts",
    "protect.flood_guard",
    "protect.heuristics",
]
SDK_NAMES = {"aiogram", "aiogram_dialog", "maxo"}


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
