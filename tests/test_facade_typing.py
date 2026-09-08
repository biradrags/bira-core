"""Каждое имя из __all__ фасада должно быть видимо статически.

Фасады отдают часть символов через __getattr__ (ленивый импорт под extras).
Для mypy потребителя такой символ - Any, и весь код вокруг него перестаёт
проверяться, хотя py.typed в пакете есть. Лечится зеркальным импортом под
if TYPE_CHECKING; этот тест следит, чтобы зеркало не отставало.
"""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "bira_core"

FACADES = [
    p
    for p in [SRC / "__init__.py", *sorted(SRC.glob("*/__init__.py"))]
    if "def __getattr__" in p.read_text(encoding="utf-8")
]


def _statically_visible(tree: ast.Module) -> set[str]:
    """Имена, которые mypy увидит в модуле: импорты, классы, функции, присваивания."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            names.update(a.asname or a.name for a in node.names)
        elif isinstance(node, ast.Import):
            names.update((a.asname or a.name).split(".")[0] for a in node.names)
        elif isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    return names


def _declared_all(tree: ast.Module) -> set[str]:
    for node in tree.body:
        targets = (
            node.targets
            if isinstance(node, ast.Assign)
            else [node.target]
            if isinstance(node, ast.AnnAssign)
            else []
        )
        if any(isinstance(t, ast.Name) and t.id == "__all__" for t in targets):
            value = node.value
            if isinstance(value, ast.List):
                return {e.value for e in value.elts if isinstance(e, ast.Constant)}
    return set()


def test_facades_discovered() -> None:
    assert FACADES, (
        "не нашли ни одного фасада с __getattr__ - тест ничего бы не проверял"
    )


@pytest.mark.parametrize("path", FACADES, ids=lambda p: str(p.relative_to(SRC)))
def test_every_export_is_statically_visible(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    missing = sorted(_declared_all(tree) - _statically_visible(tree))
    assert not missing, (
        f"{path.relative_to(SRC)}: {missing} отдаются только через __getattr__ - "
        "для mypy потребителя это Any. Добавить зеркальный импорт под if TYPE_CHECKING."
    )
