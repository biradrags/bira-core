import bira_core

EXPECTED = {
    "setup_logging",
    "RedactionFilter",
    "build_url",
    "DbDsn",
    "BaseDAO",
    "Base",
    "is_superadmin",
    "IsSuperAdmin",
    "register_error_handlers",
    "safe_send",
    "MessageSender",
    "Alerts",
    "fly_src_gate",
    "cron_protocol",
    "create_app",
    "run_webhook",
    "run_polling",
    "DbProvider",
    "RedisProvider",
    "NotifierProvider",
    "warm_up",
}


def test_public_api_pinned() -> None:
    assert set(bira_core.__all__) == EXPECTED
