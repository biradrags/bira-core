import pytest

from bira_core.db.alembic import resolve_ddl_url


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
