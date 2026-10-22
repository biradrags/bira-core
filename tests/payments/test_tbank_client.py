import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from bira_core.payments import tbank

TERMINAL_KEY = "TERMINAL-synthetic-1"
PASSWORD = "password-synthetic-1"


async def test_invalid_json_body_is_network_error_with_body_preview() -> None:
    calls = 0

    async def init(request: web.Request) -> web.Response:
        nonlocal calls
        calls += 1
        return web.Response(
            text="<html>502 Bad Gateway</html>", content_type="application/json"
        )

    app = web.Application()
    app.router.add_post("/Init", init)
    async with TestServer(app) as server, aiohttp.ClientSession() as session:
        client = tbank.TBankClient(
            terminal_key=TERMINAL_KEY,
            password=PASSWORD,
            api_base_url=str(server.make_url("")),
            session=session,
        )
        with pytest.raises(tbank.TBankNetworkError) as info:
            await client.init({"Amount": 100, "OrderId": "1"})

    message = str(info.value)
    assert "502 Bad Gateway" in message
    assert PASSWORD not in message
    assert TERMINAL_KEY not in message
    assert calls == 2
