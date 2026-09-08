"""aiohttp middleware for FloodGuard."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from aiohttp import web
from aiohttp.typedefs import Middleware

from bira_core.protect.flood_guard import FloodGuard

__all__ = ["flood_guard_middleware"]


def flood_guard_middleware(
    guard: FloodGuard,
    rate_key: Callable[[web.Request], str],
) -> Middleware:
    """aiohttp middleware returning 429 when FloodGuard denies the key."""

    @web.middleware
    async def middleware(
        request: web.Request, handler: Callable[..., Awaitable[web.StreamResponse]]
    ) -> web.StreamResponse:
        key = rate_key(request)
        if not guard.allow(key):
            return web.json_response({"error": "rate limited"}, status=429)
        return await handler(request)

    return middleware
