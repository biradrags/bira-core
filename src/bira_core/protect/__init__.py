"""L1 in-memory per-machine flood guard; L2 Redis rate limiter (fail_open = N×лимит без окна)."""

from bira_core.protect.flood_guard import FloodGuard
from bira_core.protect.heuristics import StartDeduper
from bira_core.protect.middleware import flood_guard_middleware

# RateLimiter требует redis - bira_core.protect.rate_limit ([protect]).
# IsLikelyBot - фильтр aiogram, живёт в bira_core.tgbot.filters ([tgbot]).
__all__ = [
    "FloodGuard",
    "StartDeduper",
    "flood_guard_middleware",
]
