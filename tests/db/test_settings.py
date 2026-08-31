from pydantic import SecretStr

from bira_core.db.settings import DbTenantSettings


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
