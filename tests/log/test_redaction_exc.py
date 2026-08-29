import logging
from collections.abc import Iterator

import pytest

from bira_core.log import LogfmtFormatter, RedactionFilter, setup_logging
from bira_core.log.redaction import redact_extra


@pytest.fixture
def caplog_logfmt(caplog: pytest.LogCaptureFixture) -> Iterator[pytest.LogCaptureFixture]:
    setup_logging("INFO")
    logger = logging.getLogger("test.redaction.exc")
    logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(LogfmtFormatter())
    handler.addFilter(RedactionFilter())
    logger.addHandler(handler)
    logger.propagate = False
    with caplog.at_level(logging.INFO, logger="test.redaction.exc"):
        yield caplog


def test_exception_message_is_redacted(caplog_logfmt: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("test.redaction.exc")
    filt = RedactionFilter()
    fmt = LogfmtFormatter()
    try:
        raise ConnectionError("postgresql://bot:sup3rs3cret@db/x")
    except ConnectionError:
        logger.exception("db down")
    record = caplog_logfmt.records[-1]
    filt.filter(record)
    line = fmt.format(record)
    assert "sup3rs3cret" not in line and "exc=" in line


def test_nested_extra_leaf_scanned() -> None:
    out = redact_extra({"payload": {"note": "Bearer sk-fake-abc123def456ghi"}})
    assert "sk-fake" not in str(out)


def test_camel_case_key_masked() -> None:
    out = redact_extra({"authToken": "supersecretvalue123"})
    assert out["authToken"] != "supersecretvalue123"
