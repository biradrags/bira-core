"""Dishka provider facade."""

from typing import Any

__all__ = ["DbProvider", "NotifierProvider", "RedisProvider", "warm_up"]

_EXPORTS: dict[str, str] = {
    "DbProvider": "bira_core.di.db",
    "RedisProvider": "bira_core.di.redis",
    "NotifierProvider": "bira_core.di.notify",
    "warm_up": "bira_core.di.warmup",
}


def __getattr__(name: str) -> Any:
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        from importlib import import_module

        module = import_module(module_path)
    except ImportError as e:
        if name == "DbProvider":
            e.add_note("pip install bira-core[db,di]")
        elif name == "RedisProvider":
            e.add_note("pip install bira-core[redis,di]")
        elif name in {"NotifierProvider", "warm_up"}:
            e.add_note("pip install bira-core[di,tgbot]")
        else:
            e.add_note("pip install bira-core[di]")
        raise
    return getattr(module, name)
