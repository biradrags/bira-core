"""TLS trust for ru-API, отдающих цепочку НУЦ Минцифры."""

from __future__ import annotations

import ssl
from functools import cache
from importlib.resources import as_file, files

CA_BUNDLE_NAME = "russiantrustedca.pem"

__all__ = ["CA_BUNDLE_NAME", "load_ca_bundle_context", "russian_trusted_ssl_context"]


@cache
def russian_trusted_ssl_context() -> ssl.SSLContext:
    """Системные CA плюс корневой и подчинённый сертификаты НУЦ Минцифры.

    Вешать на конкретный запрос (``session.post(..., ssl=ctx)``), а не на общий
    connector: иначе доверие к НУЦ расширится на все хосты, куда ходит бот.
    """
    context = ssl.create_default_context()
    _load_bundle(context)
    return context


def load_ca_bundle_context() -> ssl.SSLContext:
    """Контекст ТОЛЬКО с бандлом НУЦ, без системных CA - для проверок бандла."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    _load_bundle(context)
    return context


def _load_bundle(context: ssl.SSLContext) -> None:
    resource = files("bira_core.tls").joinpath(CA_BUNDLE_NAME)
    with as_file(resource) as path:
        context.load_verify_locations(cafile=str(path))
