# Changelog

## v0.1.0 (draft)

### log/

- Донор: scaffold `log/redaction.py`. Снят VENDORED-хедер; добавлен фасад `setup_logging(level, *, extra_patterns)`.
- Адаптации: `BEARER_RE`, `URL_AUTH_RE`, маскировка env-KV по `_is_sensitive_key`, суффиксы `_access_key/_hash/_creds/_terminal_key`, ключ `session`.

### db/

- `build_url` + `DbDsn` — донор `metrika-bot/.../db/url.py`; Protocol с полями `host/port/user/password/name` (не `db_host/db_name` из Settings).
- `BaseDAO` — донор shvatka `infrastructure/db/dao/rdb/base.py`: `NoResultFound`→`None`, без `commit()`, `count()`→`_count()`, без `clock`/`delete_all()`.

### tg/

- `is_superadmin`/`IsSuperAdmin` — донор metrika-bot; superusers через конструктор фильтра, не config DI.
- `register_error_handlers` — скелет metrika errors без stale-intent (v0.2).

### notify/

- `safe_send` — ядро solodki `notifier.py` (retry-after sleep+retry, network/forbidden/bad-request→None); без business/media-group частей.
- `Alerts` — донор geo-bot; `MessageSender` Protocol; `urgent_mention` параметризован (публичная гигиена).

### web/

- `fly_src_gate(allowed)` + `cron_protocol()` — донор scaffold cron middleware; `fly_src_gate` параметризован (не hardcoded `_ALLOWED`).
- `create_app`/`run_webhook`/`run_polling` — донор scaffold `__main__.py.jinja`; без scheduler/max/dialogs.

### di/

- `DbProvider(pool_size, max_overflow)` — scaffold `di/db.py.jinja` + shvatka scopes; `DbDsn` от бота.
- `RedisProvider` — scaffold `make_redis_client` (Fly-suspend retry).
- `NotifierProvider`, `warm_up(container, types)`.

### testing/

- `MockBotProvider`, `MockMessageManagerProvider` — shvatka mocks; aiogram_dialog optional.

### rules_check

- Console-script `bira-rules-check`; донор scaffold `scripts/rules_check.py` (tx-network включён).
