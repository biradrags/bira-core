"""Dishka test provider overrides."""

import importlib
from typing import Any, cast
from unittest import mock

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from dishka import Provider, Scope, provide


class MockBotProvider(Provider):
    """Dishka providers returning mocked Bot/session for unit tests."""

    scope = Scope.APP

    @provide
    async def get_bot_session(self) -> BaseSession:
        """AsyncMock BaseSession for isolated Bot construction."""
        return mock.AsyncMock(BaseSession)

    @provide
    async def get_bot(self, session: BaseSession) -> Bot:
        """Bot with synthetic token wired to the mock session."""
        return Bot(token="42:FAKE_TOKEN_FOR_TESTS_ONLY", session=session)


class MockMessageManagerProvider(Provider):
    """Dishka provider for aiogram_dialog MockMessageManager."""

    scope = Scope.APP

    @provide
    def get_manager(self) -> Any:
        """Lazy-import aiogram_dialog.test_tools.MockMessageManager."""
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
    """Dishka provider for maxo.dialogs MockMessageManager."""

    scope = Scope.APP

    @provide
    def get_max_message_manager(self) -> Any:
        """Lazy-import maxo.dialogs.test_tools.MockMessageManager."""
        try:
            mod = importlib.import_module("maxo.dialogs.test_tools")
        except ImportError as e:
            e.add_note("pip install bira-core[max]")
            raise
        return mod.MockMessageManager()


class MockMaxDpProvider(Provider):
    """Dishka provider building a test MaxDispatcher with in-memory storage."""

    scope = Scope.APP

    @provide
    def get_json_storage(self) -> Any:
        """JsonMemoryStorage from maxo.dialogs test tools."""
        mod = importlib.import_module("maxo.dialogs.test_tools.memory_storage")
        return mod.JsonMemoryStorage()

    @provide
    def create_max_dispatcher(
        self,
        storage: Any,
        max_mm: Any,
    ) -> MaxDispatcher:
        """Dispatcher with DefaultKeyBuilder and injected message_manager."""
        maxo_mod = importlib.import_module("maxo")
        key_builder_mod = importlib.import_module("maxo.fsm.key_builder")

        key_builder = key_builder_mod.DefaultKeyBuilder(with_destiny=True)
        dp = maxo_mod.Dispatcher(storage=storage, key_builder=key_builder)
        dp.workflow_data["message_manager"] = max_mm
        return cast(Any, dp)  # type: ignore[no-any-return]
