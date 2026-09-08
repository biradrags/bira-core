from bira_core.protect.heuristics import StartDeduper


def test_start_deduper_window() -> None:
    t = 0.0
    deduper = StartDeduper(10, clock=lambda: t)
    assert deduper.is_duplicate(1) is False
    assert deduper.is_duplicate(1) is True
    t += 11
    assert deduper.is_duplicate(1) is False
