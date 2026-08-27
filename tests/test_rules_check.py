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


def test_module_entrypoint(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n")
    proc = subprocess.run(
        [sys.executable, "-m", "bira_core.rules_check", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
