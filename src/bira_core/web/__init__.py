"""aiohttp web bootstrap facade."""

from bira_core.web.bootstrap import attach_cron_site, create_cron_app, health_handler
from bira_core.web.cron import CRON_PORT, cron_protocol, fly_src_gate

# create_app требует aiogram - bira_core.tgbot.web_bootstrap.
__all__ = [
    "CRON_PORT",
    "attach_cron_site",
    "create_cron_app",
    "cron_protocol",
    "fly_src_gate",
    "health_handler",
]
