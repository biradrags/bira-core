import pytest
from aiogram.exceptions import TelegramBadRequest

from bira_core.tgbot.forum import TOPIC_GONE_MARKERS, is_topic_gone


@pytest.mark.asyncio
async def test_topic_gone_markers_union() -> None:
    assert "thread not found" in TOPIC_GONE_MARKERS
    assert "topic_deleted" in TOPIC_GONE_MARKERS
    assert "TOPIC_DELETED" in TOPIC_GONE_MARKERS
    assert "message thread not found" in TOPIC_GONE_MARKERS
    assert "TOPIC_ID_INVALID" in TOPIC_GONE_MARKERS
    assert "topic not found" in TOPIC_GONE_MARKERS
    assert "topic_not_found" in TOPIC_GONE_MARKERS


@pytest.mark.parametrize(
    "message",
    [
        "thread not found",
        "message thread not found",
        "TOPIC_DELETED",
        "topic_deleted",
        "TOPIC_ID_INVALID",
        "Bad Request: TOPIC_ID_INVALID",
        "topic not found",
        "topic_not_found",
    ],
)
def test_is_topic_gone_covers_every_marker(message: str) -> None:
    exc = TelegramBadRequest(method="sendMessage", message=message)
    assert is_topic_gone(exc) is True


def test_is_topic_gone_false_for_other_errors() -> None:
    other = TelegramBadRequest(method="sendMessage", message="chat not found")
    assert is_topic_gone(other) is False
    assert is_topic_gone(RuntimeError("thread not found")) is False
