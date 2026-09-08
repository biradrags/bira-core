import ssl
import time

from bira_core.tls.russian_trusted import (
    load_ca_bundle_context,
    russian_trusted_ssl_context,
)

MIN_DAYS_LEFT = 60
_DAY_SECONDS = 86400


def test_bundle_carries_root_and_sub_ca() -> None:
    subjects = {
        dict(part for rdn in cert["subject"] for part in rdn).get("commonName")
        for cert in load_ca_bundle_context().get_ca_certs()
    }

    assert "Russian Trusted Root CA" in subjects
    assert "Russian Trusted Sub CA" in subjects


def test_bundle_is_not_about_to_expire() -> None:
    """Падает за 60 дней до протухания: иначе узнаем от клиента с непрошедшей оплатой."""
    now = time.time()

    for cert in load_ca_bundle_context().get_ca_certs():
        days_left = (ssl.cert_time_to_seconds(cert["notAfter"]) - now) / _DAY_SECONDS
        common_name = dict(part for rdn in cert["subject"] for part in rdn).get(
            "commonName"
        )
        assert days_left > MIN_DAYS_LEFT, (
            f"{common_name}: осталось {days_left:.0f} дней - обновить бандл НУЦ "
            f"с gosuslugi.ru/crt во всех копиях флота"
        )


def test_context_trusts_system_cas_too() -> None:
    context = russian_trusted_ssl_context()

    assert isinstance(context, ssl.SSLContext)
    assert len(context.get_ca_certs()) > len(load_ca_bundle_context().get_ca_certs())
