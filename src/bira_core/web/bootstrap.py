from __future__ import annotations

import logging
from collections.abc import Sequence
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiohttp.web_routedef import RouteDef
from dishka import AsyncContainer
from dishka.integrations.aiohttp import setup_dishka

from bira_core.web.cron import CRON_PORT, cron_protocol, fly_src_gate

logger = logging.getLogger(__name__)


async def _health(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def create_app(
    dp: Dispatcher,
    bot: Bot,
    *,
    webhook_path: str,
    webhook_secret: str,
    container: AsyncContainer | None = None,
    extra_routes: Sequence[RouteDef] = (),
) -> web.Application:
    app = web.Application()
    app.router.add_get("/health", _health)
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


async def run_webhook(
    dp: Dispatcher,
    bot: Bot,
    *,
    port: int,
    webhook_url: str,
    webhook_secret: str,
    container: AsyncContainer | None = None,
    extra_routes: Sequence[RouteDef] = (),
) -> None:
    path = urlparse(webhook_url).path if webhook_url.startswith("http") else webhook_url
    app = create_app(
        dp,
        bot,
        webhook_path=path,
        webhook_secret=webhook_secret,
        container=container,
        extra_routes=extra_routes,
    )

    async def on_startup(_: web.Application) -> None:
        await bot.set_webhook(
            webhook_url, secret_token=webhook_secret, drop_pending_updates=False
        )
        logger.info("Webhook установлен")

    app.on_startup.append(on_startup)
    web.run_app(app, host="0.0.0.0", port=port)


async def run_polling(dp: Dispatcher, bot: Bot) -> None:
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        await dp.start_polling(bot)
    finally:
        logger.info("Бот остановлен")


def create_cron_app(
    routes: Sequence[RouteDef],
    *,
    allowed: frozenset[str] = frozenset({"bira-cron"}),
    container: AsyncContainer | None = None,
) -> web.Application:
    app = web.Application(middlewares=[fly_src_gate(allowed), cron_protocol()])
    app.router.add_routes(routes)
    if container is not None:
        setup_dishka(container, app, auto_inject=True, finalize_container=False)
    return app


def attach_cron_site(
    app: web.Application,
    cron_app: web.Application,
    port: int = CRON_PORT,
) -> None:
    """Второй раннер на 8081 в том же процессе; жизненный цикл - от основного app."""

    async def _start(_: web.Application) -> None:
        runner = web.AppRunner(cron_app)
        await runner.setup()
        app["_cron_runner"] = (
            runner  # до .start(): иначе упавший бинд оставит раннер без cleanup
        )
        await web.TCPSite(runner, "0.0.0.0", port).start()

    async def _stop(_: web.Application) -> None:
        await app["_cron_runner"].cleanup()

    app.on_startup.append(_start)
    app.on_cleanup.append(_stop)
