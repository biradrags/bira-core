# Package status

v0.2 — alpha до первого бот-адоптера; API стабилизируется по мере миграции флота.

| Модуль | Статус | Примечание |
|---|---|---|
| `log` | alpha | logfmt + redaction; `LOG_LEVEL` env при `setup_logging(level=None)` |
| `dt` | alpha | timezone helpers |
| `kbd` | alpha | `wrap_by_label_width` |
| `db` | alpha | extra `[db]`; BaseDAO — интеграционные тесты на Postgres |
| `redis` | alpha | extra `[redis]` |
| `di` | alpha | extra `[di]`; lazy-фасад, провайдеры db/redis/notify |
| `web` | alpha | cron middleware; TG bootstrap — extra `tgbot` |
| `notify` | alpha | `safe_send` / `deliver` / `send_bulk` |
| `forum` | alpha | `ForumTopics` + `ThreadStore` |
| `payments` | alpha | extra `[payments]`; T-Bank |
| `protect` | alpha | L1 FloodGuard + L2 RateLimiter; extra `[protect]` для Redis |
| `tgbot` | alpha | extra `[tgbot]` |
| `tgbot.dialogs` | alpha | extra `[dialogs]` |
| `maxbot` | alpha | extra `[max]` |
| `testing` | alpha | mock providers + db fixtures |
| `rules_check` | beta | console-script `bira-rules-check` |
