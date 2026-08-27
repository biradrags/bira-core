import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bira_core.db import Base

DSN = "postgresql+asyncpg://test:test@localhost:5499/test"


@pytest.fixture
async def session():
    engine = create_async_engine(DSN)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
