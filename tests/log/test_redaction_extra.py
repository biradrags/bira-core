import pytest

from bira_core.log.redaction import redact_extra, redact_string

# Голая форма, без префикса переменной: именно её regex и обязан ловить сам,
# без помощи маскирования по имени ключа.
OPENAI_KEYS = [
    "sk-proj-abcdefghij0123456789KLMNOPQRSTUV",
    "sk-svcacct-abcdefghij0123456789KLMNOP",
    "sk-abcdefghij0123456789KLMNOP",
]


@pytest.mark.parametrize("key", OPENAI_KEYS)
def test_openai_key_masked_in_bare_text(key: str) -> None:
    redacted = redact_string(f"auth failed for {key} on retry")

    assert key not in redacted
    assert "***" in redacted


def test_query_token_masked_inside_extra_value() -> None:
    """Канон велит логировать через extra=, значит защита обязана быть и там."""
    fields = redact_extra(
        {"url": "https://api.example.com/hook?token=abcdef1234secret"}  # gitleaks:allow
    )

    assert "abcdef1234secret" not in fields["url"]


def test_query_token_masked_inside_nested_extra() -> None:
    fields = redact_extra({"reqs": ["GET https://x.com/a?api_key=verysecret1234 200"]})

    assert "verysecret1234" not in fields["reqs"][0]


def test_dsn_password_masked_in_extra() -> None:
    fields = redact_extra({"url": "postgresql://user:hunter2@db.internal:5432/app"})

    assert "hunter2" not in fields["url"]


def test_plain_values_and_counters_survive() -> None:
    fields = redact_extra({"msg": "lead created", "ms": "42", "count": 7})

    assert fields == {"msg": "lead created", "ms": "42", "count": 7}
