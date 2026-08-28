import importlib

import pytest

pytest.importorskip("maxo")

from dishka import make_async_container

from bira_core.testing.providers import MockMaxDpProvider, MockMaxMessageManagerProvider


@pytest.mark.asyncio
async def test_mock_max_providers_build_dispatcher() -> None:
    maxo = importlib.import_module("maxo")
    container = make_async_container(
        MockMaxMessageManagerProvider(),
        MockMaxDpProvider(),
    )
    async with container() as request:
        dp = await request.get(maxo.Dispatcher)
        assert dp is not None
    await container.close()
