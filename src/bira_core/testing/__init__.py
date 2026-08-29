from typing import Any

__all__ = [
    "MockBotProvider",
    "MockMaxDpProvider",
    "MockMaxMessageManagerProvider",
    "MockMessageManagerProvider",
    "rollback_session",
    "rollback_session_fixture",
    "savepoint_session",
    "savepoint_session_fixture",
    "savepoint_session_from_connection",
    "xdist_locked_migrations",
]

_DB_EXPORTS = frozenset(
    {
        "rollback_session",
        "rollback_session_fixture",
        "savepoint_session",
        "savepoint_session_fixture",
        "savepoint_session_from_connection",
        "xdist_locked_migrations",
    }
)


def __getattr__(name: str) -> Any:
    if name in {
        "MockBotProvider",
        "MockMaxDpProvider",
        "MockMaxMessageManagerProvider",
        "MockMessageManagerProvider",
    }:
        from bira_core.testing import providers as providers_mod

        return getattr(providers_mod, name)
    if name in _DB_EXPORTS:
        from bira_core.testing import db as db_mod

        return getattr(db_mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
