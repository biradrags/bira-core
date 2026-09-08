"""Dishka provider facade - требует extra [di]."""

try:
    from bira_core.di.notify import NotifierProvider
    from bira_core.di.warmup import warm_up
except ImportError as e:  # pragma: no cover - путь без extra [di]
    e.add_note("pip install bira-core[di]")
    raise

# DbProvider - bira_core.di.db ([db,di]); RedisProvider - bira_core.di.redis ([redis,di]).
__all__ = ["NotifierProvider", "warm_up"]
