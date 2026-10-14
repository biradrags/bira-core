import logging

import pytest

from bira_core.log.redaction import RedactionFilter, redact_extra
from tests.fixtures_secret_names import SECRET_ENV_NAMES, SECRET_SHAPE_SAMPLES

CASES = [
    ("token=7213001234:AAFakeFakeFakeFakeFakeFakeFakeFak", "7213001234:AAFake"),
    ("postgres://bot:sup3rs3cret@db.internal:5432/app", "sup3rs3cret"),
    ("Authorization: Bearer sk-fake-abcdef123456", "sk-fake-abcdef123456"),
    # Яндекс.Диск: токен течёт и в заголовке, и голым в тексте ошибки yadisk
    ("Authorization: OAuth y0_FakeFakeFakeFakeFake12345", "y0_FakeFakeFake"),
    ("yadisk request failed: y0_FakeFakeFakeFakeFake12345", "y0_FakeFakeFake"),
    # Провайдеры с узнаваемым префиксом - та же форма «токен без имени ключа»
    ("xai call failed: xai-fake-key-abcdef123456789012", "fake-key-abcdef"),
    ("groq call failed: gsk_fake123456789012345678901234567890", "gsk_fake1234567"),
    ("s3 denied for AKIAIOSFODNN7EXAMPLE", "AKIAIOSFODNN7EX"),
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


@pytest.mark.parametrize(
    "key", ["phone", "username", "transcript", "description", "contact_phone"]
)
def test_pii_keys_are_masked(key: str) -> None:
    out = redact_extra({key: "+79991234567"})
    assert out[key] != "+79991234567"


def test_pii_text_value_is_masked() -> None:
    out = redact_extra({"transcript": "позвоните мне вечером"})
    assert out["transcript"] != "позвоните мне вечером"
