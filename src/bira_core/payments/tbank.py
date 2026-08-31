"""T-Bank payment client."""

from __future__ import annotations

import hashlib
import hmac
import ssl
from collections.abc import Mapping
from typing import Any, cast

import aiohttp
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from bira_core.tls import russian_trusted_ssl_context


def build_tbank_token(params: Mapping[str, Any], password: str) -> str:
    """HMAC-SHA256 token over sorted T-Bank request fields plus password."""
    items: list[tuple[str, str]] = []
    for key, value in params.items():
        if key in ("Token", "DATA", "Receipt"):
            continue
        if value is None:
            continue
        if isinstance(value, bool):
            str_value = "true" if value else "false"
        else:
            str_value = str(value)
        items.append((key, str_value))
    items.append(("Password", password))
    items.sort(key=lambda kv: kv[0])
    concatenated = "".join(v for _, v in items)
    return hashlib.sha256(concatenated.encode("utf-8")).hexdigest()


def verify_tbank_token(params: Mapping[str, Any], password: str) -> bool:
    """Constant-time compare of request Token with freshly built digest."""
    token = str(params.get("Token") or "")
    expected = build_tbank_token(params, password)
    return hmac.compare_digest(token.encode("utf-8"), expected.encode("utf-8"))


class TBankNetworkError(Exception):
    """Transient HTTP/timeout failure from T-Bank API."""


class TBankClient:
    """Async T-Bank REST client with one retry on network errors."""

    def __init__(
        self,
        *,
        terminal_key: str,
        password: str,
        api_base_url: str,
        session: aiohttp.ClientSession,
        ssl_context: ssl.SSLContext | None = None,
    ) -> None:
        """Store terminal credentials, shared session and TLS trust for T-Bank.

        По умолчанию - контекст с НУЦ Минцифры: его корня нет в системном bundle
        образа. Контекст вешается на запрос, поэтому общая сессия бота не
        начинает доверять НУЦ для остальных хостов.
        """
        self._terminal_key = terminal_key
        self._password = password
        self._api_base_url = api_base_url.rstrip("/")
        self._session = session
        self._ssl_context = ssl_context or russian_trusted_ssl_context()

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential_jitter(initial=0.5, max=2.0),
        retry=retry_if_exception_type(TBankNetworkError),
        reraise=True,
    )
    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        body.setdefault("TerminalKey", self._terminal_key)
        body["Token"] = build_tbank_token(body, self._password)
        try:
            async with self._session.post(
                f"{self._api_base_url}{path}",
                json=body,
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=self._ssl_context,
            ) as resp:
                data = cast(dict[str, Any], await resp.json())
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise TBankNetworkError(str(exc)) from exc
        if not isinstance(data, dict):
            raise TBankNetworkError("unexpected response format")
        return data

    async def init(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Init payment; keep OrderId stable across retries."""
        return await self._post("/Init", payload)

    async def cancel(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /Cancel with signed payload."""
        return await self._post("/Cancel", payload)
