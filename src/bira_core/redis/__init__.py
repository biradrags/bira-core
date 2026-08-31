"""redis helpers."""

from typing import Any

__all__ = ["make_redis_client", "redis_connection_kwargs"]


def __getattr__(name: str) -> Any:
    if name in {"make_redis_client", "redis_connection_kwargs"}:
        try:
            from bira_core.redis import client as client_mod
        except ImportError as e:
            e.add_note("pip install bira-core[redis]")
            raise
        return getattr(client_mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
