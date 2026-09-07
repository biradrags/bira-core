"""SQLAlchemy declarative base."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

__all__ = ["NAMING_CONVENTION", "Base"]

# Конвенция имён ограничений. Родословная: словарь пришёл из shvatka (эталон
# архитектуры), оттуда скопирован в solodki-bot. В metrika-bot, metrikamedia,
# max-reposter и sitegen-bot ключ "fk" позже переписали на явную форму с
# referred_table - здесь взята она, как версия четырёх ботов из пяти.
# Кому нужен исходный shvatka-вариант ("%(table_name)s_%(column_0_name)s_fkey",
# сейчас solodki-bot) - собирает свою MetaData из этого словаря, заменив "fk".
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix__%(column_0_label)s",
    "uq": "uq__%(table_name)s__%(column_0_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(column_0_name)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}


class Base(DeclarativeBase):
    """Fleet-wide SQLAlchemy declarative registry."""

    # Копия: SQLAlchemy держит ссылку и применяет конвенцию лениво, при привязке
    # ограничения - правка экспортированного словаря не должна утекать сюда.
    metadata = MetaData(naming_convention=dict(NAMING_CONVENTION))
