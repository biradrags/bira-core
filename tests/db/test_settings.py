import pytest
from pydantic import SecretStr

from bira_core.db.settings import DbTenantSettings, ddl_dsn, ddl_url, dml_dsn
from bira_core.db.url import RoleDsn


def _cfg() -> DbTenantSettings:
    return DbTenantSettings(
        db_host="db.flycast",
        db_port=5432,
        db_name="app",
        db_dml_role="app_dml",
        db_ddl_role="app_ddl",
        db_dml_password=SecretStr("dml-p"),
        db_ddl_password=SecretStr("ddl-p"),
    )


def test_db_tenant_settings_fields() -> None:
    cfg = DbTenantSettings(
        db_host="localhost",
        db_port=5432,
        db_name="app",
        db_dml_role="app_dml",
        db_ddl_role="app_ddl",
        db_dml_password=SecretStr("dml"),
        db_ddl_password=SecretStr("ddl"),
    )
    assert cfg.db_host == "localhost"
    assert cfg.db_dml_password.get_secret_value() == "dml"


def test_dml_dsn() -> None:
    assert dml_dsn(_cfg()) == RoleDsn("db.flycast", 5432, "app_dml", "dml-p", "app")


def test_ddl_dsn() -> None:
    assert ddl_dsn(_cfg()) == RoleDsn("db.flycast", 5432, "app_ddl", "ddl-p", "app")


def test_ddl_url_builds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALEMBIC_DATABASE_URL", raising=False)
    assert ddl_url(_cfg()) == "postgresql+asyncpg://app_ddl:ddl-p@db.flycast:5432/app"


def test_ddl_url_custom_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MIGRATE_URL", "postgresql+asyncpg://o:o@o:1/o")
    assert (
        ddl_url(_cfg(), env_override="MIGRATE_URL") == "postgresql+asyncpg://o:o@o:1/o"
    )
