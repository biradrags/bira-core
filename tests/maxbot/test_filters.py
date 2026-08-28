import pytest

pytest.importorskip("maxo")

from unittest.mock import AsyncMock, MagicMock

from bira_core.maxbot.filters import IsSuperAdmin
from bira_core.maxbot.web import drop_webhook_subscriptions


class _User:
    def __init__(self, tg_id: int) -> None:
        self.tg_id = tg_id


@pytest.mark.asyncio
async def test_drop_webhook_subscriptions_unsubscribes_all() -> None:
    bot = AsyncMock()
    bot.state.started = True
    sub = MagicMock(url="https://example.com/hook")
    bot.get_subscriptions.return_value.subscriptions = [sub]

    await drop_webhook_subscriptions(bot)

    bot.unsubscribe.assert_awaited_once_with(url=sub.url)


@pytest.mark.asyncio
async def test_is_superadmin_filter() -> None:
    filt = IsSuperAdmin({1, 2})
    ctx: dict[str, object] = {"user": _User(2)}
    assert await filt(MagicMock(), ctx) is True
    ctx["user"] = _User(3)
    assert await filt(MagicMock(), ctx) is False
