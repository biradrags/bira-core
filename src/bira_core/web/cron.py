"""Fly cron middleware and port constant."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

from aiohttp import web
from aiohttp.typedefs import Middleware

logger = logging.getLogger(__name__)

CRON_PORT = 8081  # константа флота: bira-cron шлёт на <app>.flycast:8081

_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]


def fly_src_gate(allowed: frozenset[str]) -> Middleware:
    """Reject cron requests whose fly-src app is not in the allowlist."""

    @web.middleware
    async def middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
        src = _caller_app(request)
        if src not in allowed:
            logger.warning(
                "cron denied",
                extra={"src": src or "unknown", "path": request.path},
            )
            return web.json_response({"error": "forbidden"}, status=403)
        return await handler(request)

    return middleware


_locks: dict[str, asyncio.Lock] = {}


def cron_protocol() -> Middleware:
    """Serialize concurrent runs per job name; always return JSON status."""

    @web.middleware
    async def middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
        name = request.match_info.get("job") or request.path.lstrip("/")
        lock = _locks.setdefault(name, asyncio.Lock())
        if lock.locked():
            logger.info(
                "cron skipped", extra={"job": name, "reason": "already_running"}
            )
            return web.json_response(
                {"job": name, "status": "skipped", "reason": "already_running"}
            )

        async with lock:
            started = time.monotonic()
            try:
                await handler(request)
            except web.HTTPException:
                raise
            except Exception:
                logger.exception("cron job failed", extra={"job": name})
                return web.json_response({"job": name, "status": "error"}, status=500)
            took_ms = int((time.monotonic() - started) * 1000)
            logger.info("cron job done", extra={"job": name, "took_ms": took_ms})
            return web.json_response({"job": name, "status": "ok", "took_ms": took_ms})

    return middleware


def _caller_app(request: web.Request) -> str | None:
    raw = request.headers.get("fly-src")
    if not raw:
        return None
    for part in raw.split(";"):
        key, _, value = part.partition("=")
        if key.strip() == "app":
            return value.strip()
    return None
