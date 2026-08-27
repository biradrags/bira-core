from collections.abc import AsyncIterable, Sequence
from typing import Any

from dishka import AsyncContainer, Provider, Scope, provide
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bira_core.db.url import DbDsn, build_url
from bira_core.di._redis import make_redis_client
from bira_core.notify.alerts import Alerts
from bira_core.notify.send import MessageSender


class DbProvider(Provider):
    scope = Scope.APP

    def __init__(self, *, pool_size: int, max_overflow: int) -> None:
        super().__init__()
        self._pool_size = pool_size
        self._max_overflow = max_overflow

    @provide
    async def engine(self, dsn: DbDsn) -> AsyncIterable[AsyncEngine]:
        url = build_url(dsn)
        connect_args: dict[str, object] = {}
        host = (url.host or "").lower()
        if host.endswith((".flycast", ".internal")):
            connect_args["ssl"] = False
        engine = create_async_engine(
            url=url,
            pool_pre_ping=True,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_timeout=5,
            pool_recycle=1800,
            connect_args=connect_args,
        )
        yield engine
        await engine.dispose(True)

    @provide
    def pool(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
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
        async with pool() as session:
            yield session


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    async def redis(self, redis_url: str) -> AsyncIterable[Redis]:
        client = make_redis_client(redis_url)
        yield client
        await client.aclose()


class NotifierProvider(Provider):
    @provide
    def alerts(self, sender: MessageSender, owner_chat_id: int) -> Alerts:
        return Alerts(sender, owner_chat_id)


async def warm_up(container: AsyncContainer, types: Sequence[type[Any]]) -> None:
    async with container() as request:
        for dep in types:
            await request.get(dep)
