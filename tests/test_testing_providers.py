from unittest import mock

import pytest
from aiogram import Bot
from dishka import make_async_container

import bira_core.testing
from bira_core.testing import MockBotProvider
from bira_core.testing.providers import MockMessageManagerProvider


async def test_mock_bot_provider_uses_mock_session() -> None:
    container = make_async_container(MockBotProvider())
    async with container() as request:
        bot = await request.get(Bot)
        assert isinstance(bot.session, mock.AsyncMock)
    await container.close()


def test_testing_import_without_aiogram_dialog() -> None:
    assert bira_core.testing.MockBotProvider is MockBotProvider


def test_mock_message_manager_requires_aiogram_dialog() -> None:
    with pytest.raises(ImportError, match="aiogram_dialog"):
        MockMessageManagerProvider().get_manager()
