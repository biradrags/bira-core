"""Dishka test providers for the MAX side."""

import importlib
from typing import Any, cast

from dishka import Provider, Scope, provide
from maxo import Dispatcher as MaxDispatcher

__all__ = ["MockMaxDpProvider", "MockMaxMessageManagerProvider"]


class MockMaxMessageManagerProvider(Provider):
    """Dishka provider for maxo.dialogs MockMessageManager."""

    scope = Scope.APP

    @provide
    def get_max_message_manager(self) -> Any:
        """Lazy-import maxo.dialogs.test_tools.MockMessageManager."""
        mod = importlib.import_module("maxo.dialogs.test_tools")
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
        key_builder_mod = importlib.import_module("maxo.fsm.key_builder")

        key_builder = key_builder_mod.DefaultKeyBuilder(with_destiny=True)
        dp = MaxDispatcher(storage=storage, key_builder=key_builder)
        dp.workflow_data["message_manager"] = max_mm
        return cast(Any, dp)  # type: ignore[no-any-return]
