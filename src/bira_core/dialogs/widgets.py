from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.protocols import DialogManager as DialogManagerProtocol
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Text

from bira_core.kbd import DEFAULT_ROW_CHARS, wrap_button_rows


async def cancel_reset(
    c: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await manager.done(show_mode=ShowMode.NO_UPDATE)
    await manager.reset_stack(remove_keyboard=True)
    text = "✘ Все диалоги закрыты ✘\nГотов к обработке новых запросов"
    if c.message and c.message.text:
        await c.message.edit_text(text, reply_markup=None)
    elif c.message and c.message.caption:
        await c.message.edit_caption(caption=text, reply_markup=None)


class ProgressSteps(Text):
    def __init__(
        self,
        steps: int,
        current_step: int,
        filled: str = "🟥",
        empty: str = "⬜",
        when=None,
    ) -> None:
        super().__init__(when)
        self.steps = steps
        self.current_step = current_step
        self.filled = filled
        self.empty = empty

    async def _render_text(
        self, data: dict, manager: DialogManagerProtocol
    ) -> str:
        return (
            self.filled * self.current_step
            + self.empty * (self.steps - self.current_step)
            + f" {self.current_step}/{self.steps}"
        )


class AdaptiveGroup(Group):
    def __init__(
        self,
        *buttons,
        max_row_chars: int = DEFAULT_ROW_CHARS,
        id: str | None = None,
        when=None,
    ) -> None:
        super().__init__(*buttons, id=id, width=1, when=when)
        self.max_row_chars = max_row_chars

    def _wrap_kbd(self, kbd):
        return wrap_button_rows(kbd, self.max_row_chars)
