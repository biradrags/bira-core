"""Telegram platform filters."""

import logging
from collections.abc import Collection

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bira_core.auth import is_superadmin as _is_superadmin

logger = logging.getLogger(__name__)

__all__ = ["IsServiceChat", "IsSuperAdmin", "is_superadmin"]


def is_superadmin(user_id: int, superusers: Collection[int]) -> bool:
    """Check Superadmin."""
    return _is_superadmin(user_id, superusers)


class IsSuperAdmin(BaseFilter):
    """Is Super Admin."""

    def __init__(self, *, superusers: Collection[int]) -> None:
        """Initialize instance."""
        self._superusers = superusers

    async def __call__(self, message: Message) -> bool:
        """Call."""
        if message.from_user is None:
            return False
        result = _is_superadmin(message.from_user.id, self._superusers)
        logger.debug("IsSuperAdmin", extra={"result": result})
        return result


class IsServiceChat(BaseFilter):
    """Is Service Chat."""

    def __init__(self, service_chat_id: int) -> None:
        """Initialize instance."""
        self._service_chat_id = service_chat_id

    async def __call__(self, message: Message) -> bool:
        """Call."""
        result = int(message.chat.id) == int(self._service_chat_id)
        logger.debug(
            "IsServiceChat", extra={"chat_id": message.chat.id, "result": result}
        )
        return result
