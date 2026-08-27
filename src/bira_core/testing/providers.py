import importlib
from typing import Any
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
