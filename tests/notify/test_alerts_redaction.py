from unittest.mock import AsyncMock

import pytest

from bira_core.notify.alerts import Alerts


@pytest.mark.asyncio
async def test_alert_body_redacted_before_send() -> None:
    sender = AsyncMock()
    alerts = Alerts(sender, owner_chat_id=1, window_s=0)
    await alerts.alert("test", "token=7213001234:AAFakeFakeFakeFakeFakeFakeFakeFak")
    body = sender.send_message.await_args.args[1]
    assert "7213001234:AAFake" not in body
    assert "***" in body
