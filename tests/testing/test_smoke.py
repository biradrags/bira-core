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


def test_main_guard_not_executed(tmp_path: Path) -> None:
    body = "if __name__ == '__main__':\n    raise SystemExit(1)\n"
    env = _write_module(tmp_path, "guarded_entry", body)

    smoke_import("guarded_entry", env=env)


test_entrypoints = smoke_imports_test("bira_core.testing.smoke", "json")


def test_smoke_imports_test_is_parametrized() -> None:
    (mark,) = test_entrypoints.pytestmark  # type: ignore[attr-defined]  # ставит pytest.mark
    assert mark.args == ("module", ("bira_core.testing.smoke", "json"))
