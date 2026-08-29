from collections.abc import Collection
from typing import Protocol

from maxo.routing.ctx import Ctx
from maxo.routing.filters.base import BaseFilter
from maxo.types import BaseUpdate

from bira_core.auth import is_superadmin as _is_superadmin


class MaxUser(Protocol):
    user_id: int


class IsSuperAdmin(BaseFilter[BaseUpdate]):
    def __init__(self, *, superusers: Collection[int]) -> None:
        self._superusers = superusers

    async def __call__(self, update: BaseUpdate, ctx: Ctx) -> bool:
        user: MaxUser | None = ctx.get("user")
        if user is None:
            return False
        return _is_superadmin(user.user_id, self._superusers)
