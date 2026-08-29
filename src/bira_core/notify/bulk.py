"""Bulk send with delivery classification."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field

from bira_core.notify.delivery import DeliveryFailure, DeliveryResult, FailureCategory

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BulkReport:
    """Bulk Report."""

    sent: int = 0
    failed: int = 0
    failures: list[tuple[int, DeliveryFailure]] = field(default_factory=list)


async def send_bulk(
    recipients: Sequence[int],
    send_fn: Callable[[int], Awaitable[DeliveryResult]],
    *,
    concurrency: int = 1,
    delay: float = 0.05,
) -> BulkReport:
    """Send bulk."""
    report = BulkReport()
    sem = asyncio.Semaphore(max(1, concurrency))

    async def _one(chat_id: int) -> None:
        async with sem:
            result = await send_fn(chat_id)
            if result.sent is not None:
                report.sent += 1
            elif result.failure is not None:
                report.failed += 1
                report.failures.append((chat_id, result.failure))
                if result.failure.category == FailureCategory.FLOOD_WAIT:
                    wait = result.failure.retry_after or 0
                    await asyncio.sleep(min(wait, 30))
            else:
                report.failed += 1
            if delay > 0:
                await asyncio.sleep(delay)

    await asyncio.gather(*[_one(cid) for cid in recipients])
    return report
