"""DSN builder for async Postgres."""

from typing import Protocol

from sqlalchemy import URL


class DbDsn(Protocol):
    """Db Dsn."""

    host: str
    port: int
    user: str
    password: str
    name: str


def build_url(dsn: DbDsn, *, driver: str = "postgresql+asyncpg") -> URL:
    """Build url."""
    return URL.create(
        driver,
        username=dsn.user,
        password=dsn.password,
        host=dsn.host,
        port=dsn.port,
        database=dsn.name,
    )
