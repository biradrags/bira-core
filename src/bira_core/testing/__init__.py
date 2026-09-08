"""Test fixtures facade."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bira_core.testing.db import (
        rollback_session,
        rollback_session_fixture,
        savepoint_session,
        savepoint_session_fixture,
        savepoint_session_from_connection,
        xdist_locked_migrations,
    )
    from bira_core.testing.providers_max import (
        MockMaxDpProvider,
        MockMaxMessageManagerProvider,
    )
    from bira_core.testing.providers_tg import (
        MockBotProvider,
        MockMessageManagerProvider,
    )

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

_LAZY_EXPORTS = {
    "MockBotProvider": ("bira_core.testing.providers_tg", "testing,tgbot"),
    "MockMessageManagerProvider": ("bira_core.testing.providers_tg", "testing,dialogs"),
    "MockMaxDpProvider": ("bira_core.testing.providers_max", "testing,max"),
    "MockMaxMessageManagerProvider": ("bira_core.testing.providers_max", "testing,max"),
    "rollback_session": ("bira_core.testing.db", "testing,db"),
    "rollback_session_fixture": ("bira_core.testing.db", "testing,db"),
    "savepoint_session": ("bira_core.testing.db", "testing,db"),
    "savepoint_session_fixture": ("bira_core.testing.db", "testing,db"),
    "savepoint_session_from_connection": ("bira_core.testing.db", "testing,db"),
    "xdist_locked_migrations": ("bira_core.testing.db", "testing,db"),
}


def __getattr__(name: str) -> Any:
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path, extras = target
    try:
        module = import_module(module_path)
    except ImportError as e:
        e.add_note(f"pip install bira-core[{extras}]")
        raise
    return getattr(module, name)
