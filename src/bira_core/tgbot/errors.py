"""Unhandled update error registration."""

import logging

from aiogram import Router
from aiogram.types.error_event import ErrorEvent

from bira_core.notify import Alerts

logger = logging.getLogger(__name__)

__all__ = ["register_error_handlers"]


def register_error_handlers(router: Router, *, alerts: Alerts | None = None) -> None:
    """Register Error handlers."""

    async def handler(error: ErrorEvent) -> None:
        await _handle_error(error, alerts=alerts)

    router.errors.register(handler)


async def _handle_error(error: ErrorEvent, *, alerts: Alerts | None = None) -> None:
    logger.error(
        "unhandled update error",
        extra={
            "err": error.exception.__class__.__name__,
            "update": error.update.model_dump(exclude_none=True),
        },
        exc_info=error.exception,
    )
    if alerts is not None:
        await alerts.alert("bot", error.exception.__class__.__name__)
