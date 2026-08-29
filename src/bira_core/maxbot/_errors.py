MESSAGE_GONE_MARKERS = (
    "message to delete not found",
    "message can't be deleted",
)


def is_message_gone(err: BaseException) -> bool:
    msg = str(getattr(err, "message", err) or "").lower()
    return any(marker in msg for marker in MESSAGE_GONE_MARKERS)
