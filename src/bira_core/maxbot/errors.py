"""MAX stale-intent error handlers."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger(__name__)


async def clear_stale_intent(*_args: Any, **_kwargs: Any) -> None:
    """Сброс устаревшего intent в MAX-диалогах; зеркало tgbot.dialogs.errors."""


def register_stale_intent(
    _router: Any,
    *,
    handler: Callable[..., Awaitable[None]] | None = None,
) -> None:
    """Регистрация stale-intent на отдельном router до include; зеркало tgbot."""
