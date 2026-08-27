from typing import Protocol

from sqlalchemy import URL


class DbDsn(Protocol):
    host: str
    port: int
    user: str
    password: str
    name: str


def build_url(dsn: DbDsn, *, driver: str = "postgresql+asyncpg") -> URL:
    return URL.create(
        driver,
        username=dsn.user,
        password=dsn.password,
        host=dsn.host,
        port=dsn.port,
        database=dsn.name,
    )
