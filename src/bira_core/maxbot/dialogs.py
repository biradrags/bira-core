from maxo.dialogs import DialogManager, ShowMode
from maxo.dialogs.widgets.kbd import Button
from maxo.errors import MaxBotBadRequestError
from maxo.routing.updates import MessageCallback


def _message_id_for_delete(
    event: MessageCallback, manager: DialogManager
) -> str | None:
    if event.message is not None:
        return event.message.body.mid
    stack = manager.current_stack()
    return stack.last_message_id if stack else None


async def cancel_delete(
    event: MessageCallback,
    _button: Button,
    manager: DialogManager,
) -> None:
    message_id = _message_id_for_delete(event, manager)
    bot = manager.middleware_data["bot"]
    await manager.done(show_mode=ShowMode.NO_UPDATE)
    await manager.reset_stack(remove_keyboard=True)
    if message_id is not None:
        try:
            await bot.delete_message(message_id=message_id)
        except MaxBotBadRequestError as err:
            if (
                "message to delete not found" not in err.message
                and "message can't be deleted" not in err.message
            ):
                raise
