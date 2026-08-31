"""DSN builder for async Postgres."""

from typing import Protocol

from sqlalchemy import URL


class DbDsn(Protocol):
    """Host/port/user/password/name fields for build_url."""

    host: str
    port: int
    user: str
    password: str
    name: str


def build_url(dsn: DbDsn, *, driver: str = "postgresql+asyncpg") -> URL:
    """Render asyncpg SQLAlchemy URL from a DbDsn protocol object."""
    return URL.create(
        driver,
        username=dsn.user,
        password=dsn.password,
        host=dsn.host,
        port=dsn.port,
        database=dsn.name,
    )
