import logging
from collections.abc import Collection

from aiogram.filters import BaseFilter
from aiogram.types import Message

logger = logging.getLogger(__name__)

__all__ = ["IsServiceChat", "IsSuperAdmin", "is_superadmin"]


def is_superadmin(user_id: int, superusers: Collection[int]) -> bool:
    return user_id in superusers


class IsSuperAdmin(BaseFilter):
    def __init__(self, *, superusers: Collection[int]) -> None:
        self._superusers = superusers

    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False
        result = is_superadmin(message.from_user.id, self._superusers)
        logger.debug("IsSuperAdmin", extra={"result": result})
        return result


class IsServiceChat(BaseFilter):
    def __init__(self, service_chat_id: int) -> None:
        self._service_chat_id = service_chat_id

    async def __call__(self, message: Message) -> bool:
        result = int(message.chat.id) == int(self._service_chat_id)
        logger.debug(
            "IsServiceChat", extra={"chat_id": message.chat.id, "result": result}
        )
        return result
