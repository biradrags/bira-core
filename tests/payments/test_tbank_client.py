from typing import Any

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from bira_core.payments import tbank

TERMINAL_KEY = "TERMINAL-synthetic-1"
PASSWORD = "password-synthetic-1"


async def _init_against(bodies: list[str]) -> tuple[dict[str, Any], int]:
    """Поднять сервер, отвечающий bodies по очереди; вернуть ответ Init и число вызовов."""
    calls = 0

    async def init(request: web.Request) -> web.Response:
        nonlocal calls
        body = bodies[min(calls, len(bodies) - 1)]
        calls += 1
        return web.Response(text=body, content_type="application/json")

    app = web.Application()
    app.router.add_post("/Init", init)
    async with TestServer(app) as server, aiohttp.ClientSession() as session:
        client = tbank.TBankClient(
            terminal_key=TERMINAL_KEY,
            password=PASSWORD,
            api_base_url=str(server.make_url("")),
            session=session,
        )
        result = await client.init({"Amount": 100, "OrderId": "1"})
    return result, calls


async def test_invalid_json_body_is_network_error_with_body_preview() -> None:
    with pytest.raises(tbank.TBankNetworkError) as info:
        await _init_against(["<html>502 Bad Gateway</html>"])

    message = str(info.value)
    assert "502 Bad Gateway" in message
    assert PASSWORD not in message
    assert TERMINAL_KEY not in message


async def test_truncated_json_body_does_not_leak_into_message() -> None:
    truncated = '{"Success":true,"PaymentURL":"https://pay.example/secret-link","Paym'
    with pytest.raises(tbank.TBankNetworkError) as info:
        await _init_against([truncated])

    message = str(info.value)
    assert "secret-link" not in message
    assert TERMINAL_KEY not in message


async def test_invalid_json_body_is_retried_once_then_succeeds() -> None:
    result, calls = await _init_against(["<html>502</html>", '{"Success":true}'])

    assert result == {"Success": True}
    assert calls == 2
