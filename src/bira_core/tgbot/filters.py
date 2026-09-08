"""Telegram platform filters."""

import logging
from collections.abc import Collection

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bira_core.auth import is_superadmin as _is_superadmin

logger = logging.getLogger(__name__)

__all__ = ["IsLikelyBot", "IsSuperAdmin", "is_superadmin"]


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


class IsLikelyBot(BaseFilter):
    """True when the sender scores at or above threshold on bot-likeness.

    Признаки слабые: человек без username, с новым id и не-ru локалью
    наберёт тот же score. Годится как вход в мягкий режим (капча, лимит),
    не как единственный гейт на блокировку. Чтобы пропускать только
    похожих на людей - инвертировать фильтр: ``~IsLikelyBot()``.
    """

    def __init__(
        self,
        *,
        threshold: int = 3,
        score_no_username: int = 1,
        score_premium: int = -2,
        score_new_id: int = 1,
        score_non_ru: int = 1,
        new_id_threshold: int = 8_000_000_000,
    ) -> None:
        """Remember scoring weights and the cutoff for a fresh user id."""
        self._threshold = threshold
        self._score_no_username = score_no_username
        self._score_premium = score_premium
        self._score_new_id = score_new_id
        self._score_non_ru = score_non_ru
        self._new_id_threshold = new_id_threshold

    async def __call__(self, message: Message) -> bool:
        """True when score reaches threshold; unknown sender is not a bot."""
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
        return score >= self._threshold
