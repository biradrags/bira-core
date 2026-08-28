from bira_core.protect.heuristics import IsLikelyBot, StartDeduper


def test_start_deduper_window() -> None:
    t = 0.0
    deduper = StartDeduper(10, clock=lambda: t)
    assert deduper.is_duplicate(1) is False
    assert deduper.is_duplicate(1) is True
    t += 11
    assert deduper.is_duplicate(1) is False


async def test_is_likely_bot_blocks_high_score() -> None:
    from aiogram.types import Chat, Message, User

    filt = IsLikelyBot(threshold=1, score_no_username=2)
    msg = Message(
        message_id=1,
        date=0,
        chat=Chat(id=1, type="private"),
        from_user=User(id=1, is_bot=False, first_name="x"),
    )
    assert await filt(msg) is False
