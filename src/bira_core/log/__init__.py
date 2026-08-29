from __future__ import annotations

import logging
import os
from collections.abc import Sequence

from bira_core.log.logfmt import LogfmtFormatter, ProbeAccessFilter
from bira_core.log.redaction import RedactionFilter

__all__ = [
    "LogfmtFormatter",
    "ProbeAccessFilter",
    "RedactionFilter",
    "setup_logging",
]


def setup_logging(
    level: int | str | None = None,
    *,
    extra_patterns: Sequence[str] = (),
    extra_silence: Sequence[str] = (),
) -> None:
    """Configure root logger; env LOG_LEVEL applies only when level is None."""
    if level is None:
        env = os.environ.get("LOG_LEVEL", "INFO")
        numeric = logging.getLevelNamesMapping().get(env.upper(), logging.INFO)
    elif isinstance(level, str):
        numeric = logging.getLevelNamesMapping().get(level.upper(), logging.INFO)
    else:
        numeric = level

    handler = logging.StreamHandler()
    handler.setFormatter(LogfmtFormatter())
    handler.addFilter(RedactionFilter(extra_patterns=extra_patterns))
    root = logging.getLogger()
    for existing in root.handlers[:]:
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(numeric)
    logging.getLogger("aiohttp.access").addFilter(ProbeAccessFilter())
    for noisy in ("aiogram.event", "sqlalchemy.engine", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    for name in extra_silence:
        logging.getLogger(name).setLevel(logging.WARNING)
