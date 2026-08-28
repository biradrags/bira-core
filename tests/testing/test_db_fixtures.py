import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from bira_core.testing.db import rollback_session, savepoint_session

DSN = "postgresql+asyncpg://test:test@localhost:5499/test"


@pytest.fixture
async def engine():
    engine = create_async_engine(DSN)
    async with engine.begin() as conn:
        await conn.execute(
            text("CREATE TABLE IF NOT EXISTS fixture_probe (id INTEGER PRIMARY KEY)")
        )
        await conn.execute(text("DELETE FROM fixture_probe"))
    yield engine
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS fixture_probe"))
    await engine.dispose()


async def test_rollback_session_rolls_back(engine) -> None:
    async with rollback_session(engine) as session:
        await session.execute(text("INSERT INTO fixture_probe (id) VALUES (1)"))

    async with engine.connect() as conn:
        count = await conn.scalar(text("SELECT COUNT(*) FROM fixture_probe"))
    assert count == 0


async def test_savepoint_session_commit_not_leaks(engine) -> None:
    async with savepoint_session(engine) as session:
        await session.execute(text("INSERT INTO fixture_probe (id) VALUES (2)"))
        await session.commit()

    async with engine.connect() as conn:
        count = await conn.scalar(text("SELECT COUNT(*) FROM fixture_probe"))
    assert count == 0
