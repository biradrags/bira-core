import asyncio
import textwrap
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from bira_core.db.alembic import (
    _connect_args_for_host,
    _use_sync_engine,
    resolve_ddl_url,
)

DSN_ASYNC = "postgresql+asyncpg://test:test@localhost:5499/test"


def test_env_override_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://x:y@h:5/z")
    url = resolve_ddl_url(role="r", password="p", host="db", port=5432, name="app")
    assert url == "postgresql+asyncpg://x:y@h:5/z"


def test_empty_ddl_password_hard_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError):
        resolve_ddl_url(role="r", password="", host="db", port=5432, name="app")


def test_builds_ddl_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    url = resolve_ddl_url(
        role="app_ddl", password="p", host="db.flycast", port=5432, name="app"
    )
    assert "app_ddl" in url and "db.flycast" in url


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("db.flycast", {"ssl": False}),
        ("app.internal", {"ssl": False}),
        ("DB.FLYCAST", {"ssl": False}),  # регистр хоста не важен
        ("localhost", {}),
        ("db.example.com", {}),
        ("", {}),
    ],
)
def test_connect_args_for_host(host: str, expected: dict[str, object]) -> None:
    assert _connect_args_for_host(host) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("postgresql+asyncpg://u:p@h/db", False),
        ("postgresql+psycopg://u:p@h/db", True),
        (None, False),
        ("", False),
    ],
)
def test_use_sync_engine(url: str | None, expected: bool) -> None:
    assert _use_sync_engine(url) is expected


def _write_migration_project(tmp_path: Path, table_name: str, url: str) -> Config:
    """Минимальный одноревизионный alembic-проект: env.py зовёт run_migrations."""
    (tmp_path / "versions").mkdir()
    (tmp_path / "env.py").write_text(
        textwrap.dedent(
            """
            from alembic import context
            from sqlalchemy import MetaData

            from bira_core.db.alembic import run_migrations

            run_migrations(context.config, MetaData(), host="")
            """
        )
    )
    (tmp_path / "versions" / "0001_probe.py").write_text(
        textwrap.dedent(
            f"""
            revision = "0001"
            down_revision = None

            from alembic import op
            from sqlalchemy import Column, Integer

            def upgrade():
                op.create_table("{table_name}", Column("id", Integer, primary_key=True))

            def downgrade():
                op.drop_table("{table_name}")
            """
        )
    )
    ini = tmp_path / "alembic.ini"
    ini.write_text("[alembic]\n")
    config = Config(str(ini))
    config.set_main_option("script_location", str(tmp_path))
    config.set_main_option("sqlalchemy.url", url)
    return config


async def _table_exists(table_name: str) -> bool:
    engine = create_async_engine(DSN_ASYNC)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("select to_regclass(:name)"), {"name": table_name}
            )
            return result.scalar() is not None
    finally:
        await engine.dispose()


@pytest.mark.xdist_group(name="postgres")
@pytest.mark.parametrize(
    ("url", "table_name"),
    [
        (DSN_ASYNC, "run_migrations_probe_asyncpg"),
        (
            "postgresql+psycopg://test:test@localhost:5499/test",
            "run_migrations_probe_psycopg",
        ),
    ],
    ids=["asyncpg-async-branch", "psycopg-sync-branch"],
)
def test_run_migrations_applies_head_for_both_drivers(
    tmp_path: Path, url: str, table_name: str
) -> None:
    """Реальный прогон Alembic: и async-, и sync-ветка обязаны довести миграцию до конца.

    Воспроизводит фикстуры ботов, которые подменяют +asyncpg на +psycopg перед
    вызовом `alembic upgrade head` в подпроцессе (см. CHANGELOG про sync-ветку).
    Синхронная функция-тест - `run_migrations` сам зовёт `asyncio.run()` в async-ветке
    и падает на вложенном loop, будь тест `async def` под pytest-asyncio.
    """
    config = _write_migration_project(tmp_path, table_name, url)
    try:
        command.upgrade(config, "head")
        assert asyncio.run(_table_exists(table_name)) is True
    finally:
        command.downgrade(config, "base")
        assert asyncio.run(_table_exists(table_name)) is False
