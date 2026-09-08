"""Dialog widgets and cancel actions."""

from typing import Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.protocols import DialogManager as DialogManagerProtocol
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Text

from bira_core.kbd import DEFAULT_ROW_CHARS, wrap_by_label_width


async def cancel_delete(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    """Finish dialog, reset stack, and delete the callback message."""
    await manager.done(show_mode=ShowMode.NO_UPDATE)
    await manager.reset_stack(remove_keyboard=True)
    message = callback.message
    if not isinstance(message, Message):
        return
    business_connection_id = message.business_connection_id
    if business_connection_id and message.bot is not None:
        await message.bot.delete_business_messages(
            business_connection_id, [message.message_id]
        )
        return
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


class ProgressSteps(Text):
    """Render filled/empty step indicators for multi-step dialogs."""

    def __init__(
        self,
        steps: int,
        current_step: int,
        filled: str = "🟥",
        empty: str = "⬜",
        when: Any = None,
    ) -> None:
        """Store step count, current index, and filled/empty glyphs."""
        super().__init__(when)
        self.steps = steps
        self.current_step = current_step
        self.filled = filled
        self.empty = empty

    async def _render_text(
        self, data: dict[str, Any], manager: DialogManagerProtocol
    ) -> str:
        return (
            self.filled * self.current_step
            + self.empty * (self.steps - self.current_step)
            + f" {self.current_step}/{self.steps}"
        )


class AdaptiveGroup(Group):
    """Keyboard Group that wraps buttons via wrap_by_label_width."""

    def __init__(
        self,
        *buttons: Any,
        max_row_chars: int = DEFAULT_ROW_CHARS,
        id: str | None = None,
        when: Any = None,
    ) -> None:
        """Remember max_row_chars for label-width wrapping."""
        super().__init__(*buttons, id=id, width=1, when=when)
        self.max_row_chars = max_row_chars

    def _wrap_kbd(self, kbd: list[Any]) -> list[list[Any]]:  # type: ignore[override]  # Group._wrap_kbd типизирован уже, чем принимает
        return wrap_by_label_width(kbd, self.max_row_chars)
