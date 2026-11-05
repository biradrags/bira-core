import pytest
from dishka import Provider, Scope, alias, from_context, provide
from dishka.exceptions import GraphMissingFactoryError

from bira_core.testing.wiring import assert_container_builds


class Config:
    pass


class Userbot:
    pass


class Dao:
    pass


class Broken:
    pass


class AppProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=Config, scope=Scope.APP)

    @provide
    def userbot(self, config: Config) -> Userbot | None:
        return None

    @provide(scope=Scope.REQUEST)
    def dao(self, config: Config) -> Dao:
        return Dao()

    dao_alias = alias(source=Dao, provides=object)


class BrokenProvider(Provider):
    scope = Scope.APP

    @provide
    def broken(self) -> Broken:
        raise RuntimeError("no network in tests")


async def test_container_builds() -> None:
    await assert_container_builds(
        AppProvider(), context={Config: Config()}, requested=[Userbot | None]
    )


async def test_bare_type_of_optional_factory_reported() -> None:
    with pytest.raises(AssertionError, match="Userbot.*NoFactoryError"):
        await assert_container_builds(
            AppProvider(), context={Config: Config()}, requested=[Userbot]
        )


async def test_factory_failure_reported_and_skippable() -> None:
    with pytest.raises(AssertionError, match="Broken.*RuntimeError: no network"):
        await assert_container_builds(BrokenProvider())

    await assert_container_builds(BrokenProvider(), skip_types=[Broken])


async def test_missing_context_value_reported() -> None:
    with pytest.raises(AssertionError, match="NoContextValueError"):
        await assert_container_builds(AppProvider())


class OrphanProvider(Provider):
    scope = Scope.APP

    @provide
    def dao(self, config: Config) -> Dao:
        return Dao()


async def test_provider_without_factory_fails_build() -> None:
    with pytest.raises(GraphMissingFactoryError):
        await assert_container_builds(OrphanProvider())
