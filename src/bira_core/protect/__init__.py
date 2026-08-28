"""In-memory flood guard for aiohttp ingress. Бюджет per-machine."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from aiohttp import web
from aiohttp.typedefs import Middleware

from bira_core.protect.flood_guard import FloodGuard


def flood_guard_middleware(
    guard: FloodGuard,
    rate_key: Callable[[web.Request], str],
) -> Middleware:
    @web.middleware
    async def middleware(
        request: web.Request, handler: Callable[..., Awaitable[web.StreamResponse]]
    ) -> web.StreamResponse:
        key = rate_key(request)
        if not guard.allow(key):
            return web.json_response({"error": "rate limited"}, status=429)
        return await handler(request)

    return middleware
