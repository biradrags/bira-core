from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from bira_core.notify.classifier import classify_aiogram
from bira_core.notify.delivery import FailureCategory


def test_classify_retry_after() -> None:
    exc = TelegramRetryAfter(method=MagicMock(), message="flood", retry_after=12)
    failure = classify_aiogram(exc)
    assert failure.category == FailureCategory.FLOOD_WAIT
    assert failure.retry_after == 12


def test_classify_blocked() -> None:
    exc = TelegramForbiddenError(method=MagicMock(), message="blocked")
    failure = classify_aiogram(exc)
    assert failure.category == FailureCategory.BLOCKED


@pytest.mark.asyncio
async def test_deliver_caps_flood_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []

    async def fake_sleep(sec: float) -> None:
        sleeps.append(sec)

    monkeypatch.setattr("asyncio.sleep", fake_sleep)
    bot = AsyncMock()
    bot.send_message.side_effect = TelegramRetryAfter(
        method=MagicMock(), message="f", retry_after=999
    )
    from bira_core.notify.send import deliver

    result = await deliver(bot, 1, text="hi")
    assert result.failure is not None
    assert sleeps and sleeps[0] <= 30
