import asyncio
from collections.abc import AsyncIterator

import pytest
from redis import VERSION as REDIS_VERSION
from redis.asyncio.connection import SSLConnection

from bira_core.redis import client as redis_client
from bira_core.redis.client import make_redis_client


class FakeRedis:
    """RESP-сервер: на каждую команду +OK, кроме тех соединений, где велено молчать."""

    def __init__(self) -> None:
        self.silent_connections: set[int] = set()
        self.connections = 0
        self.writers: list[asyncio.StreamWriter] = []
        self.url = ""

    async def handle(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self.connections += 1
        number = self.connections
        self.writers.append(writer)
        try:
            while command := await _read_command(reader):
                if number in self.silent_connections:
                    continue
                # redis-py 8 по умолчанию на RESP3 и ждёт на HELLO карту с proto
                if command[0].upper() == b"HELLO":
                    writer.write(b"%1\r\n+proto\r\n:" + command[1] + b"\r\n")
                else:
                    writer.write(b"+OK\r\n")
                await writer.drain()
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        finally:
            writer.close()


async def _read_command(reader: asyncio.StreamReader) -> list[bytes]:
    header = await reader.readline()
    if not header:
        return []
    parts = []
    for _ in range(int(header[1:])):
        size = int((await reader.readline())[1:])
        parts.append((await reader.readexactly(size + 2))[:-2])
    return parts


@pytest.fixture
async def fake_redis() -> AsyncIterator[FakeRedis]:
    fake = FakeRedis()
    server = await asyncio.start_server(fake.handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    fake.url = f"redis://:secret@127.0.0.1:{port}/0"
    async with server:
        yield fake


async def test_new_connection_survives_hung_auth(
    fake_redis: FakeRedis, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(redis_client, "DEFAULT_SOCKET_TIMEOUT", 0.2)
    fake_redis.silent_connections = {1}
    client = make_redis_client(fake_redis.url)
    try:
        assert await client.set("k", "v") is True
    finally:
        await client.aclose()
    assert fake_redis.connections == 2


async def test_rediss_url_keeps_tls_connection() -> None:
    expected = (
        redis_client._HandshakeRetrySSLConnection
        if REDIS_VERSION < (7, 2)
        else SSLConnection
    )
    client = make_redis_client("rediss://:secret@127.0.0.1:6379/0")
    try:
        assert client.connection_pool.connection_class is expected
    finally:
        await client.aclose()


async def test_live_connection_survives_server_drop(fake_redis: FakeRedis) -> None:
    client = make_redis_client(fake_redis.url)
    try:
        assert await client.set("k", "v") is True
        fake_redis.writers[0].transport.abort()
        assert await client.set("k", "v") is True
    finally:
        await client.aclose()
    assert fake_redis.connections == 2
