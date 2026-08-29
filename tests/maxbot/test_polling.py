import pytest

pytest.importorskip("maxo")

from unittest.mock import AsyncMock, patch

from bira_core.maxbot.polling import run_long_polling


@pytest.mark.asyncio
async def test_run_long_polling_always_drops_webhook() -> None:
    bot = AsyncMock()
    dp = AsyncMock()

    with (
        patch(
            "bira_core.maxbot.polling.drop_webhook_subscriptions", AsyncMock()
        ) as drop,
        patch("bira_core.maxbot.polling.LongPolling") as lp_cls,
    ):
        lp = AsyncMock()
        lp_cls.return_value = lp
        lp.start = AsyncMock()

        await run_long_polling(bot, dp)

    drop.assert_awaited_once_with(bot)
    lp.start.assert_awaited_once_with(bot)


@pytest.mark.asyncio
async def test_run_long_polling_prepare_runs_after_drop() -> None:
    bot = AsyncMock()
    dp = AsyncMock()
    prepare = AsyncMock()
    order: list[str] = []

    async def drop_side_effect(_bot: object) -> None:
        order.append("drop")

    async def prepare_side_effect(_bot: object) -> None:
        order.append("prepare")

    with (
        patch(
            "bira_core.maxbot.polling.drop_webhook_subscriptions",
            AsyncMock(side_effect=drop_side_effect),
        ),
        patch("bira_core.maxbot.polling.LongPolling") as lp_cls,
    ):
        lp = AsyncMock()
        lp_cls.return_value = lp
        lp.start = AsyncMock()
        prepare.side_effect = prepare_side_effect

        await run_long_polling(bot, dp, prepare=prepare)

    assert order == ["drop", "prepare"]
    prepare.assert_awaited_once_with(bot)
