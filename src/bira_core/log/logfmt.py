from __future__ import annotations

import logging

from bira_core.log.redaction import RECORD_ATTRS

_RESERVED_KEYS = frozenset({"level", "logger", "msg", "exc", "stack"})
_MAX_VAL = 120


def _safe_key(key: str) -> str:
    return f"{key}_" if key in _RESERVED_KEYS else key


def _fmt_val(value: object, limit: int | None = _MAX_VAL) -> str:
    text = str(value)
    if limit is not None and len(text) > limit:
        text = text[:limit] + "…"
    if text == "" or any(ch in text for ch in ' ="\n\t'):
        escaped = (
            text.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )
        return f'"{escaped}"'
    return text


class LogfmtFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        parts = [
            f"level={record.levelname}",
            f"logger={record.name}",
            f"msg={_fmt_val(record.getMessage(), limit=None)}",
        ]
        parts += [
            f"{_safe_key(key)}={_fmt_val(value)}"
            for key, value in record.__dict__.items()
            if key not in RECORD_ATTRS and not key.startswith("_")
        ]
        if record.exc_info:
            parts.append(
                f"exc={_fmt_val(self.formatException(record.exc_info), limit=None)}"
            )
        if record.stack_info:
            parts.append(
                f"stack={_fmt_val(self.formatStack(record.stack_info), limit=None)}"
            )
        return " ".join(parts)


class ProbeAccessFilter(logging.Filter):
    _SKIP = ("/health", "/webhook")

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not any(path in msg for path in self._SKIP)
