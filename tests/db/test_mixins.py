from sqlalchemy.orm import Mapped, mapped_column

from bira_core.db.base import Base
from bira_core.db.mixins import TimestampMixin


def test_timestamp_mixin_columns() -> None:
    class Thing(Base, TimestampMixin):
        __tablename__ = "mixin_probe"
        id: Mapped[int] = mapped_column(primary_key=True)

    cols = Thing.__table__.columns
    assert cols["created_at"].server_default is not None
    assert cols["updated_at"].onupdate is not None
