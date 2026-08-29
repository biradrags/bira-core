import logging
import re
from collections.abc import Sequence
from typing import Any

SENSITIVE_KEY_NAMES = frozenset(
    {
        "token",
        "secret",
        "password",
        "passwd",
        "pwd",
        "dsn",
        "auth",
        "authorization",
        "credentials",
        "api_key",
        "apikey",
        "secret_key",
        "private_key",
        "access_key",
        "session",
        "session_string",
    }
)
SENSITIVE_KEY_SUFFIXES = (
    "_token",
    "_secret",
    "_password",
    "_api_key",
    "_apikey",
    "_dsn",
    "_credentials",
    "_access_key",
    "_hash",
    "_creds",
    "_terminal_key",
)
SENSITIVE_KEY_PATTERNS = ("token", "secret", "password", "api_key", "dsn", "auth")
PREFIX_LEN = 4
SUFFIX_LEN = 4
MASK = "***"

OPENAI_KEY_RE = re.compile(r"sk-[a-zA-Z0-9]{20,}")
BEARER_RE = re.compile(r"Bearer\s+\S+", re.IGNORECASE)
TG_TOKEN_RE = re.compile(r"\d{6,12}:[A-Za-z0-9_-]{30,}")
DSN_RE = re.compile(
    r"(?:postgresql|postgres|mysql|rediss|redis|mongodb)(?:\+[a-z0-9]+)?://[^\s,)\]]*",
    re.IGNORECASE,
)
URL_AUTH_RE = re.compile(r"https?://[^\s:@/]+:[^\s/@]+@[^\s,)\]]+", re.IGNORECASE)


def _mask_value(value: str) -> str:
    if len(value) <= PREFIX_LEN + SUFFIX_LEN:
        return MASK
    return value[:PREFIX_LEN] + MASK + value[-SUFFIX_LEN:]


def redact_string(s: str) -> str:
    s = TG_TOKEN_RE.sub(lambda m: _mask_value(m.group(0)), s)
    s = OPENAI_KEY_RE.sub(lambda m: _mask_value(m.group(0)), s)
    s = BEARER_RE.sub(
        lambda m: (
            m.group(0).split(maxsplit=1)[0]
            + " "
            + _mask_value(m.group(0).split(maxsplit=1)[1])
        ),
        s,
    )
    s = URL_AUTH_RE.sub(lambda m: _mask_value(m.group(0)), s)
    return DSN_RE.sub(lambda m: _mask_value(m.group(0)), s)


def _is_sensitive_key(key: str) -> bool:
    k = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()
    return k in SENSITIVE_KEY_NAMES or k.endswith(SENSITIVE_KEY_SUFFIXES)


def _is_countable(value: str) -> bool:
    return value.isdigit() or (value.replace(".", "", 1).isdigit() and "." in value)


def _keep_as_is(match: re.Match[str]) -> bool:
    return _is_countable(match.group(2)) or not _is_sensitive_key(
        match.group(1).split("=")[0].strip()
    )


def _sub_bare(match: re.Match[str]) -> str:
    if _keep_as_is(match):
        return match.group(0)
    return match.group(1) + _mask_value(match.group(2))


def _sub_quoted(match: re.Match[str]) -> str:
    if _keep_as_is(match):
        return match.group(0)
    return match.group(1) + "'" + _mask_value(match.group(2)) + "'"


def _build_kv_patterns(
    parts: Sequence[str],
) -> tuple[tuple[re.Pattern[str], re.Pattern[str]], ...]:
    return tuple(
        (
            re.compile(
                r"(\b\w*" + re.escape(part) + r"\w*\s*=\s*)([^\s,)\]}\']+)",
                re.IGNORECASE,
            ),
            re.compile(
                r"(\b\w*" + re.escape(part) + r"\w*\s*=\s*)[\'\"]([^\'\"]+)[\'\"]",
                re.IGNORECASE,
            ),
        )
        for part in parts
    )


_KV_PATTERNS = _build_kv_patterns(SENSITIVE_KEY_PATTERNS)


def _mask_sensitive_kv_in_text(text: str) -> str:
    def repl_bare(match: re.Match[str]) -> str:
        key = match.group(1).split("=")[0].strip()
        if not _is_sensitive_key(key):
            return match.group(0)
        return match.group(1) + _mask_value(match.group(2))

    def repl_quoted(match: re.Match[str]) -> str:
        key = match.group(1).split("=")[0].strip()
        if not _is_sensitive_key(key):
            return match.group(0)
        return (
            match.group(1)
            + match.group(2)
            + _mask_value(match.group(3))
            + match.group(2)
        )

    text = re.sub(
        r"(\b[A-Za-z_][A-Za-z0-9_]*\s*=\s*)([^\s,)\]}\']+)",
        repl_bare,
        text,
    )
    text = re.sub(
        r"(\b[A-Za-z_][A-Za-z0-9_]*\s*=\s*)(['\"])(.*?)\2",
        repl_quoted,
        text,
    )

    def repl_json(match: re.Match[str]) -> str:
        key = match.group(1).split("=")[0].strip()
        if not _is_sensitive_key(key):
            return match.group(0)
        return match.group(1) + _mask_value(match.group(2))

    return re.sub(
        r"(\b[A-Za-z_][A-Za-z0-9_]*\s*=\s*)(\{.*\})",
        repl_json,
        text,
    )


def redact_log_message(text: str, *, extra_patterns: Sequence[str] = ()) -> str:
    text = redact_string(text)
    text = _mask_sensitive_kv_in_text(text)
    patterns = _KV_PATTERNS
    if extra_patterns:
        patterns = patterns + _build_kv_patterns(extra_patterns)
    for bare, quoted in patterns:
        text = bare.sub(_sub_bare, text)
        text = quoted.sub(_sub_quoted, text)
    return text


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        result: dict[str, Any] = {}
        for k, v in obj.items():
            if _is_sensitive_key(k):
                result[k] = _mask_value(str(v))
            else:
                result[k] = redact(v)
        return result
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    if isinstance(obj, str):
        return redact_string(obj)
    return obj


RECORD_ATTRS = frozenset(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {
    "message",
    "asctime",
    "taskName",
}


def redact_extra(fields: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in fields.items():
        if isinstance(value, dict | list):
            result[key] = redact(value)
        elif _is_sensitive_key(key):
            result[key] = _mask_value(str(value))
        elif not isinstance(value, str) or _is_countable(value):
            result[key] = value
        else:
            result[key] = redact_string(value)
    return result


class RedactionFilter(logging.Filter):
    def __init__(self, *, extra_patterns: Sequence[str] = ()) -> None:
        super().__init__()
        self._extra_patterns = extra_patterns

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            record.msg = redact_log_message(msg, extra_patterns=self._extra_patterns)
            record.args = ()
            extra = {
                k: v
                for k, v in record.__dict__.items()
                if k not in RECORD_ATTRS and not k.startswith("_")
            }
            if extra:
                record.__dict__.update(redact_extra(extra))
            if record.exc_info:
                record.exc_text = redact_log_message(
                    logging.Formatter().formatException(record.exc_info),
                    extra_patterns=self._extra_patterns,
                )
            if record.stack_info:
                record.stack_info = redact_log_message(
                    record.stack_info,
                    extra_patterns=self._extra_patterns,
                )
        except (TypeError, ValueError, AttributeError) as e:
            logger = logging.getLogger(__name__)
            logger.debug("redaction filter skipped record", extra={"err": str(e)})
        return True
