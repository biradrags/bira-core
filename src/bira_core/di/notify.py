"""Dishka notifier provider."""

from dishka import Provider, provide

from bira_core.notify.alerts import Alerts
from bira_core.notify.send import MessageSender


class NotifierProvider(Provider):
    """Notifier Provider."""

    @provide
    def alerts(self, sender: MessageSender, owner_chat_id: int) -> Alerts:
        """Alerts."""
        return Alerts(sender, owner_chat_id)
