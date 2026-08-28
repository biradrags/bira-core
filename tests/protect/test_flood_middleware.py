from unittest.mock import MagicMock

import pytest
from aiohttp import web

from bira_core.protect import flood_guard_middleware
from bira_core.protect.flood_guard import FloodGuard


@pytest.mark.asyncio
async def test_middleware_returns_429() -> None:
    guard = FloodGuard(
        per_key_rate=0.0,
        per_key_burst=0,
        global_rate=0.0,
        global_burst=0,
    )
    middleware = flood_guard_middleware(guard, lambda r: "k")

    async def handler(_: web.Request) -> web.Response:
        return web.Response(text="ok")

    app = web.Application(middlewares=[middleware])
    app.router.add_get("/", handler)
    request = MagicMock()
    request.match_info = {}
    resp = await middleware(request, handler)
    assert resp.status == 429
