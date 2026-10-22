import subprocess
import sys
from pathlib import Path

from bira_core.rules_check import main


def test_rules_check_flags_dao_raise(tmp_path: Path) -> None:
    dao_dir = tmp_path / "dao"
    dao_dir.mkdir()
    (dao_dir / "thing.py").write_text(
        "async def bad():\n    raise ValueError('nope')\n"
    )
    assert main(["rules_check", str(tmp_path)]) == 1


def test_rules_check_clean_tree(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("async def good():\n    return 1\n")
    assert main(["rules_check", str(tmp_path)]) == 0


def test_rules_check_flags_app_env_from_os_environ(tmp_path: Path) -> None:
    (tmp_path / "config.py").write_text(
        'import os\n\nenv = os.environ.get("APP_ENV", "development")\n'
    )
    assert main(["rules_check", str(tmp_path)]) == 1


def test_rules_check_allows_app_env_as_settings_field(tmp_path: Path) -> None:
    (tmp_path / "config.py").write_text(
        'app_env: Literal["development", "production"] = "development"\n'
    )
    assert main(["rules_check", str(tmp_path)]) == 0


def test_rules_check_flags_request_fromdishka_in_tgbot(tmp_path: Path) -> None:
    handlers = tmp_path / "tgbot" / "handlers"
    handlers.mkdir(parents=True)
    (handlers / "admin.py").write_text(
        "async def stats(dao: FromDishka[HolderDao]) -> None: ...\n"
    )
    assert main(["rules_check", str(tmp_path)]) == 1


def test_rules_check_allows_request_fromdishka_outside_tgbot(tmp_path: Path) -> None:
    routes = tmp_path / "api" / "routes"
    routes.mkdir(parents=True)
    (routes / "health.py").write_text(
        "async def health(dao: FromDishka[HolderDao]) -> None: ...\n"
    )
    (tmp_path / "tgbot").mkdir()
    (tmp_path / "tgbot" / "last.py").write_text(
        "async def last(texts: FromDishka[Texts]) -> None: ...\n"
    )
    assert main(["rules_check", str(tmp_path)]) == 0


def test_rules_check_flags_bare_type_ignore_with_space_after_comma(
    tmp_path: Path,
) -> None:
    (tmp_path / "thing.py").write_text(
        "x = foo()  # type: ignore[attr-defined, no-any-return]\n"
    )
    assert main(["rules_check", str(tmp_path)]) == 1


def test_rules_check_allows_type_ignore_with_reason(tmp_path: Path) -> None:
    (tmp_path / "thing.py").write_text(
        "x = foo()  # type: ignore[attr-defined, no-any-return]  # stub без типов\n"
    )
    assert main(["rules_check", str(tmp_path)]) == 0


def test_module_entrypoint(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n")
    proc = subprocess.run(
        [sys.executable, "-m", "bira_core.rules_check", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
