from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock

import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.exceptions import GraphMissingFactoryError, NoFactoryError
from sqlalchemy.ext.asyncio import AsyncEngine

from bira_core.db.url import DbDsn
from bira_core.di.db import DbProvider
from bira_core.di.warmup import warm_up


@dataclass
class _Dsn:
    host: str = "localhost"
    port: int = 5499
    user: str = "test"
    password: str = "test"
    name: str = "test"


class _DsnProvider(Provider):
    scope = Scope.APP

    def __init__(self, host: str = "localhost") -> None:
        super().__init__()
        self._host = host

    @provide(scope=Scope.APP)
    def dsn(self) -> DbDsn:
        return _Dsn(host=self._host)


async def _engine_kwargs(
    monkeypatch: pytest.MonkeyPatch, host: str = "localhost", **provider_kw: Any
) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake(**kw: Any) -> AsyncMock:
        captured.update(kw)
        return AsyncMock()

    monkeypatch.setattr("bira_core.di.db.create_async_engine", fake)
    container = make_async_container(
        DbProvider(pool_size=1, max_overflow=0, **provider_kw), _DsnProvider(host)
    )
    await container.get(AsyncEngine)
    await container.close()
    return captured


async def test_warm_up_raises_on_missing_dependency() -> None:
    container = make_async_container(
        DbProvider(pool_size=1, max_overflow=0), _DsnProvider()
    )
    with pytest.raises((GraphMissingFactoryError, NoFactoryError)):
        await warm_up(container, [int])
    await container.close()


async def test_db_provider_pool_recycle_and_connect_timeout() -> None:
    container = make_async_container(
        DbProvider(pool_size=1, max_overflow=0, pool_recycle=300, connect_timeout=2),
        _DsnProvider(),
    )
    engine = await container.get(AsyncEngine)
    assert engine.pool._recycle == 300
    await container.close()


def test_db_provider_requires_dsn() -> None:
    with pytest.raises(GraphMissingFactoryError):
        make_async_container(DbProvider(pool_size=1, max_overflow=0))


async def test_db_provider_engine_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    kw = await _engine_kwargs(monkeypatch)
    assert kw["pool_timeout"] == 5
    assert kw["hide_parameters"] is True
    assert kw["json_serializer"]({"к": "в"}) == '{"к": "в"}'
    assert kw["connect_args"] == {}


@pytest.mark.parametrize("host", ["db.flycast", "app.internal"])
async def test_db_provider_fly_host_auto_ssl(
    monkeypatch: pytest.MonkeyPatch, host: str
) -> None:
    kw = await _engine_kwargs(monkeypatch, host=host)
    assert kw["connect_args"] == {"ssl": False}


async def test_db_provider_explicit_ssl_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    kw = await _engine_kwargs(monkeypatch, host="db.flycast", ssl="require")
    assert kw["connect_args"]["ssl"] == "require"
    kw = await _engine_kwargs(monkeypatch, host="localhost", ssl=False)
    assert kw["connect_args"]["ssl"] is False


async def test_db_provider_server_settings_and_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kw = await _engine_kwargs(
        monkeypatch,
        server_settings={"application_name": "app"},
        pool_timeout=10,
        hide_parameters=False,
        connect_timeout=2,
    )
    assert kw["connect_args"] == {
        "server_settings": {"application_name": "app"},
        "timeout": 2,
    }
    assert kw["pool_timeout"] == 10
    assert kw["hide_parameters"] is False
