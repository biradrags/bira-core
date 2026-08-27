from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.interfaces import ORMOption

Model_co = TypeVar("Model_co", bound=DeclarativeBase, covariant=True)


class BaseDAO[Model_co]:
    def __init__(self, model: type[Model_co], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def _get_all(self, options: Sequence[ORMOption] = ()) -> list[Model_co]:
        result = await self.session.scalars(select(self.model).options(*options))
        return list(result.all())

    async def _get_by_id(
        self,
        id_: int,
        options: Sequence[ORMOption] | None = None,
        populate_existing: bool = False,
    ) -> Model_co | None:
        return await self.session.get(
            self.model,
            id_,
            options=options,
            populate_existing=populate_existing,
        )

    def _save(self, obj: Model_co) -> None:
        self.session.add(obj)

    async def _delete(self, obj: Model_co) -> None:
        await self.session.delete(obj)

    async def _count(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return int(result.scalar_one())

    async def _flush(self, *objects: Model_co) -> None:
        await self.session.flush(objects)
