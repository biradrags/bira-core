"""Fleet secret env variable names (values only in synthetic test fixtures)."""

SECRET_ENV_NAMES: list[str] = sorted(
    {
        "AMO_CHANNEL_ID",
        "AMO_CHANNEL_SECRET",
        "AMO_CLIENT_ID",
        "AMO_CLIENT_SECRET",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "BOT_TOKEN",
        "BUCKET_NAME",
        "CRON_SHARED_SECRET",
        "DATABASE_URL",
        "DB_DDL_PASSWORD",
        "DB_DML_PASSWORD",
        "GOOGLE_TABLE_CREDS",
        "GROQ_API_KEY",
        "MAX_BOT_TOKEN",
        "OPENAI_API_KEY",
        "POSTGRES_PASSWORD",
        "QDRANT_URL",
        "SESSION",
        "TBANK_PASSWORD",
        "TBANK_TERMINAL_KEY",
        "TG_BOT_TOKEN",
        "USERBOT_API_HASH",
        "USERBOT_API_ID",
        "WEBHOOK_SECRET",
        "XAI_API_KEY",
    }
)

# Synthetic value samples by secret shape (not real secrets).
SECRET_SHAPE_SAMPLES: dict[str, tuple[str, str]] = {
    "tg_token": (
        "BOT_TOKEN",
        "7213001234:AAFakeFakeFakeFakeFakeFakeFakeFak",
    ),
    "dsn": (
        "DATABASE_URL",
        "postgresql+asyncpg://bot:sup3rs3cret@db.example:5432/app_db",
    ),
    "bearer": (
        "CRON_SHARED_SECRET",
        "Authorization: Bearer cron-fake-shared-secret-token",
    ),
    "openai_key": (
        "OPENAI_API_KEY",
        "sk-fake-abcdef123456789012",
    ),
    "generic_api_key": (
        "XAI_API_KEY",
        "xai-fake-key-abcdef123456789012",
    ),
    "groq_key": (
        "GROQ_API_KEY",
        "gsk_fake123456789012345678901234567890",
    ),
    "webhook_secret": (
        "WEBHOOK_SECRET",
        "whsec_fake_webhook_secret_value_12345",
    ),
    "password": (
        "TBANK_PASSWORD",
        "tbank-fake-password-value-xyz",
    ),
    "terminal_key": (
        "TBANK_TERMINAL_KEY",
        "TBankFakeTerminalKey12345678",
    ),
    "amo_secret": (
        "AMO_CLIENT_SECRET",
        "amo-fake-client-secret-abcdef",
    ),
    "amo_channel_secret": (
        "AMO_CHANNEL_SECRET",
        "amo-fake-channel-secret-abcdef",
    ),
    "session_string": (
        "SESSION",
        "1BVtsOHwBu5FakeSessionStringForTestsOnlyABCDEFGHIJKLMNOP",
    ),
    "userbot_hash": (
        "USERBOT_API_HASH",
        "0123456789abcdef0123456789abcdef",
    ),
    "aws_secret": (
        "AWS_SECRET_ACCESS_KEY",
        "wJalrFakeSecretAccessKeyForTestsOnlyABCDEF",
    ),
    "json_creds": (
        "GOOGLE_TABLE_CREDS",
        '{"type":"service_account","private_key":"-----BEGIN PRIVATE KEY-----\\nFAKE\\n-----END PRIVATE KEY-----\\n","client_email":"fake@fake.iam.gserviceaccount.com"}',
    ),
    "db_password": (
        "DB_DML_PASSWORD",
        "dml-fake-db-password-value",
    ),
    "db_ddl_password": (
        "DB_DDL_PASSWORD",
        "ddl-fake-db-password-value",
    ),
    "qdrant_url": (
        "QDRANT_URL",
        "https://fake:qdrant-fake-api-key@qdrant.example:6333",
    ),
}
