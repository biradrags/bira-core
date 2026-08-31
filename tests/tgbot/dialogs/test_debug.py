from aiogram import Router
from aiogram.fsm.state import State, StatesGroup

from bira_core.tgbot.dialogs.debug import print_router_tree


class _L1(StatesGroup):
    s1 = State()


class _L2(StatesGroup):
    s2 = State()


def test_print_router_tree_nested_three_levels() -> None:
    root = Router(name="root")
    mid = Router(name="mid")
    leaf = Router(name="leaf")
    root.include_router(mid)
    mid.include_router(leaf)
    tree = print_router_tree(root)
    assert "root" in tree
    assert "mid" in tree
    assert "leaf" in tree
    assert tree.index("root") < tree.index("mid") < tree.index("leaf")
