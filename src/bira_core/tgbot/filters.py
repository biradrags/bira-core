"""Telegram platform filters."""

import logging
from collections.abc import Collection

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bira_core.auth import is_superadmin as _is_superadmin

logger = logging.getLogger(__name__)

__all__ = ["IsSuperAdmin", "is_superadmin"]


def is_superadmin(user_id: int, superusers: Collection[int]) -> bool:
    """Re-export auth.is_superadmin for TG filter call sites."""
    return _is_superadmin(user_id, superusers)


class IsSuperAdmin(BaseFilter):
    """Pass updates from users listed in superusers."""

    def __init__(self, *, superusers: Collection[int]) -> None:
        """Remember fleet superuser ids to check on each message."""
        self._superusers = superusers

    async def __call__(self, message: Message) -> bool:
        """True when message.from_user is in superusers."""
        if message.from_user is None:
            return False
        result = _is_superadmin(message.from_user.id, self._superusers)
        logger.debug("IsSuperAdmin", extra={"result": result})
        return result
