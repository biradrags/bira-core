from bira_core.tgbot import IsSuperAdmin, is_superadmin


def test_predicate() -> None:
    assert is_superadmin(1, {1, 2})
    assert not is_superadmin(3, {1, 2})


async def test_filter_wraps_predicate() -> None:
    f = IsSuperAdmin(superusers={42})

    class _U:
        id = 42

    class _M:
        from_user = _U()

    assert await f(_M()) is True
