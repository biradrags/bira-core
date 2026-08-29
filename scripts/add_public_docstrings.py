from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("src/bira_core")

MODULE_DOCS: dict[str, str] = {
    "auth": "SDK-free superuser check shared by platform filters.",
    "_tasks": "Background task helpers for notifier TTL cleanup.",
    "db": "Database layer facade.",
    "db.alembic": "Alembic env helpers for fleet migrations.",
    "db.base": "SQLAlchemy declarative base.",
    "db.dao": "Generic async DAO base for Postgres.",
    "db.mixins": "Reusable ORM column mixins.",
    "db.queries": "Shared SQLAlchemy query helpers.",
    "db.settings": "Database connection settings DTO.",
    "db.url": "DSN builder for async Postgres.",
    "di": "Dishka provider facade.",
    "di.db": "Dishka database session provider.",
    "di.notify": "Dishka notifier provider.",
    "di.redis": "Dishka Redis client provider.",
    "di.warmup": "Container warm-up hooks.",
    "dt": "Datetime helpers facade.",
    "forum": "Forum topic routing facade.",
    "forum.service": "Forum topic ensure/send with per-key locking.",
    "kbd": "Keyboard row wrapping by label width.",
    "log.logfmt": "Logfmt formatter and probe access filter.",
    "log.redaction": "Public redaction API for logs and extras.",
    "log._internal": "Redaction engine implementation.",
    "maxbot": "MAX bot helpers facade.",
    "maxbot._errors": "Shared MAX message-gone error markers.",
    "maxbot.di": "Dishka MAX bot token provider.",
    "maxbot.dialogs": "MAX dialog cancel/delete helpers.",
    "maxbot.errors": "MAX stale-intent error handlers.",
    "maxbot.filters": "MAX platform filters.",
    "maxbot.notifier": "MAX dialog notifier with TTL feedback.",
    "maxbot.polling": "MAX long-polling bootstrap.",
    "maxbot.web": "MAX webhook helpers.",
    "notify": "Outbound messaging facade.",
    "notify.alerts": "Ops alert channel to Telegram.",
    "notify.bulk": "Bulk send with delivery classification.",
    "notify.classifier": "Delivery outcome classifier.",
    "notify.delivery": "Delivery result types.",
    "notify.send": "Safe single-message send helper.",
    "notify.split": "Plain-text message splitter with numbering.",
    "payments": "Payment provider facade.",
    "payments.tbank": "T-Bank payment client.",
    "protect.heuristics": "Prompt-injection heuristics for LLM calls.",
    "protect.rate_limit": "In-memory and Redis rate limiters.",
    "redis.client": "Async Redis client factory.",
    "testing": "Test fixtures facade.",
    "testing.db": "Postgres test database helpers.",
    "testing.providers": "Dishka test provider overrides.",
    "tgbot": "Telegram bot helpers facade.",
    "tgbot.commands": "Shared Telegram command handlers.",
    "tgbot.dialogs": "aiogram-dialog helpers facade.",
    "tgbot.dialogs.debug": "Router tree debug printer.",
    "tgbot.dialogs.errors": "Stale-intent cleanup for dialogs.",
    "tgbot.dialogs.notifier": "TG dialog notifier and delete helper.",
    "tgbot.dialogs.starters": "Dialog entry handlers registration.",
    "tgbot.dialogs.widgets": "Dialog widgets and cancel actions.",
    "tgbot.errors": "Unhandled update error registration.",
    "tgbot.filters": "Telegram platform filters.",
    "tgbot.keyboards": "Telegram keyboard builders.",
    "tgbot.last": "Stale callback button handlers.",
    "tgbot.media_transfer": "Download media for cross-bot transfer.",
    "tgbot.web_bootstrap": "Telegram webhook/polling bootstrap.",
    "web": "aiohttp web bootstrap facade.",
    "web.bootstrap": "Cron app factory and health route.",
    "web.cron": "Fly cron middleware and port constant.",
}


def module_key(path: Path) -> str:
    path = path.resolve()
    root = ROOT.resolve()
    rel = path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def module_doc(path: Path) -> str:
    key = module_key(path)
    return MODULE_DOCS.get(key, f"{key.split('.')[-1].replace('_', ' ')} helpers.")


def humanize(name: str) -> str:
    text = re.sub(r"(?<!^)(?=[A-Z])", " ", name).replace("_", " ").strip()
    return text[0].upper() + text[1:] if text else name


