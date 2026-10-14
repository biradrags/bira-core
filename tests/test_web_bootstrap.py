from unittest.mock import AsyncMock

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram_dialog import setup_dialogs
from aiohttp.test_utils import TestClient, TestServer

from bira_core.tgbot.web_bootstrap import create_app, used_update_types


def test_used_update_types_skips_dialog_internal() -> None:
    dp = Dispatcher()

    @dp.message()
    async def _(_: Message) -> None: ...

    setup_dialogs(dp)
    types = used_update_types(dp)
    assert "message" in types
    assert "aiogd_update" not in types


async def test_random_secret_set_on_startup_and_checked() -> None:
    dp = Dispatcher()
    bot = Bot(token="42:FAKE_TOKEN_FOR_TESTS_ONLY")
    bot.set_webhook = AsyncMock()  # type: ignore[method-assign]
    app = create_app(dp, bot, base_url="https://bot.example/")
    client = TestClient(TestServer(app))
    await client.start_server()

    call = bot.set_webhook.await_args
    assert call is not None
    assert call.args == ("https://bot.example/webhook",)
    secret = call.kwargs["secret_token"]
    assert len(secret) == 64
    wrong = await client.post(
        "/webhook",
        json={"update_id": 1},
        headers={"X-Telegram-Bot-Api-Secret-Token": "x"},
    )
    assert wrong.status == 401
    ok = await client.post(
        "/webhook",
        json={"update_id": 1},
        headers={"X-Telegram-Bot-Api-Secret-Token": secret},
    )
    assert ok.status == 200
    await client.close()
    await bot.session.close()


async def test_health_and_webhook_route() -> None:
    dp = Dispatcher()
    bot = Bot(token="42:FAKE_TOKEN_FOR_TESTS_ONLY")
    app = create_app(
        dp, bot, webhook_path="/webhook/testsecret", webhook_secret="testsecret"
    )
    client = TestClient(TestServer(app))
    await client.start_server()
    health = await client.get("/health")
    assert health.status == 200
    paths = {r.resource.canonical for r in app.router.routes() if r.resource}
    assert "/webhook/testsecret" in paths
    await client.close()
    await bot.session.close()
