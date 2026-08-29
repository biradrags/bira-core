"""Safe single-message send helper."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol, runtime_checkable

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import LinkPreviewOptions, Message

from bira_core.notify.classifier import classify_aiogram
from bira_core.notify.delivery import DeliveryResult

logger = logging.getLogger(__name__)

_MAX_FLOOD_WAIT_SLEEP = 30


@runtime_checkable
class MessageSender(Protocol):
    """Anything that can send_message(chat_id, text) for Alerts wiring."""

    async def send_message(
        self, chat_id: int, text: str, **kwargs: Any
    ) -> Message | None:
        """Deliver text to chat_id; return Message or None."""
        ...


async def safe_send(
    bot: Bot,
    chat_id: int,
    text: str | None = None,
    *,
    photo: str | None = None,
    business_connection_id: str | None = None,
    message_thread_id: int | None = None,
    **kwargs: Any,
) -> Message | None:
    """Send and return Message; None only after classified failure."""
    result = await deliver(
        bot,
        chat_id,
        text=text,
        photo=photo,
        business_connection_id=business_connection_id,
        message_thread_id=message_thread_id,
        **kwargs,
    )
    return result.sent


async def deliver(
    bot: Bot,
    chat_id: int,
    text: str | None = None,
    *,
    photo: str | None = None,
    business_connection_id: str | None = None,
    message_thread_id: int | None = None,
    **kwargs: Any,
) -> DeliveryResult:
    """Classify errors and retry once on TelegramRetryAfter."""

    async def _attempt() -> Message:
        if photo:
            return await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=text,
                business_connection_id=business_connection_id,
                message_thread_id=message_thread_id,
                **kwargs,
            )
        return await bot.send_message(
            chat_id=chat_id,
            text=text or "",
            business_connection_id=business_connection_id,
            message_thread_id=message_thread_id,
            link_preview_options=LinkPreviewOptions(is_disabled=True),
            parse_mode=kwargs.pop("parse_mode", ParseMode.HTML),
            **kwargs,
        )

    try:
        return DeliveryResult(sent=await _attempt())
    except TelegramRetryAfter as e:
        logger.warning(
            "rate limited on send",
            extra={"chat_id": chat_id, "retry_after": e.retry_after},
        )
        await asyncio.sleep(min(e.retry_after, _MAX_FLOOD_WAIT_SLEEP))
        try:
            return DeliveryResult(sent=await _attempt())
        except Exception as exc:  # noqa: BLE001
            return DeliveryResult(failure=classify_aiogram(exc))
    except Exception as exc:  # noqa: BLE001
        return DeliveryResult(failure=classify_aiogram(exc))
