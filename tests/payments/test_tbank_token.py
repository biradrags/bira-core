import inspect

from bira_core.payments import tbank


def test_verify_uses_compare_digest_only() -> None:
    src = inspect.getsource(tbank.verify_tbank_token)
    assert "compare_digest" in src
    body = src.replace("compare_digest", "")
    assert "==" not in body


def test_valid_and_forged_token() -> None:
    params = {"Amount": 100, "OrderId": "1"}
    password = "test-password"
    token = tbank.build_tbank_token(params, password)
    full = {**params, "Token": token}
    assert tbank.verify_tbank_token(full, password)
    forged = {**params, "Token": "0" * 64}
    assert not tbank.verify_tbank_token(forged, password)
