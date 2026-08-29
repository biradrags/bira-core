from collections.abc import Sequence
from typing import Any

from dishka import AsyncContainer


async def warm_up(container: AsyncContainer, types: Sequence[type[Any]]) -> None:
    async with container() as request:
        for dep in types:
            await request.get(dep)
