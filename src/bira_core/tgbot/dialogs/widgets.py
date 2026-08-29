from typing import Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.protocols import DialogManager as DialogManagerProtocol
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Text

from bira_core.kbd import DEFAULT_ROW_CHARS, wrap_by_label_width


async def cancel_delete(
    c: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await manager.done(show_mode=ShowMode.NO_UPDATE)
    await manager.reset_stack(remove_keyboard=True)
    if not isinstance(c.message, Message):
        return
    bci = c.message.business_connection_id
    if bci and c.message.bot is not None:
        await c.message.bot.delete_business_messages(bci, [c.message.message_id])
    else:
        try:
            await c.message.delete()
        except TelegramBadRequest:
            pass


class ProgressSteps(Text):
    def __init__(
        self,
        steps: int,
        current_step: int,
        filled: str = "🟥",
        empty: str = "⬜",
        when: Any = None,
    ) -> None:
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
    def __init__(
        self,
        *buttons: Any,
        max_row_chars: int = DEFAULT_ROW_CHARS,
        id: str | None = None,
        when: Any = None,
    ) -> None:
        super().__init__(*buttons, id=id, width=1, when=when)
        self.max_row_chars = max_row_chars

    def _wrap_kbd(self, kbd: list[Any]) -> list[list[Any]]:  # type: ignore[override]
        return wrap_by_label_width(kbd, self.max_row_chars)


async def _cancel_reset(
    c: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await manager.done(show_mode=ShowMode.NO_UPDATE)
    await manager.reset_stack(remove_keyboard=True)
    if not isinstance(c.message, Message):
        return
    text = "✘ Все диалоги закрыты ✘\nГотов к обработке новых запросов"
    if c.message.text:
        await c.message.edit_text(text, reply_markup=None)
    elif c.message.caption:
        await c.message.edit_caption(caption=text, reply_markup=None)
