from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "bira_core"

CORE_PURE = ["log", "dt", "kbd", "db", "redis", "forum", "protect", "payments", "web"]
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
