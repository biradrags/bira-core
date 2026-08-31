from aiogram.types import Chat, Message, User

from bira_core.protect.heuristics import IsLikelyBot, StartDeduper


def _message(**user_kwargs: object) -> Message:
    defaults: dict[str, object] = {"id": 1, "is_bot": False, "first_name": "x"}
    defaults.update(user_kwargs)
    return Message(
        message_id=1,
        date=0,
        chat=Chat(id=1, type="private"),
        from_user=User(**defaults),  # type: ignore[arg-type]
    )


def test_start_deduper_window() -> None:
    t = 0.0
    deduper = StartDeduper(10, clock=lambda: t)
    assert deduper.is_duplicate(1) is False
    assert deduper.is_duplicate(1) is True
    t += 11
    assert deduper.is_duplicate(1) is False


async def test_flags_sender_at_or_above_threshold() -> None:
    filt = IsLikelyBot(threshold=1, score_no_username=2)

    assert await filt(_message()) is True


async def test_does_not_flag_sender_below_threshold() -> None:
    filt = IsLikelyBot(threshold=3, score_no_username=1)

    assert await filt(_message(username="ivan", language_code="ru")) is False


async def test_premium_pulls_score_down() -> None:
    filt = IsLikelyBot(threshold=1, score_no_username=1, score_premium=-2)

    assert await filt(_message(is_premium=True)) is False


async def test_fresh_id_scores_above_raised_threshold() -> None:
    filt = IsLikelyBot(threshold=1, score_no_username=0, score_new_id=1)

    assert await filt(_message(id=9_000_000_000, username="u")) is True
    assert await filt(_message(id=7_000_000_000, username="u")) is False


async def test_bot_sender_is_never_flagged() -> None:
    filt = IsLikelyBot(threshold=0)

    assert await filt(_message(is_bot=True)) is False
