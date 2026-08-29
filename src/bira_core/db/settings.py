"""Database connection settings DTO."""

from pydantic import BaseModel, SecretStr


class DbTenantSettings(BaseModel):
    """Per-tenant Postgres roles and secrets for DML/DDL."""

    db_host: str
    db_port: int
    db_name: str
    db_dml_role: str
    db_ddl_role: str
    db_dml_password: SecretStr
    db_ddl_password: SecretStr
