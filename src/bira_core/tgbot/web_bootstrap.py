"""Telegram webhook/polling bootstrap."""

from __future__ import annotations

import secrets
from collections.abc import Sequence
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiohttp.web_routedef import RouteDef

from bira_core.web.bootstrap import health_handler

if TYPE_CHECKING:
    from dishka import AsyncContainer

# Служебный апдейт aiogram_dialog: Telegram такого типа не знает
_INTERNAL_UPDATES = frozenset({"aiogd_update"})


def used_update_types(dp: Dispatcher) -> list[str]:
    """allowed_updates для set_webhook и start_polling - из хендлеров диспетчера."""
    return dp.resolve_used_update_types(skip_events=set(_INTERNAL_UPDATES))


def create_app(
    dp: Dispatcher,
    bot: Bot,
    *,
    base_url: str | None = None,
    webhook_path: str = "/webhook",
    webhook_secret: str | None = None,
    container: AsyncContainer | None = None,
    extra_routes: Sequence[RouteDef] = (),
    handle_in_background: bool = True,
) -> web.Application:
    """aiohttp app с /health, webhook и опциональным Dishka.

    С ``base_url`` вебхук ставится на старте. Без ``webhook_secret`` секрет случайный
    на процесс: Telegram получает его в set_webhook, хендлер сверяет тот же.
    """
    secret = webhook_secret or secrets.token_hex(32)
    app = web.Application()
    app.router.add_get("/health", health_handler)
    for route in extra_routes:
        app.router.add_route(route.method, route.path, route.handler)

    if container is not None:
        from dishka.integrations.aiogram import setup_dishka

        setup_dishka(container=container, router=dp, auto_inject=True)

        async def on_shutdown(_: web.Application) -> None:
            await container.close()

        app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=secret,
        handle_in_background=handle_in_background,
    ).register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)

    # После setup_application: вебхук ставится, когда startup-хендлеры диспетчера отработали
    if base_url is not None:
        url = base_url.rstrip("/") + webhook_path

        async def set_webhook(_: web.Application) -> None:
            await bot.set_webhook(
                url,
                secret_token=secret,
                allowed_updates=used_update_types(dp),
                drop_pending_updates=False,
            )

        app.on_startup.append(set_webhook)
    return app
