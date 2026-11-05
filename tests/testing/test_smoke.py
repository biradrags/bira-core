from pathlib import Path

import pytest

from bira_core.testing.smoke import smoke_import, smoke_imports_test


def _write_module(tmp_path: Path, name: str, body: str) -> dict[str, str]:
    (tmp_path / f"{name}.py").write_text(body)
    return {"PYTHONPATH": str(tmp_path)}


def test_smoke_import_ok() -> None:
    smoke_import("bira_core.testing.smoke")


def test_smoke_import_reports_stderr(tmp_path: Path) -> None:
    env = _write_module(tmp_path, "broken_entry", "from nowhere import missing\n")

    with pytest.raises(AssertionError, match="No module named 'nowhere'"):
        smoke_import("broken_entry", env=env)


def test_smoke_import_passes_env(tmp_path: Path) -> None:
    env = _write_module(tmp_path, "env_entry", "import os\nos.environ['BOT_TOKEN']\n")

    smoke_import("env_entry", env={**env, "BOT_TOKEN": "42:fake"})


def test_hanging_import_reported(tmp_path: Path) -> None:
    body = "import sys, time\nsys.stderr.write('connecting\\n'); sys.stderr.flush()\ntime.sleep(3)\n"
    env = _write_module(tmp_path, "hung_entry", body)

    with pytest.raises(AssertionError, match="hung over 0.5s:\nconnecting"):
        smoke_import("hung_entry", env=env, timeout=0.5)


test_entrypoints = smoke_imports_test("bira_core.testing.smoke", "json")
