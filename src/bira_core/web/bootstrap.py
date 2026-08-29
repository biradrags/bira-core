from __future__ import annotations

from collections.abc import Sequence

from aiohttp import web
from aiohttp.web_routedef import RouteDef
from dishka import AsyncContainer
from dishka.integrations.aiohttp import setup_dishka

from bira_core.web.cron import CRON_PORT, cron_protocol, fly_src_gate


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


async def _health(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})
