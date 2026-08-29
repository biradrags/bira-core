from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path("src/bira_core")


def module_has_docstring(tree: ast.Module) -> bool:
    if not tree.body:
        return False
    first = tree.body[0]
    return (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    )


def insert_module_docstring(path: Path) -> bool:
    text = path.read_text()
    tree = ast.parse(text)
    if module_has_docstring(tree):
        return False
    name = path.stem.replace("_", " ")
    doc = f'"""{name.capitalize()} module."""\n\n'
    lines = text.splitlines(keepends=True)
    insert_at = 0
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            return False
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            insert_at = node.end_lineno or insert_at
        else:
            break
    lines.insert(insert_at, doc)
    path.write_text("".join(lines))
    return True


def main() -> None:
    count = 0
    for path in sorted(ROOT.rglob("*.py")):
        if insert_module_docstring(path):
            count += 1
    print(count)


if __name__ == "__main__":
    main()
