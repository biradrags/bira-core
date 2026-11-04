"""Dishka database session provider."""

import functools
import json
from collections.abc import AsyncIterable, Callable, Mapping
from ssl import SSLContext
from typing import Any

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bira_core.db.url import DbDsn, build_url

_json_dumps = functools.partial(json.dumps, ensure_ascii=False)


class DbProvider(Provider):
    """Dishka APP-scoped engine, session pool, and request session."""

    scope = Scope.APP

    def __init__(
        self,
        *,
        pool_size: int,
        max_overflow: int,
        pool_recycle: int = 1800,
        pool_timeout: float = 5,
        connect_timeout: float | None = None,
        # None - автоопределение: False для .flycast/.internal, иначе дефолт драйвера
        ssl: bool | str | SSLContext | None = None,
        server_settings: Mapping[str, str] | None = None,
        # ПДн из параметров запроса не попадают в текст исключений и в лог запросов
        hide_parameters: bool = True,
        # ensure_ascii=False - кириллица в JSON читаемая
        json_serializer: Callable[[Any], str] = _json_dumps,
    ) -> None:
        """Пул, таймауты и connect_args engine().

        pool_recycle короче простоя, после которого Fly рвёт соединения.
        """
        super().__init__()
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._pool_recycle = pool_recycle
        self._pool_timeout = pool_timeout
        self._connect_timeout = connect_timeout
        self._ssl = ssl
        self._server_settings = server_settings
        self._hide_parameters = hide_parameters
        self._json_serializer = json_serializer

    @provide
    async def engine(self, dsn: DbDsn) -> AsyncIterable[AsyncEngine]:
        """Yield async engine; dispose on container shutdown."""
        url = build_url(dsn)
        connect_args: dict[str, object] = {}
        host = (url.host or "").lower()
        if self._ssl is not None:
            connect_args["ssl"] = self._ssl
        elif host.endswith((".flycast", ".internal")):
            connect_args["ssl"] = False
        if self._server_settings is not None:
            connect_args["server_settings"] = dict(self._server_settings)
        if self._connect_timeout is not None:
            connect_args["timeout"] = self._connect_timeout
        engine = create_async_engine(
            url=url,
            pool_pre_ping=True,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_timeout=self._pool_timeout,
            pool_recycle=self._pool_recycle,
            hide_parameters=self._hide_parameters,
            json_serializer=self._json_serializer,
            connect_args=connect_args,
        )
        yield engine
        await engine.dispose(True)

    @provide
    def pool(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        """Session factory without autoflush/autocommit."""
        return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def session(
        self, pool: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """Open one AsyncSession per request scope."""
        async with pool() as session:
            yield session
