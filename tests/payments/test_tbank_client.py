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
# Невидимые символы собраны через chr(): литерал в исходнике теряется при правке.
JSON_PREFIXES = [
    "",
    chr(0xFEFF),
    " \n" + chr(0xFEFF),
    chr(0xA0),
    chr(0x0B),
    chr(0x2028),
    chr(0),
    ")]}'\n",
]


async def _call_against(
    method: str, bodies: list[str | bytes]
) -> tuple[dict[str, Any] | tbank.TBankNetworkError, int]:
    """Сервер отвечает bodies по очереди; вернуть итог вызова клиента и число запросов."""
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
    outcome: dict[str, Any] | tbank.TBankNetworkError
    async with TestServer(app) as server, aiohttp.ClientSession() as session:
        client = tbank.TBankClient(
            terminal_key=TERMINAL_KEY,
            password=PASSWORD,
            api_base_url=str(server.make_url("")),
            session=session,
        )
        try:
            outcome = await getattr(client, method)({"Amount": 100, "OrderId": "1"})
        except tbank.TBankNetworkError as exc:
            outcome = exc
    return outcome, calls


async def test_html_body_is_network_error_with_body_preview() -> None:
    outcome, calls = await _call_against("init", ["<html>502 Bad Gateway</html>"])

    assert isinstance(outcome, tbank.TBankNetworkError)
    assert "502 Bad Gateway" in str(outcome)
    assert calls == 2


@pytest.mark.parametrize("prefix", JSON_PREFIXES)
async def test_truncated_json_body_does_not_leak_into_message(prefix: str) -> None:
    outcome, _ = await _call_against("init", [prefix + TRUNCATED_JSON])

    assert isinstance(outcome, tbank.TBankNetworkError)
    message = str(outcome)
    assert "secret-link" not in message
    assert TERMINAL_KEY not in message


async def test_undecodable_body_message_says_so() -> None:
    outcome, calls = await _call_against("init", [b'\xff\xfe{"a"'])

    assert isinstance(outcome, tbank.TBankNetworkError)
    assert "undecodable" in str(outcome)
    assert "0 chars" not in str(outcome)
    assert calls == 2


async def test_invalid_body_is_retried_once_then_succeeds() -> None:
    outcome, calls = await _call_against(
        "init", ["<html>502</html>", '{"Success":true}']
    )

    assert outcome == {"Success": True}
    assert calls == 2


async def test_cancel_with_invalid_body_is_network_error_after_one_retry() -> None:
    outcome, calls = await _call_against("cancel", ["<html>502</html>"])

    assert isinstance(outcome, tbank.TBankNetworkError)
    assert calls == 2


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
