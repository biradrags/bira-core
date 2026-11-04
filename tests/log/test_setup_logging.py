import logging
from collections.abc import Iterator

import pytest

from bira_core.log.redaction import RedactionFilter
from bira_core.log.setup import setup_logging

_LOGGERS = ("aiogram.event", "sqlalchemy.engine", "httpx")


@pytest.fixture(autouse=True)
def _restore_logging() -> Iterator[None]:
    root = logging.getLogger()
    level = root.level
    handlers = root.handlers[:]
    levels = {name: logging.getLogger(name).level for name in _LOGGERS}
    yield
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    for handler in handlers:
        root.addHandler(handler)
    root.setLevel(level)
    for name, saved in levels.items():
        logging.getLogger(name).setLevel(saved)


def test_explicit_level_wins_over_env(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    setup_logging("WARNING")
    assert logging.getLogger().level == logging.WARNING


def test_env_level_when_none(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    setup_logging(None)
    assert logging.getLogger().level == logging.ERROR


def test_custom_redaction_filter() -> None:
    custom = logging.Filter()
    setup_logging("INFO", redaction_filter=custom)
    filters = logging.getLogger().handlers[0].filters
    assert custom in filters
    assert not any(isinstance(f, RedactionFilter) for f in filters)


def test_silence_override_keeps_aiogram_event() -> None:
    logging.getLogger("aiogram.event").setLevel(logging.NOTSET)
    setup_logging("INFO", silence=("sqlalchemy.engine", "httpx"))
    assert logging.getLogger("aiogram.event").level == logging.NOTSET
    assert logging.getLogger("httpx").level == logging.WARNING


def test_default_silence() -> None:
    setup_logging("INFO")
    for name in _LOGGERS:
        assert logging.getLogger(name).level == logging.WARNING
