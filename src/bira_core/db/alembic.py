"""Alembic env helpers for fleet migrations."""

from __future__ import annotations

import asyncio
import os
from typing import Any

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.sql.schema import MetaData

from bira_core.db.url import build_url


def resolve_ddl_url(
    *,
    role: str,
    password: str,
    host: str,
    port: int,
    name: str,
    env_override: str = "DATABASE_URL",
) -> str:
    """DATABASE_URL override or DDL-role DSN with password guard."""
    override = os.environ.get(env_override)
    if override:
        return override
    if not password:
        raise RuntimeError(
            "DB_DDL_PASSWORD не задан - миграциям нужна DDL-роль, отказ запускаться под DML"
        )
    url = build_url(
        _Dsn(role=role, password=password, host=host, port=port, name=name),
    )
    return url.render_as_string(hide_password=False)


class _Dsn:
    def __init__(
        self, *, role: str, password: str, host: str, port: int, name: str
    ) -> None:
        self.user = role
        self.password = password
        self.host = host
        self.port = port
        self.name = name


def _connect_args_for_host(host: str) -> dict[str, object]:
    _host = (host or "").lower()
    return {"ssl": False} if _host.endswith((".flycast", ".internal")) else {}


def run_migrations(config: Any, target_metadata: MetaData, *, host: str = "") -> None:
    """Run Alembic offline or online against target_metadata."""
    from alembic import context

    _connect_args = _connect_args_for_host(host)

    def run_migrations_offline() -> None:
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )
        with context.begin_transaction():
            context.run_migrations()

    def do_run_migrations(connection: Connection) -> None:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    async def run_async_migrations() -> None:
        connectable = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            connect_args=_connect_args,
        )
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    def run_migrations_online() -> None:
        asyncio.run(run_async_migrations())

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
