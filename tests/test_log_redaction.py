import logging

from bira_core.log import RedactionFilter

CASES = [
    ("token=7213001234:AAFakeFakeFakeFakeFakeFakeFakeFak", "7213001234:AAFake"),
    ("postgres://bot:sup3rs3cret@db.internal:5432/app", "sup3rs3cret"),
    ("Authorization: Bearer sk-fake-abcdef123456", "sk-fake-abcdef123456"),
]


def _record(msg: str) -> logging.LogRecord:
    return logging.LogRecord("t", logging.INFO, __file__, 1, msg, (), None)


def test_masks_known_secret_shapes() -> None:
    f = RedactionFilter()
    for raw, secret in CASES:
        rec = _record(raw)
        assert f.filter(rec) is True
        assert secret not in rec.getMessage()
