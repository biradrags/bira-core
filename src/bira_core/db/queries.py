"""Shared SQLAlchemy query helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy import Update, select, update
from sqlalchemy.orm import InstrumentedAttribute


def idempotent_transition(
    model: type[Any],
    *,
    row_id: int,
    status_attr: InstrumentedAttribute[Any],
    from_status: Any,
    to_status: Any,
) -> Update:
    """UPDATE that succeeds only when status_attr still equals from_status."""
    return (
        update(model)
        .where(model.id == row_id, status_attr == from_status)
        .values({status_attr: to_status})
        .returning(model.id)
    )


def claim_due(
    model: type[Any],
    *,
    due_attr: InstrumentedAttribute[Any],
    now: Any,
    limit: int,
    set_values: Mapping[str, Any],
) -> Update:
    """Lock and mark up to limit rows with due_attr < now."""
    due = (
        select(model.id)
        .where(due_attr < now)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    return (
        update(model).where(model.id.in_(due)).values(**set_values).returning(model.id)
    )
