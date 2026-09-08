from dataclasses import dataclass, field

from bira_core.notify.alerts import Alerts


@dataclass
class FakeSender:
    sent: list[tuple[int, str]] = field(default_factory=list)

    async def send_message(self, chat_id: int, text: str):
        self.sent.append((chat_id, text))


async def test_alert_goes_to_owner() -> None:
    s = FakeSender()
    await Alerts(s, owner_chat_id=99).alert("db", "pool exhausted")
    assert s.sent and s.sent[0][0] == 99


async def test_dedup_window_suppresses_repeat() -> None:
    s = FakeSender()
    a = Alerts(s, owner_chat_id=99)
    await a.alert("db", "pool exhausted")
    await a.alert("db", "pool exhausted")
    assert len(s.sent) == 1


async def test_never_raises() -> None:
    class Broken:
        async def send_message(self, chat_id: int, text: str):
            raise RuntimeError("boom")

    await Alerts(Broken(), owner_chat_id=99).alert("x", "y")
