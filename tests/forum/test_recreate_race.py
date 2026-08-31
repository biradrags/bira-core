import asyncio

from aiogram.exceptions import TelegramBadRequest

from bira_core.forum.service import ForumTopics


class FakeStore:
    def __init__(self) -> None:
        self.threads: dict[str, int] = {}
        self.writes: list[int] = []

    async def get_thread_id(self, key: str) -> int | None:
        return self.threads.get(key)

    async def set_thread_id(self, key: str, thread_id: int) -> None:
        self.threads[key] = thread_id
        self.writes.append(thread_id)


class GoneTopicBot:
    """Первый топик считается снесённым: send в него всегда падает."""

    def __init__(self, stale_id: int) -> None:
        self.stale_id = stale_id
        self.created: list[int] = []
        self.delivered: list[tuple[int, str]] = []
        self._next_id = stale_id + 1

    async def create_forum_topic(self, chat_id: int, name: str) -> object:
        await asyncio.sleep(0)
        topic_id = self._next_id
        self._next_id += 1
        self.created.append(topic_id)
        return type("Topic", (), {"message_thread_id": topic_id})()

    async def send_message(
        self, chat_id: int, text: str, *, message_thread_id: int, **kwargs: object
    ) -> str:
        await asyncio.sleep(0)
        if message_thread_id == self.stale_id:
            raise TelegramBadRequest(method=None, message="message thread not found")  # type: ignore[arg-type]
        self.delivered.append((message_thread_id, text))
        return text


async def test_concurrent_send_recreates_topic_once() -> None:
    store = FakeStore()
    store.threads["client-1"] = 900
    bot = GoneTopicBot(stale_id=900)
    forum = ForumTopics(bot, forum_chat_id=-100, store=store)

    await asyncio.gather(
        forum.send("client-1", "hello 1", topic_name="Client 1"),
        forum.send("client-1", "hello 2", topic_name="Client 1"),
    )

    assert len(bot.created) == 1, f"создано топиков: {bot.created}"
    live_topic = store.threads["client-1"]
    assert {topic_id for topic_id, _ in bot.delivered} == {live_topic}
