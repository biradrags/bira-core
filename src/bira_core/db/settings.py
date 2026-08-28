from pydantic import BaseModel, SecretStr


class DbTenantSettings(BaseModel):
    db_host: str
    db_port: int
    db_name: str
    db_dml_role: str
    db_ddl_role: str
    db_dml_password: SecretStr
    db_ddl_password: SecretStr
