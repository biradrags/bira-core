import logging
from collections.abc import Sequence

from bira_core.log.redaction import RedactionFilter

__all__ = ["RedactionFilter", "setup_logging"]


def setup_logging(level: str, *, extra_patterns: Sequence[str] = ()) -> None:
    numeric = logging.getLevelNamesMapping().get(level.upper(), logging.INFO)
    handler = logging.StreamHandler()
    handler.addFilter(RedactionFilter(extra_patterns=extra_patterns))
    root = logging.getLogger()
    for existing in root.handlers[:]:
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(numeric)
