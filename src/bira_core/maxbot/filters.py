from typing import Protocol

from maxo.routing.ctx import Ctx
from maxo.routing.filters.base import BaseFilter
from maxo.types import BaseUpdate


class MaxUser(Protocol):
    tg_id: int


class IsSuperAdmin(BaseFilter[BaseUpdate]):
    def __init__(self, superusers: frozenset[int] | set[int]) -> None:
        self._superusers = superusers

    async def __call__(self, update: BaseUpdate, ctx: Ctx) -> bool:
        user: MaxUser | None = ctx.get("user")
        if user is None:
            return False
        return user.tg_id in self._superusers
