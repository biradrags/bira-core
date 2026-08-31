import logging

from bira_core.log import setup_logging
from bira_core.log.logfmt import LogfmtFormatter, ProbeAccessFilter


def test_logfmt_formatter_order() -> None:
    record = logging.LogRecord("app.svc", logging.INFO, __file__, 1, "hello", (), None)
    line = LogfmtFormatter().format(record)
    assert line.startswith("level=INFO logger=app.svc msg=hello")


def test_probe_access_filter_blocks_health() -> None:
    filt = ProbeAccessFilter()
    rec = logging.LogRecord(
        "aiohttp.access", logging.INFO, "", 0, "GET /health", (), None
    )
    assert filt.filter(rec) is False


def test_extra_silence_mutes_logger() -> None:
    setup_logging("INFO", extra_silence=["pyrogram"])
    assert logging.getLogger("pyrogram").level == logging.WARNING
