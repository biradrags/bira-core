from bira_core.protect.flood_guard import FloodGuard


def test_burst_then_deny() -> None:
    t = 0.0

    def clock() -> float:
        return t

    guard = FloodGuard(
        per_key_rate=1.0,
        per_key_burst=2,
        global_rate=10.0,
        global_burst=10,
        clock=clock,
    )
    assert guard.allow("a") is True
    assert guard.allow("a") is True
    assert guard.allow("a") is False
    t += 2.0
    assert guard.allow("a") is True


def test_global_bucket_limits_fresh_key() -> None:
    t = 0.0

    def clock() -> float:
        return t

    guard = FloodGuard(
        per_key_rate=10.0,
        per_key_burst=10,
        global_rate=1.0,
        global_burst=1,
        clock=clock,
    )
    assert guard.allow("a") is True
    assert guard.allow("b") is False
