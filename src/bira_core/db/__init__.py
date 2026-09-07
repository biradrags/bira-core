"""Database layer facade."""

from typing import Any

__all__ = [
    "NAMING_CONVENTION",
    "Base",
    "BaseDAO",
    "DbDsn",
    "DbTenantSettings",
    "TimestampMixin",
    "build_url",
    "resolve_ddl_url",
    "run_migrations",
]


def __getattr__(name: str) -> Any:
    if name in {"resolve_ddl_url", "run_migrations"}:
        try:
            from bira_core.db import alembic as alembic_mod
        except ImportError as e:
            e.add_note("pip install bira-core[alembic]")
            raise
        return getattr(alembic_mod, name)
    if name in {"build_url", "DbDsn"}:
        try:
            from bira_core.db import url as url_mod
        except ImportError as e:
            e.add_note("pip install bira-core[db]")
            raise
        return getattr(url_mod, name)
    if name in {"Base", "NAMING_CONVENTION"}:
        try:
            from bira_core.db import base as base_mod
        except ImportError as e:
            e.add_note("pip install bira-core[db]")
            raise
        return getattr(base_mod, name)
    if name == "BaseDAO":
        try:
            from bira_core.db.dao import BaseDAO

            return BaseDAO
        except ImportError as e:
            e.add_note("pip install bira-core[db]")
            raise
    if name == "DbTenantSettings":
        try:
            from bira_core.db.settings import DbTenantSettings

            return DbTenantSettings
        except ImportError as e:
            e.add_note("pip install bira-core[db]")
            raise
    if name == "TimestampMixin":
        try:
            from bira_core.db.mixins import TimestampMixin

            return TimestampMixin
        except ImportError as e:
            e.add_note("pip install bira-core[db]")
            raise
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
