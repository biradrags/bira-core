"""Database layer facade - требует extra [db]."""

try:
    from bira_core.db.alembic import resolve_ddl_url, run_migrations
    from bira_core.db.base import NAMING_CONVENTION, Base
    from bira_core.db.dao import BaseDAO
    from bira_core.db.mixins import TimestampMixin
    from bira_core.db.settings import DbTenantSettings
    from bira_core.db.url import DbDsn, build_url
except ImportError as e:  # pragma: no cover - путь без extra [db]
    e.add_note("pip install bira-core[db]")
    raise

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
