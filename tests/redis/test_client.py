from unittest.mock import patch

from bira_core.redis import make_redis_client, redis_connection_kwargs


def test_redis_connection_kwargs_shape() -> None:
    kwargs = redis_connection_kwargs(decode_responses=True)
    assert kwargs["decode_responses"] is True
    assert kwargs["socket_keepalive"] is True
    assert "retry" in kwargs


def test_make_redis_client_default_decode_responses() -> None:
    with patch("redis.asyncio.from_url") as from_url:
        from_url.return_value = object()
        make_redis_client("redis://localhost:6379/0")
        assert from_url.call_args.kwargs["decode_responses"] is True


def test_make_redis_client_uses_from_url() -> None:
    with patch("redis.asyncio.from_url") as from_url:
        from_url.return_value = object()
        make_redis_client("redis://localhost:6379/0", decode_responses=False)
        from_url.assert_called_once()
        args, kwargs = from_url.call_args
        assert args[0] == "redis://localhost:6379/0"
        assert kwargs["decode_responses"] is False
