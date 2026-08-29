import logging

from bira_core.log import setup_logging


def test_explicit_level_wins_over_env(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    setup_logging("WARNING")
    assert logging.getLogger().level == logging.WARNING


def test_env_level_when_none(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    setup_logging(None)
    assert logging.getLogger().level == logging.ERROR
