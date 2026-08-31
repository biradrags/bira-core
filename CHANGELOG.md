# Changelog

## Unreleased — фикс-раунд №2 (2026-08-31)

Ревизия PR #1: шесть блокеров мержа плюс P1-хвост.

### Breaking

- `bira_core.kbd` — пакет (`kbd/wrap.py` + фасад); приватная `_wrap_indices` удалена, тесты ходят через публичную функцию.
- `bira_core.maxbot.dialogs` — пакет (`errors`/`notifier`/`widgets`), зеркально `tgbot.dialogs`. `maxbot.notifier` и `maxbot.errors` как модули больше не существуют.
- `bira_core.testing.providers` разбит на `providers_tg` / `providers_max`: MAX-провайдеры больше не требуют aiogram. Новый extra `testing`.
- Удалены без потребителей: `chat_id_command`, `CHAT_ID_COMMAND`, `register_debug_commands`, `IsServiceChat`, `build_cancel_back_keyboard`, `ToMainMenuCD`, `CancelResetCD`, приватная `_cancel_reset`.
- `create_cron_app(allowed=...)` — параметр обязателен; дефолт с именем внутреннего приложения убран.
- `web.bootstrap._health` → публичный `web.health_handler`.
- `IsLikelyBot` возвращает `True` для похожего на бота (было наоборот). Пропускать людей — `~IsLikelyBot()`. `new_id_threshold` поднят до 8 млрд.

### Исправления

- `bira-core[max]` был неустанавливаем: `bira_core.maxbot` тянул dishka. DI-символы ушли за ленивый фасад с подсказкой `[max,di]`.
- MAX stale-intent был заглушкой-no-op с докстрингом «зеркало tgbot» — теперь рабочая реализация по канону `dialogs.md`.
- Редакция логов: `OPENAI_KEY_RE` не ловил `sk-proj-…`/`sk-svcacct-…`; строковые значения в `extra` шли мимо KV-маскирования, из-за чего `?token=` в URL утекал.
- `Alerts` и `MessageSender` больше не требуют aiogram (протокол вынесен в `notify/sender.py`).
- `split_message` отдавал куски длиннее лимита при 100+ частях (пересчёт нумерации терял результат).
- `ForumTopics`: пересоздание топика шло мимо per-key лока — две гонки создавали два топика и теряли сообщение.
- `FloodGuard` и fallback `RateLimiter` росли без вытеснения; fallback теперь честно оконный.
- CI: матрица `smoke-extras` падала на квотинге и не проверяла ничего; смоук-карта строится обходом пакета, а не руками.

### Новое

- `bira_core.tls.russian_trusted_ssl_context()` — доверие цепочке НУЦ Минцифры для ru-API (T-Bank и далее), вешается на запрос. `TBankClient` использует по умолчанию. Тест-страж падает за 60 дней до протухания бандла.

## v0.2.0 (2026-08-28)

Полный харвест дублей флота (Phase A + B). Один релиз перед первым бот-адоптером.

### Breaking

- `setup_logging(level, *, extra_patterns=(), extra_silence=())` — logfmt + probe-filter + silence-список (v0.1 тонкий StreamHandler заменён).
- `setup_logging`: явный `level` выигрывает у env `LOG_LEVEL` (раньше env перебивал аргумент).
- `aiogram` убран из core-зависимостей; TG-слой — extra `tgbot` (`pip install bira-core[tgbot]`). `dialogs` требует `aiogram>=3.20` явно.
- `bira_core.tg` → `bira_core.tgbot`; `bira_core.dialogs` → `bira_core.tgbot.dialogs`; `MaxUser.tg_id` → `MaxUser.user_id`.
- Нотифаеры: `safe_*` → `answer`/`warn`/`delete`/`ack` (вариант А); `delete_if_exists` — свободная функция.
- `wrap_by_label_width(buttons, max_row_chars)` — донорская сигнатура; индексная версия — `_wrap_indices`.
- `protect`: `RateLimiter.hit` → `allow`; `UsageGate` удалён (рецепт в README).
- `cancel_reset` удалён из dialogs API; канон — `cancel_delete`.
- `StaleIntentNotifier` удалён; `clear_stale_intent` берёт `bot` из события.
- `redis`/`dt`: реализация в `redis/client.py`, `dt/timezone.py`; фасады в `__init__.py`.
- `log/redaction`: движок в `log/_internal.py`.

### Un-breaking

- `make_redis_client(..., decode_responses=True)` — дефолт как у донора.

### Новые модули

- `db.alembic`, `DbTenantSettings`, `TimestampMixin`, `db.queries`
- `dt`, `redis` (публичный), `kbd`, `tg.commands/keyboards/last/media_transfer`
- `dialogs`, `maxbot`, `forum`, `payments`, `protect` (L1–L4)
- `notify.delivery`, `send_bulk`, `split_message`
- `testing.db` (xdist lock, rollback/savepoint sessions)

### web

- `CRON_PORT`, `attach_cron_site`, `create_cron_app` (фикс `_cron_runner` до `.start()`).

### Адаптации по донорам

- TBank: только `hmac.compare_digest`; идемпотентный переход статуса в донорах ботов (Phase 0).
- `media_transfer`: guard `Path(filename).name` против path traversal.

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
