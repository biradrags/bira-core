from dataclasses import dataclass

from bira_core.db.url import build_url


@dataclass
class _Dsn:
    host: str = "localhost"
    port: int = 5435
    user: str = "bot"
    password: str = "p@ss:w"
    name: str = "app_db"


def test_build_url_quotes_password() -> None:
    url = build_url(_Dsn())
    assert url.drivername == "postgresql+asyncpg"
    rendered = url.render_as_string(hide_password=False)
    assert rendered == "postgresql+asyncpg://bot:p%40ss%3Aw@localhost:5435/app_db"


def test_build_url_custom_driver() -> None:
    assert (
        build_url(_Dsn(), driver="postgresql+psycopg").drivername
        == "postgresql+psycopg"
    )
