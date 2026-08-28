import pytest

pytest.importorskip("maxo")

from unittest.mock import AsyncMock, patch

from bira_core.maxbot.polling import run_long_polling


@pytest.mark.asyncio
async def test_run_long_polling_prepares_and_starts() -> None:
    bot = AsyncMock()
    dp = AsyncMock()
    prepare = AsyncMock()

    with patch("bira_core.maxbot.polling.LongPolling") as lp_cls:
        lp = AsyncMock()
        lp_cls.return_value = lp
        lp.start = AsyncMock()

        await run_long_polling(bot, dp, prepare=prepare)

    prepare.assert_awaited_once_with(bot)
    lp.start.assert_awaited_once_with(bot)
