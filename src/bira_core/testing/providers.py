import importlib
from typing import Any, cast
from unittest import mock

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from dishka import Provider, Scope, provide


class MockBotProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_bot_session(self) -> BaseSession:
        return mock.AsyncMock(BaseSession)

    @provide
    async def get_bot(self, session: BaseSession) -> Bot:
        return Bot(token="42:FAKE_TOKEN_FOR_TESTS_ONLY", session=session)


class MockMessageManagerProvider(Provider):
    scope = Scope.APP

    @provide
    def get_manager(self) -> Any:
        try:
            mod = importlib.import_module("aiogram_dialog.test_tools")
        except ImportError as e:
            e.add_note("pip install aiogram_dialog")
            raise
        return mod.MockMessageManager()


try:
    from maxo import Dispatcher as MaxDispatcher
except ImportError:  # pragma: no cover - optional [max] extra
    MaxDispatcher = Any  # type: ignore[misc,assignment]


class MockMaxMessageManagerProvider(Provider):
    scope = Scope.APP

    @provide
    def get_max_message_manager(self) -> Any:
        try:
            mod = importlib.import_module("maxo.dialogs.test_tools")
        except ImportError as e:
            e.add_note("pip install bira-core[max]")
            raise
        return mod.MockMessageManager()


class MockMaxDpProvider(Provider):
    scope = Scope.APP

    @provide
    def get_json_storage(self) -> Any:
        mod = importlib.import_module("maxo.dialogs.test_tools.memory_storage")
        return mod.JsonMemoryStorage()

    @provide
    def create_max_dispatcher(
        self,
        storage: Any,
        max_mm: Any,
    ) -> MaxDispatcher:
        maxo_mod = importlib.import_module("maxo")
        key_builder_mod = importlib.import_module("maxo.fsm.key_builder")

        key_builder = key_builder_mod.DefaultKeyBuilder(with_destiny=True)
        dp = maxo_mod.Dispatcher(storage=storage, key_builder=key_builder)
        dp.workflow_data["message_manager"] = max_mm
        return cast(Any, dp)  # type: ignore[no-any-return]
