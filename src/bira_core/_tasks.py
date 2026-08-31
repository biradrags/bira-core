from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


class DelayedDeleter:
    def __init__(self) -> None:
        self._pending: set[asyncio.Task[None]] = set()

    def schedule(
        self,
        coro_fn: Callable[[], Awaitable[None]],
        delay: float,
    ) -> None:
        if delay <= 0:
            return
        task = asyncio.create_task(self._run(coro_fn, delay))
        self._pending.add(task)
        task.add_done_callback(self._pending.discard)

    async def shutdown(self) -> None:
        for task in list(self._pending):
            task.cancel()
        if self._pending:
            await asyncio.gather(*self._pending, return_exceptions=True)

    async def _run(
        self,
        coro_fn: Callable[[], Awaitable[None]],
        delay: float,
    ) -> None:
        try:
            await asyncio.sleep(delay)
            await coro_fn()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("delayed task failed", exc_info=True)
