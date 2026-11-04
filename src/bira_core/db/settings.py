"""Database connection settings DTO and DSN adapters."""

from typing import Protocol

from pydantic import BaseModel, SecretStr

from bira_core.db.alembic import resolve_ddl_url
from bira_core.db.url import RoleDsn


class DbTenantFields(Protocol):
    """Поля координат и ролей Postgres-тенанта; совпадают с полями DbTenantSettings."""

    db_host: str
    db_port: int
    db_name: str
    db_dml_role: str
    db_ddl_role: str
    db_dml_password: SecretStr
    db_ddl_password: SecretStr


class DbTenantSettings(BaseModel):
    """Per-tenant Postgres roles and secrets for DML/DDL."""

    db_host: str
    db_port: int
    db_name: str
    db_dml_role: str
    db_ddl_role: str
    db_dml_password: SecretStr
    db_ddl_password: SecretStr


def dml_dsn(cfg: DbTenantFields) -> RoleDsn:
    """DSN рантайма под DML-ролью."""
    return RoleDsn(
        cfg.db_host,
        cfg.db_port,
        cfg.db_dml_role,
        cfg.db_dml_password.get_secret_value(),
        cfg.db_name,
    )


def ddl_dsn(cfg: DbTenantFields) -> RoleDsn:
    """DSN миграций под DDL-ролью."""
    return RoleDsn(
        cfg.db_host,
        cfg.db_port,
        cfg.db_ddl_role,
        cfg.db_ddl_password.get_secret_value(),
        cfg.db_name,
    )


def ddl_url(cfg: DbTenantFields, *, env_override: str = "ALEMBIC_DATABASE_URL") -> str:
    """resolve_ddl_url поверх полей конфига - одна строка в alembic/env.py бота."""
    return resolve_ddl_url(
        role=cfg.db_ddl_role,
        password=cfg.db_ddl_password.get_secret_value(),
        host=cfg.db_host,
        port=cfg.db_port,
        name=cfg.db_name,
        env_override=env_override,
    )
