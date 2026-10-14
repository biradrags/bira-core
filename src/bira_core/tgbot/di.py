"""Dishka для aiogram: одна REQUEST-область на апдейт."""

from collections.abc import Awaitable, Callable
from functools import partial
from typing import Any

from aiogram import Router
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import (
    CONTAINER_NAME,
    ContainerMiddleware,
    inject_router,
)


class _UpdateScopeMiddleware(ContainerMiddleware):
    """Штатный middleware открывает область на каждом observer - на `update` и снова
    на `message`: DAO middleware апдейта и `FromDishka` хендлера расходятся."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if CONTAINER_NAME in data:
            return await handler(event, data)
        return await super().__call__(handler, event, data)


def setup_dishka(
    container: AsyncContainer, router: Router, *, auto_inject: bool = True
) -> None:
    """Замена `dishka.integrations.aiogram.setup_dishka` с общей областью апдейта."""
    middleware = _UpdateScopeMiddleware(container)
    for observer in router.observers.values():
        observer.outer_middleware(middleware)
    if auto_inject:
        router.startup.register(partial(inject_router, router=router))
