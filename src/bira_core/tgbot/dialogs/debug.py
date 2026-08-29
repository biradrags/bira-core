"""Router tree debug printer."""

from aiogram import Dispatcher, Router


def print_router_tree(router: Router, indent: int = 0) -> str:
    """Return indented router/sub-router names for debugging nested trees."""
    if isinstance(router, Dispatcher):
        result = " " * indent + "dispatcher"
    else:
        result = " " * indent + (router.name or "router")
    for in_router in router.sub_routers:
        result += "\n" + print_router_tree(in_router, indent + 2)
    return result
