"""Resolve every APP/REQUEST factory of dishka providers to surface wiring errors."""

from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping
from typing import Any

from dishka import AsyncContainer, Provider, Scope, make_async_container

__all__ = ["assert_container_builds"]


async def assert_container_builds(
    *providers: Provider,
    context: Mapping[Any, Any] | None = None,
    requested: Collection[Any] = (),
    skip_types: Collection[Any] = (),
) -> None:
    """get() each APP/REQUEST factory, alias and `requested` key; one AssertionError lists all.

    `requested` - keys handlers ask via FromDishka (`X` vs `X | None`); skip types that hit network or DB.
    """
    app_keys: list[tuple[Any, str | None]] = []
    request_keys: list[tuple[Any, str | None]] = [(t, "") for t in requested]
    for provider in providers:
        component = provider.component
        for factory in provider.factories:
            if factory.scope is Scope.APP:
                app_keys.append((factory.provides.type_hint, component))
            elif factory.scope is Scope.REQUEST:
                request_keys.append((factory.provides.type_hint, component))
        request_keys.extend((a.provides.type_hint, component) for a in provider.aliases)

    container = make_async_container(*providers, context=dict(context or {}))
    failures: list[str] = []
    try:
        await _resolve(container, app_keys, skip_types, failures)
        async with container() as request:
            await _resolve(request, request_keys, skip_types, failures)
    finally:
        await container.close()
    if failures:
        raise AssertionError("dishka wiring failed:\n" + "\n".join(failures))


async def _resolve(
    container: AsyncContainer,
    keys: Iterable[tuple[Any, str | None]],
    skip_types: Collection[Any],
    failures: list[str],
) -> None:
    for type_hint, component in dict.fromkeys(keys):
        if type_hint in skip_types:
            continue
        try:
            await container.get(type_hint, component=component)
        except Exception as e:  # noqa: BLE001 - собираем все сбои фабрик в один отчёт
            failures.append(f"{type_hint!r}: {type(e).__name__}: {e}")
