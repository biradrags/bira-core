from typing import Any

__all__ = ["DbDsn", "build_url"]


def __getattr__(name: str) -> Any:
    if name in {"build_url", "DbDsn"}:
        try:
            from bira_core.db import url as url_mod
        except ImportError as e:
            e.add_note("pip install bira-core[db]")
            raise
        return getattr(url_mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
