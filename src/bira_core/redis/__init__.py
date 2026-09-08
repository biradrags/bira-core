"""redis helpers - требует extra [redis]."""

try:
    from bira_core.redis.client import make_redis_client, redis_connection_kwargs
except ImportError as e:  # pragma: no cover - путь без extra [redis]
    e.add_note("pip install bira-core[redis]")
    raise

__all__ = ["make_redis_client", "redis_connection_kwargs"]
