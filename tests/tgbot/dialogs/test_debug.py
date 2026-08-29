from aiogram import Router

from bira_core.tgbot.dialogs.debug import print_router_tree


def test_print_router_tree() -> None:
    router = Router(name="root")
    child = Router(name="child")
    router.include_router(child)
    tree = print_router_tree(router)
    assert "root" in tree
    assert "child" in tree
