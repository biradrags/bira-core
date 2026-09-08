"""Semantic rule checks that Ruff cannot express."""

from __future__ import annotations

import re
import sys
from collections.abc import Iterator
from pathlib import Path

_MONEY = (
    r"(?:price|amount|balance|cost|total|subtotal|payment|payout|refund|"
    r"sum|fee|tariff|stars|сумм|стоим|баланс|цена|оплат|выплат|доля)"
)
_MONEY_ANNOT = re.compile(rf"\b\w*{_MONEY}\w*\s*:\s*float\b", re.IGNORECASE)
_MONEY_CAST = re.compile(rf"\bfloat\(\s*[^)]*{_MONEY}", re.IGNORECASE)
_LAYER_IMPORT = re.compile(r"\b(?:from|import)\s+\S*\b(?:tgbot|maxbot)\b")
_SESSION = re.compile(r"\b(?:ClientSession|AsyncClient)\s*\(")
_BROAD_EXCEPT = re.compile(r"\bexcept\s+BaseException\b")
_DAO_RAISE = re.compile(r"^\s*raise\b")
_HTML_FSTR = re.compile(r"""f(['"]).*<[a-zA-Z][^>]*>.*\{[^}]+\}.*\1""")
_LOG_SETUP = (
    re.compile(r"\blogging\.basicConfig\s*\("),
    re.compile(r"\blogging\.config\.dictConfig\s*\("),
    re.compile(r"\bcolorlog\b"),
)
_APP_ENV_OS = re.compile(
    r"""\bos\.(?:environ\.get|getenv|environ\[)\s*\(?\s*['"]APP_ENV['"]"""
)
_TX_WRITE = re.compile(
    r"\bawait\s+(?:self\.)?\w*dao\.\w+\.(?:create|upsert|insert|add|save|set|"
    r"update|delete|remove|mark|claim|toggle|link|expire|bump|incr)\w*\s*\("
)
_TX_CLOSE = re.compile(r"\b(?:release_current_dao|commit|release|rollback)\s*\(")
_TX_NETWORK = re.compile(r"\bawait\s+(?:self\.)?(?:bot|notifier)\.")
_TX_BOUNDARY = re.compile(r"^\s*(?:async\s+def|def|class)\s")
_ASSERT_NONE = re.compile(r"\bassert\s+[\w.\[\]'\"]+\s+is\s+not\s+None\b")
_TYPE_IGNORE_BARE = re.compile(r"#\s*type:\s*ignore\[[a-z0-9_,-]+\]\s*$")
_SKIP_DIRS = {
    ".venv",
    ".git",
    "node_modules",
    "migrations",
    "versions",
    "__pycache__",
    ".cursor",
    ".mypy_cache",
    ".ruff_cache",
}


def _in_layer(path: Path, *names: str) -> bool:
    return bool(set(path.parts) & set(names))


def _money(path: Path, line: str) -> bool:
    return bool(_MONEY_ANNOT.search(line) or _MONEY_CAST.search(line))


def _layer_import(path: Path, line: str) -> bool:
    return _in_layer(path, "core", "dto", "dao") and bool(_LAYER_IMPORT.search(line))


def _per_call_session(path: Path, line: str) -> bool:
    if "di" in path.parts or path.stem == "di":
        return False
    return bool(_SESSION.search(line))


def _broad_except(path: Path, line: str) -> bool:
    return bool(_BROAD_EXCEPT.search(line))


def _dao_raise(path: Path, line: str) -> bool:
    return _in_layer(path, "dao") and bool(_DAO_RAISE.search(line))


def _html_escape(path: Path, line: str) -> bool:
    if "html.escape" in line:
        return False
    return bool(_HTML_FSTR.search(line))


def _skip_scripts_and_tests(path: Path) -> bool:
    return (
        "scripts" in path.parts
        or "tests" in path.parts
        or path.name.startswith("test_")
    )


def _log_setup(path: Path, line: str) -> bool:
    if _skip_scripts_and_tests(path):
        return False
    if line.lstrip().startswith("#"):
        return False
    return any(p.search(line) for p in _LOG_SETUP)


def _app_env_source(path: Path, line: str) -> bool:
    if _skip_scripts_and_tests(path):
        return False
    return bool(_APP_ENV_OS.search(line))


def _assert_none(path: Path, line: str) -> bool:
    return not _skip_scripts_and_tests(path) and bool(_ASSERT_NONE.search(line))


def _type_ignore_why(path: Path, line: str) -> bool:
    return bool(_TYPE_IGNORE_BARE.search(line))


def _tx_network_hits(lines: list[str]) -> list[tuple[int, str, int]]:
    hits: list[tuple[int, str, int]] = []
    pending = 0
    for i, line in enumerate(lines, 1):
        if _TX_BOUNDARY.search(line):
            pending = 0
        if _TX_CLOSE.search(line):
            pending = 0
            continue
        if _TX_WRITE.search(line):
            pending = i
            continue
        if pending and _TX_NETWORK.search(line):
            hits.append((i, line, pending))
    return hits


_CHECKS = (
    ("money-float", "money-ok", _money),
    ("layer-import", "layer-import-ok", _layer_import),
    ("per-call-session", "per-call-session-ok", _per_call_session),
    ("broad-except", "broad-except-ok", _broad_except),
    ("html-escape", "html-escape-ok", _html_escape),
    ("dao-raise", "dao-raise-ok", _dao_raise),
    ("log-setup", "log-setup-ok", _log_setup),
    ("app-env-source", "app-env-ok", _app_env_source),
    ("assert-none", "assert-none-ok", _assert_none),
    ("type-ignore-why", "type-ignore-ok", _type_ignore_why),
)


def _iter_py(roots: list[str]) -> Iterator[Path]:
    for root in roots:
        for p in Path(root).rglob("*.py"):
            if _SKIP_DIRS & set(p.parts):
                continue
            posix = p.as_posix()
            if "/tests/" in posix or p.name.startswith("test_"):
                continue
            yield p


def main(argv: list[str] | None = None) -> int:
    """CLI entry: scan paths and print semantic rule violations."""
    args = argv if argv is not None else sys.argv
    roots = args[1:] or ["."]
    hits: list[tuple[str, Path, int, str]] = []
    for p in _iter_py(roots):
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            for check_id, token, predicate in _CHECKS:
                if f"# {token}" in line:
                    continue
                if predicate(p, line):
                    hits.append((check_id, p, i, line.strip()))
        for i, line, wline in _tx_network_hits(lines):
            if "# tx-network-ok" in line:
                continue
            hits.append(("tx-network", p, i, f"{line.strip()} (write at :{wline})"))
    if hits:
        print(
            "rules_check FAIL (suppress a verified false positive with `# <token>-ok`):"
        )
        for check_id, p, i, line in sorted(hits, key=lambda h: (h[0], str(h[1]), h[2])):
            print(f"  [{check_id}] {p}:{i}: {line}")
        return 1
    print("rules_check ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
