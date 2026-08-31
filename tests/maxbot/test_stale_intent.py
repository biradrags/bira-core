import pytest

pytest.importorskip("maxo")

from maxo import Dispatcher
from maxo.dialogs.api.exceptions import UnknownIntent
from maxo.types import MessageCallback

from bira_core.maxbot.dialogs.errors import (
    STALE_INTENT_EXCEPTIONS,
    clear_stale_intent,
    register_stale_intent,
)


class FakeBot:
    def __init__(self) -> None:
        self.deleted: list[str] = []

    async def delete_message(self, message_id: str) -> None:
        self.deleted.append(message_id)


def _callback(mid: str) -> MessageCallback:
    """Голый MessageCallback: хендлер обязан узнавать его по isinstance."""
    callback = object.__new__(MessageCallback)
    body = type("Body", (), {"mid": mid})()
    object.__setattr__(callback, "message", type("Msg", (), {"body": body})())
    return callback


def _error_event(callback: MessageCallback) -> object:
    return type(
        "ErrorEvent",
        (),
        {
            "exception": UnknownIntent("gone"),
            "update": type("Upd", (), {"update": callback})(),
        },
    )()


def test_registers_on_dispatcher_error_router() -> None:
    dp = Dispatcher()

    register_stale_intent(dp)

    assert dp.error.handlers, "stale-intent не зарегистрирован"


def test_exception_set_matches_canon() -> None:
    assert UnknownIntent in STALE_INTENT_EXCEPTIONS
    assert len(STALE_INTENT_EXCEPTIONS) == 3


async def test_deletes_orphaned_menu() -> None:
    bot = FakeBot()

    await clear_stale_intent(_error_event(_callback("mid-42")), {"bot": bot})  # type: ignore[arg-type]

    assert bot.deleted == ["mid-42"]


async def test_without_bot_in_context_does_not_raise() -> None:
    await clear_stale_intent(_error_event(_callback("mid-1")), {})  # type: ignore[arg-type]
