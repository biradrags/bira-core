"""MAX long-polling bootstrap."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from contextlib import suppress
from typing import TYPE_CHECKING, Any, Protocol

from aiohttp import web
from maxo import Bot, Dispatcher
from maxo.transport.long_polling import LongPolling

if TYPE_CHECKING:
    from dishka import AsyncContainer

from bira_core.maxbot.web import drop_webhook_subscriptions

logger = logging.getLogger(__name__)


class SecondaryBotFactory(Protocol):
    """Build secondary Max dispatchers for multi-bot polling."""

    def create_dispatcher(self) -> Dispatcher:
        """Return a fresh Dispatcher wired for one secondary bot."""
        ...


async def run_long_polling(
    bot: Bot,
    dp: Dispatcher,
    *,
    prepare: Callable[[Bot], Any] | None = None,
) -> None:
    """Drop webhooks then block in LongPolling; prepare runs after drop."""
    await drop_webhook_subscriptions(bot)
    if prepare is not None:
        await prepare(bot)
    lp = LongPolling(dp)
    await lp.start(bot)


class MaxPollingManager:
    """Manage main and secondary MAX bots in background polling tasks."""

    def __init__(
        self,
        container: AsyncContainer,
        *,
        secondary_factory: SecondaryBotFactory,
    ) -> None:
        """Hold Dishka container and factory for extra bot dispatchers."""
        self._container = container
        self._secondary_factory = secondary_factory
        self._tasks: dict[int, asyncio.Task[None]] = {}

    async def start_main(self) -> None:
        """Start polling for the primary bot from the container."""
        bot = await self._container.get(Bot)
        dp = await self._container.get(Dispatcher)
        await drop_webhook_subscriptions(bot)
        task = asyncio.create_task(LongPolling(dp).start(bot))
        self._tasks[0] = task
        logger.info("Max main bot polling started")

    async def register_bot(self, bot_id: int, token: str) -> None:
        """Spawn polling for an additional token if not already running."""
        if bot_id in self._tasks:
            return
        dp = self._secondary_factory.create_dispatcher()
        bot = Bot(token=token, warming_up=False)
        await drop_webhook_subscriptions(bot)
        task = asyncio.create_task(LongPolling(dp).start(bot))
        self._tasks[bot_id] = task
        logger.info("max secondary bot polling started", extra={"bot_id": bot_id})

    async def unregister_bot(self, bot_id: int) -> None:
        """Cancel polling task for bot_id when present."""
        task = self._tasks.pop(bot_id, None)
        if task:
            await self._cancel_task(bot_id=bot_id, task=task)
            logger.info("max secondary bot polling stopped", extra={"bot_id": bot_id})

    async def stop_all(self) -> None:
        """Cancel every active main/secondary polling task."""
        for bot_id in list(self._tasks):
            task = self._tasks.pop(bot_id)
            await self._cancel_task(bot_id=bot_id, task=task)
        logger.info("All max polling stopped")

    async def _cancel_task(self, *, bot_id: int, task: asyncio.Task[None]) -> None:
        task.cancel()
        with suppress(asyncio.CancelledError):
            try:
                await task
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    "max polling task stopped",
                    extra={"bot_id": bot_id, "err": f"{type(e).__name__}: {e}"},
                )


async def stop_max_polling(app: web.Application) -> None:
    """aiohttp cleanup hook that stops MaxPollingManager if attached."""
    polling_mgr = app.get("max_polling_manager")
    if polling_mgr is not None:
        await polling_mgr.stop_all()
