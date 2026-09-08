import pytest
from sqlalchemy.orm import Mapped, mapped_column

from bira_core.db.base import Base
from bira_core.db.dao import BaseDAO

pytestmark = pytest.mark.xdist_group(name="postgres")


class Thing(Base):
    __tablename__ = "things"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]


class ThingDAO(BaseDAO[Thing]):
    def __init__(self, session):
        super().__init__(Thing, session)

    async def by_id(self, id_: int) -> Thing | None:
        return await self._get_by_id(id_)


async def test_get_by_id_missing_returns_none(session) -> None:
    assert await ThingDAO(session).by_id(999) is None


async def test_save_flush_get(session) -> None:
    dao = ThingDAO(session)
    dao._save(Thing(id=1, title="t"))
    await dao._flush()
    got = await dao.by_id(1)
    assert got is not None and got.title == "t"


def test_no_commit_method() -> None:
    assert not hasattr(BaseDAO, "commit")
