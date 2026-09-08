"""Telegram forum-topic error detection."""

from aiogram.exceptions import TelegramBadRequest

__all__ = ["TOPIC_GONE_MARKERS", "is_topic_gone"]

TOPIC_GONE_MARKERS = frozenset(
    {
        "thread not found",
        "topic_deleted",
        "TOPIC_DELETED",
        "message thread not found",
    }
)


def is_topic_gone(exc: BaseException) -> bool:
    """True когда Telegram сказал, что топика больше нет.

    Публичная: распознать «топик удалён» нужно и тем, кто его не пересоздаёт,
    а скипает или гасит доставку.
    """
    if not isinstance(exc, TelegramBadRequest):
        return False
    text = str(exc).lower()
    return any(marker.lower() in text for marker in TOPIC_GONE_MARKERS)
