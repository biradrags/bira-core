"""DSN builder for async Postgres."""

from dataclasses import dataclass, field
from typing import Protocol

from sqlalchemy import URL


class DbDsn(Protocol):
    """Host/port/user/password/name fields for build_url."""

    host: str
    port: int
    user: str
    password: str
    name: str


@dataclass
class RoleDsn:
    """DbDsn под одну роль; пароль уже раскрыт - объект не логировать."""

    host: str
    port: int
    user: str
    password: str = field(repr=False)
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
