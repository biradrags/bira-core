"""Async Redis client factory."""

from __future__ import annotations

from typing import Any

import redis.asyncio as redis
from redis import VERSION as REDIS_VERSION
from redis.asyncio.connection import AbstractConnection, Connection, SSLConnection
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

DEFAULT_SOCKET_TIMEOUT = 5
DEFAULT_RETRY_ATTEMPTS = 2

_RECONNECT_ERRORS: tuple[type[BaseException], ...] = (
    RedisConnectionError,
    RedisTimeoutError,
    OSError,
    TypeError,
)


def redis_connection_kwargs(*, decode_responses: bool = True) -> dict[str, Any]:
    """Default kwargs for redis.from_url (keepalive, retry, decode)."""
    return {
        "decode_responses": decode_responses,
        "socket_keepalive": True,
        "socket_timeout": DEFAULT_SOCKET_TIMEOUT,
        "retry": Retry(
            ExponentialBackoff(cap=2, base=0.1),
            retries=DEFAULT_RETRY_ATTEMPTS,
            supported_errors=_RECONNECT_ERRORS,  # type: ignore[arg-type]  # redis-py сужает до RedisError, ретраим ещё OSError/TypeError
        ),
        "retry_on_error": list(_RECONNECT_ERRORS),
    }


def make_redis_client(url: str, *, decode_responses: bool = True) -> redis.Redis:
    """from_url client with fleet reconnect and decode_responses default.

    On redis-py < 7.2 also retries the AUTH/HELLO handshake of a new connection.
    """
    client = redis.from_url(
        url,
        **redis_connection_kwargs(decode_responses=decode_responses),
    )
    # redis-py 7.2 (#3863) сам ретраит connect вместе с рукопожатием, ниже - бэкпорт
    if REDIS_VERSION < (7, 2):
        pool = client.connection_pool
        pool.connection_class = _HANDSHAKE_RETRY.get(
            pool.connection_class, pool.connection_class
        )
    return client


async def _connect_with_handshake_retry(conn: AbstractConnection) -> None:
    await conn.retry.call_with_retry(
        lambda: conn.connect_check_health(
            check_health=True, retry_socket_connect=False
        ),
        lambda _error: conn.disconnect(),
    )


class _HandshakeRetryConnection(Connection):
    async def connect(self) -> None:
        await _connect_with_handshake_retry(self)


class _HandshakeRetrySSLConnection(SSLConnection):
    async def connect(self) -> None:
        await _connect_with_handshake_retry(self)


_HANDSHAKE_RETRY: dict[type[AbstractConnection], type[AbstractConnection]] = {
    Connection: _HandshakeRetryConnection,
    SSLConnection: _HandshakeRetrySSLConnection,
}