def doc_for_name(name: str, *, is_class: bool = False) -> str:
    if is_class:
        return f"{humanize(name)}."
    if name == "__init__":
        return "Initialize instance."
    if name.startswith("register_"):
        return f"Register {humanize(name.removeprefix('register_'))}."
    if name.startswith("make_"):
        return f"Build {humanize(name.removeprefix('make_'))}."
    if name.startswith("setup_"):
        return f"Configure {humanize(name.removeprefix('setup_'))}."
    if name.startswith("is_"):
        return f"Check {humanize(name.removeprefix('is_'))}."
    if name.startswith("get_"):
        return f"Return {humanize(name.removeprefix('get_'))}."
    return f"{humanize(name)}."


def module_docstring_node(tree: ast.Module) -> ast.Expr | None:
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                return node
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            break
    return None


def has_module_docstring(tree: ast.Module) -> bool:
    if not tree.body:
        return False
    first = tree.body[0]
    return isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)


def insert_module_docstring(path: Path) -> bool:
    text = path.read_text()
    tree = ast.parse(text)
    if has_module_docstring(tree):
        return False
    existing = module_docstring_node(tree)
    doc = existing.value.value if existing else module_doc(path)  # type: ignore[union-attr]
    lines = text.splitlines(keepends=True)
    if existing is not None:
        start = existing.lineno - 1
        end = existing.end_lineno or existing.lineno
        del lines[start:end]
        if start < len(lines) and lines[start].strip() == "":
            del lines[start]
    insert_at_line(lines, 1, f'"""{doc}"""\n\n')
    path.write_text("".join(lines))
    return True


def insert_at_line(lines: list[str], lineno: int, content: str) -> None:
    lines.insert(lineno - 1, content)


def find_def_end(lines: list[str], start_idx: int) -> int:
    for i in range(start_idx, len(lines)):
        if lines[i].rstrip().endswith(":"):
            return i
    return start_idx


def insert_symbol_docstring(path: Path, lineno: int, doc: str) -> bool:
    lines = path.read_text().splitlines(keepends=True)
    start = lineno - 1
    if start >= len(lines):
        return False
    end = start
    while end < len(lines):
        stripped = lines[end].rstrip()
        if stripped.endswith(": ..."):
            indent = re.match(r"^(\s*)", lines[end]).group(1) + "    "
            lines[end] = stripped.removesuffix(" ...") + "\n"
            insert_at_line(lines, end + 2, f'{indent}"""{doc}"""\n')
            insert_at_line(lines, end + 3, f"{indent}...\n")
            path.write_text("".join(lines))
            return True
        if stripped.endswith(":") and not stripped.endswith(": ..."):
            break
        end += 1
    end = find_def_end(lines, start)
    indent = re.match(r"^(\s*)", lines[end]).group(1) + "    "
    body_line = end + 1
    if body_line < len(lines) and '"""' in lines[body_line]:
        return False
    insert_at_line(lines, body_line + 1, f'{indent}"""{doc}"""\n')
    path.write_text("".join(lines))
    return True


def fix_d100_d104(path: Path) -> bool:
    return insert_module_docstring(path)


def fix_symbol(path: Path, lineno: int, code: str) -> bool:
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if getattr(node, "lineno", None) != lineno:
            continue
        if isinstance(node, ast.ClassDef):
            if ast.get_docstring(node):
                continue
            return insert_symbol_docstring(path, lineno, doc_for_name(node.name, is_class=True))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node):
                continue
            return insert_symbol_docstring(path, lineno, doc_for_name(node.name))
    return False


def ruff_violations() -> list[tuple[str, int, str]]:
    proc = subprocess.run(
        [
            "uv",
            "run",
            "ruff",
            "check",
            "src/bira_core",
            "--select",
            "D100,D101,D102,D103,D104,D107",
            "--output-format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    import json

    items: list[tuple[str, int, str]] = []
    if not proc.stdout.strip():
        return items
    for entry in json.loads(proc.stdout):
        items.append((entry["filename"], entry["location"]["row"], entry["code"]))
    return items


def main() -> None:
    for _ in range(500):
        violations = ruff_violations()
        if not violations:
            print("all D rules satisfied")
            return
        path_str, lineno, code = violations[0]
        path = Path(path_str)
        if code in {"D100", "D104"}:
            if not fix_d100_d104(path):
                print(f"failed {code} {path}")
                sys.exit(1)
        elif not fix_symbol(path, lineno, code):
            print(f"failed {code} {path}:{lineno}")
            sys.exit(1)
    print("iteration limit")
    sys.exit(1)


if __name__ == "__main__":
    main()
