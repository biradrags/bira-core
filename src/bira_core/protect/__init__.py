"""L1 in-memory per-machine flood guard; L2 Redis rate limiter (fail_open = N×лимит без окна)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from aiohttp import web
from aiohttp.typedefs import Middleware

from bira_core.protect.flood_guard import FloodGuard
from bira_core.protect.heuristics import IsLikelyBot, StartDeduper
from bira_core.protect.rate_limit import RateLimiter

__all__ = [
    "FloodGuard",
    "IsLikelyBot",
    "RateLimiter",
    "StartDeduper",
    "flood_guard_middleware",
]


def flood_guard_middleware(
    guard: FloodGuard,
    rate_key: Callable[[web.Request], str],
) -> Middleware:
    """Flood guard middleware."""

    @web.middleware
    async def middleware(
        request: web.Request, handler: Callable[..., Awaitable[web.StreamResponse]]
    ) -> web.StreamResponse:
        key = rate_key(request)
        if not guard.allow(key):
            return web.json_response({"error": "rate limited"}, status=429)
        return await handler(request)

    return middleware
