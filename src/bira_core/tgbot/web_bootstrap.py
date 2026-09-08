"""Telegram webhook/polling bootstrap."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiohttp.web_routedef import RouteDef

from bira_core.web.bootstrap import health_handler

if TYPE_CHECKING:
    from dishka import AsyncContainer


def create_app(
    dp: Dispatcher,
    bot: Bot,
    *,
    webhook_path: str,
    webhook_secret: str,
    container: AsyncContainer | None = None,
    extra_routes: Sequence[RouteDef] = (),
) -> web.Application:
    """aiohttp app with /health, webhook handler, and optional Dishka."""
    app = web.Application()
    app.router.add_get("/health", health_handler)
    for route in extra_routes:
        app.router.add_route(route.method, route.path, route.handler)

    if container is not None:
        from dishka.integrations.aiogram import setup_dishka as setup_dishka_aiogram

        setup_dishka_aiogram(container=container, router=dp, auto_inject=True)

        async def on_shutdown(_: web.Application) -> None:
            await container.close()

        app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=webhook_secret,
    ).register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)
    return app
