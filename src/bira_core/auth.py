"""SDK-free superuser check shared by platform filters."""

from collections.abc import Collection

__all__ = ["is_superadmin"]


def is_superadmin(user_id: int, superusers: Collection[int]) -> bool:
    """Check Superadmin."""
    return user_id in superusers
