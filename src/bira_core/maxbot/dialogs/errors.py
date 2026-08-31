"""MAX stale-intent error handler; mirror of bira_core.tgbot.dialogs.errors."""

from __future__ import annotations

import contextlib
import logging
from collections.abc import Awaitable, Callable
from typing import Any, cast

from maxo import Ctx, Dispatcher
from maxo.dialogs.api.exceptions import OutdatedIntent, UnknownIntent, UnknownState
from maxo.routing.filters import ExceptionTypeFilter
from maxo.types import ErrorEvent, MessageCallback

logger = logging.getLogger(__name__)

STALE_INTENT_EXCEPTIONS = (UnknownIntent, UnknownState, OutdatedIntent)

__all__ = ["STALE_INTENT_EXCEPTIONS", "clear_stale_intent", "register_stale_intent"]


async def clear_stale_intent(event: ErrorEvent[Any, Any], ctx: Ctx) -> None:
    """Delete the orphaned menu whose dialog context is gone.

    В MAX нет аналога callback.answer с тостом, поэтому реакция одна - убрать
    мёртвое меню, чтобы юзер не ходил по кругу «тап - ничего не происходит».
    """
    logger.info("stale intent", extra={"err": type(event.exception).__name__})
    inner = event.update.update
    if not isinstance(inner, MessageCallback) or inner.message is None:
        return
    bot = await _resolve_bot(ctx)
    if bot is None:
        logger.warning("stale intent: no bot in context, menu left in place")
        return
    with contextlib.suppress(Exception):
        await bot.delete_message(message_id=inner.message.body.mid)


def register_stale_intent(
    dp: Dispatcher,
    *,
    handler: Callable[..., Awaitable[None]] | None = None,
) -> None:
    """Register the stale-intent handler on the dispatcher error router."""
    dp.error.handler(
        cast(Any, handler or clear_stale_intent),
        ExceptionTypeFilter(*STALE_INTENT_EXCEPTIONS),
    )


async def _resolve_bot(ctx: Ctx) -> Any | None:
    bot = ctx.get("bot")
    if bot is not None:
        return bot
    try:
        from maxo import Bot
        from maxo.integrations.dishka import CONTAINER_NAME
    except ImportError:
        return None
    container = ctx.get(CONTAINER_NAME)
    if container is None:
        return None
    return await container.get(Bot)
