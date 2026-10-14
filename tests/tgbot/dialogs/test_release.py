from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram_dialog.manager.message_manager import MessageManager
from dishka import Provider, Scope, make_async_container, provide

from bira_core.tgbot.dialogs.release import (
    ReleaseMiddleware,
    ReleasingMessageManager,
    release_current,
)


class _Dao:
    def __init__(self) -> None:
        self.released = 0

    async def release(self) -> None:
        self.released += 1


class _Provider(Provider):
    @provide(scope=Scope.REQUEST)
    def dao(self) -> _Dao:
        return _Dao()


async def test_middleware_exposes_dao_to_release_and_resets() -> None:
    container = make_async_container(_Provider())
    seen: dict[str, _Dao] = {}

    async def handler(_: Any, data: dict[str, Any]) -> None:
        seen["dao"] = await data["dishka_container"].get(_Dao)
        await release_current()

    async with container() as request:
        await ReleaseMiddleware(_Dao)(
            handler, MagicMock(), {"dishka_container": request}
        )

    assert seen["dao"].released == 1
    await release_current()  # вне апдейта ContextVar пуст - no-op
    assert seen["dao"].released == 1
    await container.close()


async def test_message_manager_releases_before_each_telegram_call() -> None:
    dao = _Dao()
    calls: list[str] = []

    def recorder(name: str) -> AsyncMock:
        return AsyncMock(side_effect=lambda *_: calls.append(f"{name}:{dao.released}"))

    async def handler(_: Any, __: dict[str, Any]) -> None:
        manager = ReleasingMessageManager()
        with (
            patch.object(MessageManager, "show_message", recorder("show")),
            patch.object(MessageManager, "remove_kbd", recorder("remove")),
            patch.object(MessageManager, "answer_callback", recorder("answer")),
        ):
            await manager.show_message(MagicMock(), MagicMock(), None)
            await manager.remove_kbd(MagicMock(), MagicMock(), None)
            await manager.answer_callback(MagicMock(), MagicMock())

    class _Fixed(Provider):
        @provide(scope=Scope.REQUEST)
        def dao(self) -> _Dao:
            return dao

    container = make_async_container(_Fixed())
    async with container() as request:
        await ReleaseMiddleware(_Dao)(
            handler, MagicMock(), {"dishka_container": request}
        )

    assert calls == ["show:1", "remove:2", "answer:3"]
    await container.close()
