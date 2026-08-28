import asyncio

import pytest
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column

from bira_core.db import Base
from bira_core.db.queries import claim_due, idempotent_transition

DSN = "postgresql+asyncpg://test:test@localhost:5499/test"


class StatusRow(Base):
    __tablename__ = "query_probe"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(16))
    due_at: Mapped[int] = mapped_column(Integer, default=0)


@pytest.fixture
async def engine():
    engine = create_async_engine(DSN)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def test_idempotent_transition_one_winner(engine) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            StatusRow.__table__.insert().values(id=1, status="pending", due_at=0)
        )

    async def run() -> bool:
        maker = async_sessionmaker(engine, expire_on_commit=False)
        async with maker() as session:
            stmt = idempotent_transition(
                StatusRow,
                row_id=1,
                status_attr=StatusRow.status,
                from_status="pending",
                to_status="done",
            )
            res = await session.execute(stmt)
            row = res.scalar_one_or_none()
            await session.commit()
            return row is not None

    results = await asyncio.gather(run(), run())
    assert sorted(results) == [False, True]


async def test_claim_due_no_overlap(engine) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            StatusRow.__table__.insert(),
            [{"id": i, "status": "due", "due_at": 0} for i in range(1, 5)],
        )

    async def claim(limit: int) -> list[int]:
        maker = async_sessionmaker(engine, expire_on_commit=False)
        async with maker() as session:
            stmt = claim_due(
                StatusRow,
                due_attr=StatusRow.due_at,
                now=1,
                limit=limit,
                set_values={"status": "claimed"},
            )
            res = await session.execute(stmt)
            ids = [row[0] for row in res.all()]
            await session.commit()
            return ids

    a, b = await asyncio.gather(claim(2), claim(2))
    assert len(set(a + b)) == len(a) + len(b)
