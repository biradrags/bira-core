import logging

import pytest

from bira_core.log import RedactionFilter
from tests.fixtures_secret_names import SECRET_ENV_NAMES, SECRET_SHAPE_SAMPLES

CASES = [
    ("token=7213001234:AAFakeFakeFakeFakeFakeFakeFakeFak", "7213001234:AAFake"),
    ("postgres://bot:sup3rs3cret@db.internal:5432/app", "sup3rs3cret"),
    ("Authorization: Bearer sk-fake-abcdef123456", "sk-fake-abcdef123456"),
]

REQUIRED_ENV_NAMES = {
    "BOT_TOKEN",
    "MAX_BOT_TOKEN",
    "OPENAI_API_KEY",
    "XAI_API_KEY",
    "GROQ_API_KEY",
    "TBANK_TERMINAL_KEY",
    "TBANK_PASSWORD",
    "WEBHOOK_SECRET",
    "USERBOT_API_ID",
    "USERBOT_API_HASH",
    "SESSION",
    "GOOGLE_TABLE_CREDS",
    "AMO_CLIENT_SECRET",
    "AMO_CHANNEL_SECRET",
    "DB_DML_PASSWORD",
    "DB_DDL_PASSWORD",
    "AWS_SECRET_ACCESS_KEY",
    "QDRANT_URL",
}


def _record(msg: str) -> logging.LogRecord:
    return logging.LogRecord("t", logging.INFO, __file__, 1, msg, (), None)


def test_masks_known_secret_shapes() -> None:
    f = RedactionFilter()
    for raw, secret in CASES:
        rec = _record(raw)
        assert f.filter(rec) is True
        assert secret not in rec.getMessage()


def test_secret_env_names_cover_fleet_minimum() -> None:
    assert REQUIRED_ENV_NAMES <= set(SECRET_ENV_NAMES)


@pytest.mark.parametrize("shape", list(SECRET_SHAPE_SAMPLES))
def test_masks_fleet_secret_shape(shape: str) -> None:
    env_name, secret_value = SECRET_SHAPE_SAMPLES[shape]
    f = RedactionFilter()
    if shape == "bearer":
        raw = secret_value
    else:
        raw = f"{env_name}={secret_value}"
    rec = _record(raw)
    assert f.filter(rec) is True
    assert secret_value not in rec.getMessage()
