"""Import entrypoints in a fresh interpreter to catch import-time wiring errors."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable, Mapping

import pytest

__all__ = ["smoke_import", "smoke_imports_test"]

_IMPORT_SNIPPET = "import importlib, sys; importlib.import_module(sys.argv[1])"


def smoke_import(
    module: str,
    *,
    env: Mapping[str, str] | None = None,
    timeout: float = 30,
) -> None:
    """Import module in a new interpreter; AssertionError carries its stderr.

    `env` is merged over os.environ: entrypoints read config on import.
    """
    result = subprocess.run(
        [sys.executable, "-c", _IMPORT_SNIPPET, module],
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        msg = f"import {module} failed (exit {result.returncode}):\n{result.stderr}"
        raise AssertionError(msg)


def smoke_imports_test(
    *modules: str,
    env: Mapping[str, str] | None = None,
) -> Callable[[str], None]:
    """Parametrized pytest test over modules: `test_entrypoints = smoke_imports_test(...)`."""

    @pytest.mark.parametrize("module", modules)
    def _test(module: str) -> None:
        smoke_import(module, env=env)

    return _test
