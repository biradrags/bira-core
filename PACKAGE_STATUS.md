# Package status

v0.3 — alpha до первого бот-адоптера; публичный API — модуль-владелец, инициализаторы пустые.

| Модуль | Статус | Примечание |
|---|---|---|
| `log.setup` / `log.redaction` | alpha | logfmt + redaction; `LOG_LEVEL` env при `setup_logging(level=None)` |
| `dt.timezone` | alpha | timezone helpers |
| `kbd.wrap` | alpha | `wrap_by_label_width` |
| `db` | alpha | extra `[db]` (включая alembic); BaseDAO — интеграционные тесты на Postgres |
| `redis.client` | alpha | extra `[redis]`; `protect.rate_limit` — тот же extra |
| `di` | alpha | extra `[di]`; провайдеры db/redis/notify в подмодулях |
| `web` | alpha | cron middleware; TG `create_app` — `tgbot.web_bootstrap` |
| `notify` | alpha | `safe_send` / `deliver` / `send_bulk` — подмодули |
| `payments.tbank` | alpha | extra `[payments]` |
| `protect` | alpha | L1 FloodGuard + L2 RateLimiter; Redis — extra `[redis]` |
| `tgbot` | alpha | extra `[tgbot]` (включая aiogram-dialog) |
| `tgbot.forum` | alpha | `is_topic_gone` — детекция удалённого топика |
| `maxbot` | alpha | extra `[max]` |
| `testing` | alpha | mock providers + db fixtures |
| `rules_check` | beta | console-script `bira-rules-check` |
