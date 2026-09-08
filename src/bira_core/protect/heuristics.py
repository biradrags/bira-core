"""Cheap abuse heuristics: /start dedupe."""

from __future__ import annotations

import time
from collections.abc import Callable

__all__ = ["StartDeduper"]


class StartDeduper:
    """Suppress duplicate /start within a sliding time window."""

    def __init__(
        self,
        window_s: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Remember last /start timestamp per user for window_s seconds."""
        self._window = window_s
        self._clock = clock
        self._last: dict[int, float] = {}

    def is_duplicate(self, user_id: int) -> bool:
        """True when the same user_id started inside the dedupe window."""
        now = self._clock()
        last = self._last.get(user_id)
        if last is not None and now - last < self._window:
            return True
        self._last[user_id] = now
        return False
