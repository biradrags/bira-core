"""MAX webhook helpers."""

import logging

from maxo import Bot

logger = logging.getLogger(__name__)


async def drop_webhook_subscriptions(bot: Bot) -> None:
    """Unsubscribe all MAX webhooks before switching to long polling."""
    if not bot.state.started:
        await bot.start()
    result = await bot.get_subscriptions()
    for sub in result.subscriptions:
        await bot.unsubscribe(url=sub.url)
    if result.subscriptions:
        logger.info("Max webhook subscriptions dropped for polling")
