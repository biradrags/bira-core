"""Dishka database session provider."""

from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bira_core.db.url import DbDsn, build_url


class DbProvider(Provider):
    """Dishka APP-scoped engine, session pool, and request session."""

    scope = Scope.APP

    def __init__(
        self,
        *,
        pool_size: int,
        max_overflow: int,
        pool_recycle: int = 1800,
        connect_timeout: float | None = None,
    ) -> None:
        """Пул и таймауты engine(); pool_recycle короче простоя, после которого Fly рвёт соединения."""
        super().__init__()
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._pool_recycle = pool_recycle
        self._connect_timeout = connect_timeout

    @provide
    async def engine(self, dsn: DbDsn) -> AsyncIterable[AsyncEngine]:
        """Yield async engine; dispose on container shutdown."""
        url = build_url(dsn)
        connect_args: dict[str, object] = {}
        host = (url.host or "").lower()
        if host.endswith((".flycast", ".internal")):
            connect_args["ssl"] = False
        if self._connect_timeout is not None:
            connect_args["timeout"] = self._connect_timeout
        engine = create_async_engine(
            url=url,
            pool_pre_ping=True,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_timeout=5,
            pool_recycle=self._pool_recycle,
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
