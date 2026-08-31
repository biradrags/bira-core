"""Dishka test providers for the aiogram side."""

import importlib
from typing import Any
from unittest import mock

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from dishka import Provider, Scope, provide

__all__ = ["MockBotProvider", "MockMessageManagerProvider"]


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
            e.add_note("pip install bira-core[dialogs]")
            raise
        return mod.MockMessageManager()
