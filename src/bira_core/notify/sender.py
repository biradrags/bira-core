"""Platform-neutral sender protocol shared by alerts and bulk delivery."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = ["MessageSender"]


@runtime_checkable
class MessageSender(Protocol):
    """Anything with send_message(chat_id, text): aiogram Bot, maxo Bot, mock."""

    async def send_message(self, chat_id: int, text: str, **kwargs: Any) -> Any:
        """Deliver text to chat_id; return the platform message object or None."""
        ...
