"""Ops alert channel to Telegram."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from bira_core.log.redaction import redact_log_message
from bira_core.notify.send import MessageSender

logger = logging.getLogger(__name__)


class Alerts:
    """Alerts."""

    def __init__(
        self,
        sender: MessageSender,
        owner_chat_id: int,
        *,
        window_s: float = 900.0,
        urgent_mention: str = "",
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialize instance."""
        self._sender = sender
        self._owner_chat_id = owner_chat_id
        self._window_s = window_s
        self._urgent_mention = urgent_mention
        self._now = now
        self._last: dict[str, float] = {}

    async def alert(
        self,
        kind: str,
        text: str,
        *,
        urgent: bool = False,
    ) -> None:
        """Alert."""
        now = self._now()
        last = self._last.get(kind)
        if last is not None and now - last < self._window_s:
            logger.info("alert suppressed %s", kind)
            return
        self._last[kind] = now
        log = logger.error if urgent else logger.info
        log("alert %s", kind, extra={"text": text[:500]})
        try:
            body = redact_log_message(f"[{kind}] {text}"[:4000])
            if urgent and self._urgent_mention:
                body = f"{body} {self._urgent_mention}"
            await self._sender.send_message(self._owner_chat_id, body)
        except Exception as e:  # noqa: BLE001 # broad-except-ok: alert best effort
            logger.error(
                "alert undelivered %s",
                kind,
                extra={"err": f"{type(e).__name__}: {e}"},
            )
