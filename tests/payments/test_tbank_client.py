import subprocess
import sys
from typing import Any

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from bira_core.payments import tbank

TERMINAL_KEY = "TERMINAL-synthetic-1"
PASSWORD = "password-synthetic-1"
TRUNCATED_JSON = (
    '{"TerminalKey":"TERMINAL-synthetic-1","Success":true,'
    '"PaymentURL":"https://pay.example/secret-link","Paym'
)


async def _call_against(
    method: str, bodies: list[str | bytes]
) -> tuple[dict[str, Any], int]:
    """Сервер отвечает bodies по очереди; вернуть ответ метода клиента и число вызовов."""
    calls = 0

    async def handler(request: web.Request) -> web.Response:
        nonlocal calls
        body = bodies[min(calls, len(bodies) - 1)]
        calls += 1
        if isinstance(body, bytes):
            return web.Response(
                body=body, content_type="application/json", charset="utf-8"
            )
        return web.Response(text=body, content_type="application/json")

    app = web.Application()
    app.router.add_post("/Init", handler)
    app.router.add_post("/Cancel", handler)
    async with TestServer(app) as server, aiohttp.ClientSession() as session:
        client = tbank.TBankClient(
            terminal_key=TERMINAL_KEY,
            password=PASSWORD,
            api_base_url=str(server.make_url("")),
            session=session,
        )
        result = await getattr(client, method)({"Amount": 100, "OrderId": "1"})
    return result, calls


async def test_non_json_body_is_network_error_with_body_preview() -> None:
    with pytest.raises(tbank.TBankNetworkError) as info:
        await _call_against("init", ["<html>502 Bad Gateway</html>"])

    assert "502 Bad Gateway" in str(info.value)


@pytest.mark.parametrize("prefix", ["", "﻿", " \n﻿"])
async def test_truncated_json_body_does_not_leak_into_message(prefix: str) -> None:
    with pytest.raises(tbank.TBankNetworkError) as info:
        await _call_against("init", [prefix + TRUNCATED_JSON])

    message = str(info.value)
    assert "secret-link" not in message
    assert TERMINAL_KEY not in message


async def test_undecodable_body_message_says_so() -> None:
    with pytest.raises(tbank.TBankNetworkError) as info:
        await _call_against("init", [b'\xff\xfe{"a"'])

    message = str(info.value)
    assert "undecodable" in message
    assert "0 chars" not in message


async def test_invalid_body_is_retried_once_then_succeeds() -> None:
    result, calls = await _call_against(
        "init", ["<html>502</html>", '{"Success":true}']
    )

    assert result == {"Success": True}
    assert calls == 2


async def test_cancel_with_invalid_body_is_network_error_after_one_retry() -> None:
    with pytest.raises(tbank.TBankNetworkError):
        await _call_against("cancel", ["<html>502</html>"])


def test_module_imports_without_deprecation_warning() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-W",
            "error::DeprecationWarning",
            "-c",
            "import bira_core.payments.tbank",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
