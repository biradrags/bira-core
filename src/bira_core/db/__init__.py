from typing import Any

__all__ = ["Base", "BaseDAO", "DbDsn", "build_url"]


def __getattr__(name: str) -> Any:
    if name in {"build_url", "DbDsn"}:
        try:
            from bira_core.db import url as url_mod
        except ImportError as e:
            e.add_note("pip install bira-core[db]")
            raise
        return getattr(url_mod, name)
    if name == "Base":
        try:
            from bira_core.db.base import Base

            return Base
        except ImportError as e:
            e.add_note("pip install bira-core[db]")
            raise
    if name == "BaseDAO":
        try:
            from bira_core.db.dao import BaseDAO

            return BaseDAO
        except ImportError as e:
            e.add_note("pip install bira-core[db]")
            raise
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
