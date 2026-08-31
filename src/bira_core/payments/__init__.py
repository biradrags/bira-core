"""Payment provider facade."""

try:
    from bira_core.payments.tbank import (
        TBankClient,
        TBankNetworkError,
        build_tbank_token,
        verify_tbank_token,
    )
except ImportError as e:  # pragma: no cover - путь без extra [payments]
    e.add_note("pip install bira-core[payments]")
    raise

__all__ = [
    "TBankClient",
    "TBankNetworkError",
    "build_tbank_token",
    "verify_tbank_token",
]
