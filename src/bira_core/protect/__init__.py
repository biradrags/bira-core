"""L1 in-memory per-machine flood guard; L2 Redis rate limiter (fail_open = N×лимит без окна)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from aiohttp import web
from aiohttp.typedefs import Middleware

from bira_core.protect.flood_guard import FloodGuard
from bira_core.protect.heuristics import StartDeduper

# RateLimiter требует redis - bira_core.protect.rate_limit ([protect]).
# IsLikelyBot - фильтр aiogram, живёт в bira_core.tgbot.filters ([tgbot]).
__all__ = [
    "FloodGuard",
    "StartDeduper",
    "flood_guard_middleware",
]


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
