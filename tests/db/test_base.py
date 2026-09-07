import pytest
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from bira_core.db import NAMING_CONVENTION, Base


def test_naming_convention_pinned() -> None:
    """Имена ограничений едут в миграции - менять их можно только осознанно."""
    assert NAMING_CONVENTION == {
        "ix": "ix__%(column_0_label)s",
        "uq": "uq__%(table_name)s__%(column_0_name)s",
        "ck": "ck__%(table_name)s__%(constraint_name)s",
        "fk": "fk__%(table_name)s__%(column_0_name)s__%(referred_table_name)s",
        "pk": "pk__%(table_name)s",
    }


def test_base_metadata_applies_convention() -> None:
    class Probe(Base):
        __tablename__ = "convention_probe"
        __table_args__ = (UniqueConstraint("chat_id", "thread_id"),)

        id: Mapped[int] = mapped_column(primary_key=True)
        chat_id: Mapped[int]
        thread_id: Mapped[int]

    names = {c.name for c in Probe.__table__.constraints}
    assert "pk__convention_probe" in names
    assert "uq__convention_probe__chat_id" in names


def test_mutating_exported_dict_does_not_leak_into_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(NAMING_CONVENTION, "fk", "leaked_%(table_name)s")

    assert Base.metadata.naming_convention["fk"] == (
        "fk__%(table_name)s__%(column_0_name)s__%(referred_table_name)s"
    )
