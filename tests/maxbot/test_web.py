import pytest

pytest.importorskip("maxo")

from unittest.mock import AsyncMock

from bira_core.maxbot.web import drop_webhook_subscriptions


@pytest.mark.asyncio
async def test_drop_webhook_starts_bot_when_needed() -> None:
    bot = AsyncMock()
    bot.state.started = False
    bot.get_subscriptions.return_value.subscriptions = []

    await drop_webhook_subscriptions(bot)

    bot.start.assert_awaited_once()
