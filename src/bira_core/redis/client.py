"""Async Redis client factory."""

from __future__ import annotations

from typing import Any

import redis.asyncio as redis
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
            supported_errors=_RECONNECT_ERRORS,  # type: ignore[arg-type]
        ),
        "retry_on_error": list(_RECONNECT_ERRORS),
    }


def make_redis_client(url: str, *, decode_responses: bool = True) -> redis.Redis:
    """from_url client with fleet reconnect and decode_responses default."""
    return redis.from_url(
        url,
        **redis_connection_kwargs(decode_responses=decode_responses),
    )
