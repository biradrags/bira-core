# bira-core

Fleet plumbing for aiogram bots: logging redaction, webhook bootstrap, cron gates, DAO base, notifier.

## Install

```bash
uv add "bira-core[db,di,redis] @ git+https://github.com/biradrags/bira-core@v0.1.0"
```

## Quickstart

```python
from aiogram import Bot
from bira_core import safe_send, run_webhook
from aiogram import Dispatcher

async def main() -> None:
    dp = Dispatcher()
    bot = Bot(token="...")
    await safe_send(bot, chat_id=1, text="hello")
    await run_webhook(
        dp,
        bot,
        port=8080,
        webhook_url="https://example.com/webhook/secret",
        webhook_secret="secret",
    )
```

Module maturity and migration gates: [PACKAGE_STATUS.md](PACKAGE_STATUS.md).

## Development

```bash
make install
docker compose up -d   # Postgres on localhost:5499 for DAO tests
make check
```
