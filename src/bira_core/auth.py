from collections.abc import Collection

__all__ = ["is_superadmin"]


def is_superadmin(user_id: int, superusers: Collection[int]) -> bool:
    return user_id in superusers
