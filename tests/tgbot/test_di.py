import datetime
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import Chat, Message, TelegramObject, Update, User
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import FromDishka

from bira_core.tgbot.di import setup_dishka


class _Token:
    pass


class _Provider(Provider):
    @provide(scope=Scope.REQUEST)
    def token(self) -> _Token:
        return _Token()


def _update(update_id: int) -> Update:
    return Update(
        update_id=update_id,
        message=Message(
            message_id=1,
            date=datetime.datetime.now(tz=datetime.UTC),
            chat=Chat(id=1, type="private"),
            from_user=User(id=1, is_bot=False, first_name="a"),
            text="x",
        ),
    )


async def test_update_middleware_and_handler_share_request_scope() -> None:
    container = make_async_container(_Provider())
    dp = Dispatcher()
    setup_dishka(container, dp)
    seen: dict[str, _Token] = {}

    async def update_mw(
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        seen["update"] = await data["dishka_container"].get(_Token)
        return await handler(event, data)

    dp.update.middleware(update_mw)

    @dp.message()
    async def handler(_: Message, token: FromDishka[_Token]) -> None:
        seen["handler"] = token

    bot = Bot(token="42:FAKE_TOKEN_FOR_TESTS_ONLY")
    await dp.emit_startup(bot=bot)
    await dp.feed_update(bot, _update(1))
    first = seen["handler"]
    await dp.feed_update(bot, _update(2))

    assert seen["update"] is seen["handler"]
    assert seen["handler"] is not first
    await bot.session.close()
    await container.close()
