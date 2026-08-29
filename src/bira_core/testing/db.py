"""Postgres test database helpers."""

from __future__ import annotations

import os
import time
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)


def xdist_locked_migrations(
    tmp_path_factory: pytest.TempPathFactory,
    request: pytest.FixtureRequest,
    run_migrations: Callable[[], None],
) -> None:
    """Xdist locked migrations."""
    if not hasattr(request.config, "workerinput"):
        run_migrations()
        return

    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    lock_file = root_tmp_dir / "bira_core_migrations.lock"
    done_file = root_tmp_dir / "bira_core_migrations.done"

    try:
        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        run_migrations()
        done_file.touch()
    except FileExistsError:
        for _ in range(600):
            if done_file.exists():
                return
            time.sleep(0.1)
        pytest.fail("Timed out waiting for migrations from another xdist worker")


@asynccontextmanager
async def rollback_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Rollback session."""
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autobegin=True,
    )
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@asynccontextmanager
async def savepoint_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Savepoint session."""
    async with engine.connect() as conn:
        trans = await conn.begin()
        async with AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        ) as session:
            try:
                yield session
            finally:
                await trans.rollback()


@asynccontextmanager
async def savepoint_session_from_connection(
    connection: AsyncConnection,
) -> AsyncIterator[AsyncSession]:
    """Savepoint session from connection."""
    async with AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    ) as session:
        yield session


def rollback_session_fixture(
    engine: AsyncEngine,
) -> Callable[[], AsyncIterator[AsyncSession]]:
    """Rollback session fixture."""

    @pytest.fixture
    async def _session() -> AsyncIterator[AsyncSession]:
        async with rollback_session(engine) as session:
            yield session

    return _session


def savepoint_session_fixture(
    engine: AsyncEngine,
) -> Callable[[], AsyncIterator[AsyncSession]]:
    """Savepoint session fixture."""

    @pytest.fixture
    async def _session() -> AsyncIterator[AsyncSession]:
        async with savepoint_session(engine) as session:
            yield session

    return _session
