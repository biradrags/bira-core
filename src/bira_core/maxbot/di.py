from collections.abc import Callable
from typing import Protocol

from dishka import AsyncContainer, Provider, Scope, provide
from maxo import Bot as MaxBot
from maxo import Dispatcher as MaxDispatcher
from maxo.fsm.key_builder import DefaultKeyBuilder
from maxo.integrations.dishka import CONTAINER_NAME, setup_dishka


class MaxToken(Protocol):
    def get_secret_value(self) -> str: ...


class MaxBotProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_max_bot(self, token: MaxToken) -> MaxBot:
        return MaxBot(token=token.get_secret_value(), warming_up=False)


def create_max_dispatcher(
    container: AsyncContainer,
    *,
    setup_handlers: Callable[[MaxDispatcher], None] | None = None,
    setup_middlewares: Callable[[MaxDispatcher], None] | None = None,
) -> MaxDispatcher:
    key_builder = DefaultKeyBuilder(with_destiny=True)
    dp = MaxDispatcher(key_builder=key_builder)
    setup_dishka(container=container, dispatcher=dp, auto_inject=True)
    dp.workflow_data[CONTAINER_NAME] = container
    if setup_middlewares is not None:
        setup_middlewares(dp)
    if setup_handlers is not None:
        setup_handlers(dp)
    return dp
