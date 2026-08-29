from dataclasses import dataclass, field

from aiogram import Router
from aiogram.types import Chat, Message, Update, User
from aiogram.types.error_event import ErrorEvent

from bira_core.notify import Alerts
from bira_core.tgbot import register_error_handlers


@dataclass
class FakeSender:
    sent: list[tuple[int, str]] = field(default_factory=list)

    async def send_message(self, chat_id: int, text: str):
        self.sent.append((chat_id, text))


def test_register_error_handlers_adds_handler() -> None:
    router = Router()
    register_error_handlers(router)
    assert router.errors.handlers


async def test_register_error_handlers_alerts_owner() -> None:
    router = Router()
    sender = FakeSender()
    register_error_handlers(router, alerts=Alerts(sender, owner_chat_id=7))
    handler = router.errors.handlers[0].callback
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=0,
            chat=Chat(id=1, type="private"),
            from_user=User(id=1, is_bot=False, first_name="x"),
        ),
    )
    event = ErrorEvent(update=update, exception=RuntimeError("boom"))
    await handler(event)
    assert sender.sent and sender.sent[0][0] == 7
