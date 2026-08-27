import asyncio
import logging
from typing import Any, Protocol, runtime_checkable

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import Message

logger = logging.getLogger(__name__)


@runtime_checkable
class MessageSender(Protocol):
    async def send_message(self, chat_id: int, text: str) -> Any: ...


async def safe_send(
    bot: Bot,
    chat_id: int,
    text: str,
    **kwargs: Any,
) -> Message | None:
    try:
        return await bot.send_message(chat_id, text, **kwargs)
    except TelegramRetryAfter as e:
        logger.warning(
            "rate limited on send",
            extra={"chat_id": chat_id, "retry_after": e.retry_after},
        )
        await asyncio.sleep(e.retry_after)
        try:
            return await bot.send_message(chat_id, text, **kwargs)
        except (TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter):
            logger.error(
                "failed to send message after retry", extra={"chat_id": chat_id}
            )
            return None
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.warning(
            "forbidden or bad request sending message",
            extra={"chat_id": chat_id, "err": str(e)},
        )
        return None
    except TelegramNetworkError as e:
        logger.warning(
            "network error sending message",
            extra={"chat_id": chat_id, "err": str(e)},
        )
        return None
