import pytest

from bira_core.notify.bulk import send_bulk
from bira_core.notify.delivery import DeliveryFailure, DeliveryResult, FailureCategory


@pytest.mark.asyncio
async def test_send_bulk_counts_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []

    async def fake_sleep(sec: float) -> None:
        sleeps.append(sec)

    monkeypatch.setattr("asyncio.sleep", fake_sleep)

    async def send_fn(chat_id: int) -> DeliveryResult:
        if chat_id == 2:
            return DeliveryResult(
                failure=DeliveryFailure(category=FailureCategory.OTHER, raw="fail")
            )
        return DeliveryResult(sent=object())

    report = await send_bulk([1, 2], send_fn, delay=0.01)
    assert report.sent == 1
    assert report.failed == 1
    assert len(report.failures) == 1
