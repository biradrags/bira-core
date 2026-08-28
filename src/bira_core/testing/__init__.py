from typing import Any

__all__ = [
    "MockBotProvider",
    "MockMaxDpProvider",
    "MockMaxMessageManagerProvider",
    "MockMessageManagerProvider",
]


def __getattr__(name: str) -> Any:
    if name in {
        "MockBotProvider",
        "MockMaxDpProvider",
        "MockMaxMessageManagerProvider",
        "MockMessageManagerProvider",
    }:
        from bira_core.testing import providers as providers_mod

        return getattr(providers_mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
