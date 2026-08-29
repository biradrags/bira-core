"""SDK-free superuser check shared by platform filters."""

from collections.abc import Collection

__all__ = ["is_superadmin"]


def is_superadmin(user_id: int, superusers: Collection[int]) -> bool:
    """True when user_id is in the configured superuser set."""
    return user_id in superusers
