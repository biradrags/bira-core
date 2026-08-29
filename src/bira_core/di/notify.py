from dishka import Provider, provide

from bira_core.notify.alerts import Alerts
from bira_core.notify.send import MessageSender


class NotifierProvider(Provider):
    @provide
    def alerts(self, sender: MessageSender, owner_chat_id: int) -> Alerts:
        return Alerts(sender, owner_chat_id)
