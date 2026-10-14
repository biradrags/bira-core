from unittest.mock import AsyncMock, MagicMock, patch

from aiogram_dialog.manager.message_manager import MessageManager

from bira_core.tgbot.dialogs.release import (
    ReleasingMessageManager,
    bind_release,
    release_current,
)


class _Dao:
    def __init__(self) -> None:
        self.released = 0

    async def release(self) -> None:
        self.released += 1


async def test_bind_release_exposes_dao_and_resets() -> None:
    dao = _Dao()
    with bind_release(dao):
        await release_current()
    assert dao.released == 1
    await release_current()  # вне апдейта ContextVar пуст - no-op
    assert dao.released == 1


async def test_message_manager_releases_before_each_telegram_call() -> None:
    dao = _Dao()
    calls: list[str] = []

    def recorder(name: str) -> AsyncMock:
        return AsyncMock(side_effect=lambda *_: calls.append(f"{name}:{dao.released}"))

    manager = ReleasingMessageManager()
    with (
        bind_release(dao),
        patch.object(MessageManager, "show_message", recorder("show")),
        patch.object(MessageManager, "remove_kbd", recorder("remove")),
        patch.object(MessageManager, "answer_callback", recorder("answer")),
    ):
        await manager.show_message(MagicMock(), MagicMock(), None)
        await manager.remove_kbd(MagicMock(), MagicMock(), None)
        await manager.answer_callback(MagicMock(), MagicMock())

    assert calls == ["show:1", "remove:2", "answer:3"]
