from __future__ import annotations

import time
from collections.abc import Callable

from aiogram import types
from aiogram.filters import Filter


class StartDeduper:
    def __init__(
        self,
        window_s: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._window = window_s
        self._clock = clock
        self._last: dict[int, float] = {}

    def is_duplicate(self, user_id: int) -> bool:
        now = self._clock()
        last = self._last.get(user_id)
        if last is not None and now - last < self._window:
            return True
        self._last[user_id] = now
        return False


class IsLikelyBot(Filter):
    def __init__(
        self,
        *,
        threshold: int = 3,
        score_no_username: int = 1,
        score_premium: int = -2,
        score_new_id: int = 1,
        score_non_ru: int = 1,
        new_id_threshold: int = 5_000_000_000,
    ) -> None:
        self._threshold = threshold
        self._score_no_username = score_no_username
        self._score_premium = score_premium
        self._score_new_id = score_new_id
        self._score_non_ru = score_non_ru
        self._new_id_threshold = new_id_threshold

    async def __call__(self, message: types.Message) -> bool:
        user = message.from_user
        if not user or user.is_bot:
            return False
        score = 0
        if not user.username:
            score += self._score_no_username
        if user.is_premium:
            score += self._score_premium
        if user.id > self._new_id_threshold:
            score += self._score_new_id
        if user.language_code and user.language_code.lower() != "ru":
            score += self._score_non_ru
        return score < self._threshold
