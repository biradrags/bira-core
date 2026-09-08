from aiogram import Bot, Dispatcher
from aiohttp.test_utils import TestClient, TestServer

from bira_core.tgbot.web_bootstrap import create_app


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
