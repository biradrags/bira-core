from dataclasses import dataclass

import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.exceptions import GraphMissingFactoryError, NoFactoryError

from bira_core.db.url import DbDsn
from bira_core.di import DbProvider, warm_up


@dataclass
class _Dsn:
    host: str = "localhost"
    port: int = 5499
    user: str = "test"
    password: str = "test"
    name: str = "test"


class _DsnProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    def dsn(self) -> DbDsn:
        return _Dsn()


async def test_warm_up_raises_on_missing_dependency() -> None:
    container = make_async_container(
        DbProvider(pool_size=1, max_overflow=0), _DsnProvider()
    )
    with pytest.raises((GraphMissingFactoryError, NoFactoryError)):
        await warm_up(container, [int])
    await container.close()


def test_db_provider_requires_dsn() -> None:
    with pytest.raises(GraphMissingFactoryError):
        make_async_container(DbProvider(pool_size=1, max_overflow=0))
