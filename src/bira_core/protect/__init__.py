"""L1 in-memory per-machine flood guard; L2 Redis rate limiter (fail_open = N×лимит без окна)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiohttp import web
from aiohttp.typedefs import Middleware

from bira_core.protect.flood_guard import FloodGuard
from bira_core.protect.heuristics import StartDeduper

if TYPE_CHECKING:
    from bira_core.protect.heuristics import IsLikelyBot
    from bira_core.protect.rate_limit import RateLimiter

__all__ = [
    "FloodGuard",
    "IsLikelyBot",
    "RateLimiter",
    "StartDeduper",
    "flood_guard_middleware",
]

_LAZY_EXPORTS: dict[str, str] = {
    "IsLikelyBot": "bira_core.protect.heuristics",
    "RateLimiter": "bira_core.protect.rate_limit",
}


def __getattr__(name: str) -> Any:
    module_path = _LAZY_EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    module = import_module(module_path)
    return getattr(module, name)


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
