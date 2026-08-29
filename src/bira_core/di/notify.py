"""Dishka notifier provider."""

from dishka import Provider, provide

from bira_core.notify.alerts import Alerts
from bira_core.notify.send import MessageSender


class NotifierProvider(Provider):
    """Wire MessageSender and owner chat into Alerts."""

    @provide
    def alerts(self, sender: MessageSender, owner_chat_id: int) -> Alerts:
        """Build Alerts bound to the ops owner chat."""
        return Alerts(sender, owner_chat_id)
