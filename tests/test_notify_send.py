from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter

from bira_core.notify.send import safe_send


class _FakeBot:
    def __init__(self, fails: list[Exception]):
        self._fails = fails
        self.calls: list[tuple[int, str]] = []

    async def send_message(self, chat_id: int, text: str, **kw):
        self.calls.append((chat_id, text))
        if self._fails:
            raise self._fails.pop(0)
        return "MSG"


def _retry_after(seconds: int = 0) -> TelegramRetryAfter:
    return TelegramRetryAfter(method=None, message="flood", retry_after=seconds)


async def test_retries_on_retry_after() -> None:
    bot = _FakeBot([_retry_after()])
    assert await safe_send(bot, 1, "hi") == "MSG"  # type: ignore[arg-type]
    assert len(bot.calls) == 2


async def test_network_error_returns_none() -> None:
    bot = _FakeBot([TelegramNetworkError(method=None, message="down")] * 5)
    assert await safe_send(bot, 1, "hi") is None  # type: ignore[arg-type]
