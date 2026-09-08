# Changelog

## v0.3.0 (2026-09-08)

Корень: библиотека держала невозможный трёхсторонний контракт — широкие публичные фасады,
мелкие extras и строгая типизация. Python исполняет `parent/__init__.py` даже при глубоком
импорте, поэтому каждая попытка удержать все три рождала адаптер (`__getattr__`, зеркала
`TYPE_CHECKING`, eager с `try/except`). Убрана одна сторона: фасады. Публичный контракт —
модуль-владелец; инициализаторы пакетов пустые.

### Breaking — пути импорта

| Символы | Публичный путь |
|---|---|
| `setup_logging`, `LogfmtFormatter`, `ProbeAccessFilter` | `bira_core.log.setup` |
| `RedactionFilter`, `RECORD_ATTRS`, `redact_log_message` | `bira_core.log.redaction` |
| `DEFAULT_TIMEZONE`, `get_timezone`, `now_in_timezone`, … | `bira_core.dt.timezone` |
| `DEFAULT_ROW_CHARS`, `wrap_by_label_width` | `bira_core.kbd.wrap` |
| `CA_BUNDLE_NAME`, `load_ca_bundle_context`, `russian_trusted_ssl_context` | `bira_core.tls.russian_trusted` |
| `is_superadmin` (SDK-free) | `bira_core.auth` |
| `CRON_PORT`, `cron_protocol`, `fly_src_gate` | `bira_core.web.cron` |
| `attach_cron_site`, `create_cron_app`, `health_handler` | `bira_core.web.bootstrap` |
| `Alerts` | `bira_core.notify.alerts` |
| `BulkReport`, `send_bulk` | `bira_core.notify.bulk` |
| `DeliveryFailure`, `DeliveryResult`, `FailureCategory` | `bira_core.notify.delivery` |
| `MessageSender` | `bira_core.notify.sender` |
| `split_message` | `bira_core.notify.split` |
| `deliver`, `safe_send` | `bira_core.notify.send` |
| `classify_aiogram` | `bira_core.notify.classifier` |
| `Base`, `NAMING_CONVENTION` | `bira_core.db.base` |
| `BaseDAO` | `bira_core.db.dao` |
| `DbDsn`, `build_url` | `bira_core.db.url` |
| `DbTenantSettings` | `bira_core.db.settings` |
| `TimestampMixin` | `bira_core.db.mixins` |
| `resolve_ddl_url`, `run_migrations` | `bira_core.db.alembic` |
| `make_redis_client`, `redis_connection_kwargs` | `bira_core.redis.client` |
| `DbProvider` / `RedisProvider` / `NotifierProvider` / `warm_up` | `bira_core.di.db` / `.redis` / `.notify` / `.warmup` |
| `FloodGuard` | `bira_core.protect.flood_guard` |
| `StartDeduper` | `bira_core.protect.heuristics` |
| `RateLimiter` | `bira_core.protect.rate_limit` |
| `flood_guard_middleware` | `bira_core.protect.middleware` |
| `TBankClient`, token helpers | `bira_core.payments.tbank` |
| `IsLikelyBot`, `IsSuperAdmin`, `is_superadmin` | `bira_core.tgbot.filters` |
| `is_topic_gone`, `TOPIC_GONE_MARKERS` | `bira_core.tgbot.forum` |

### Снято

- Публичные фасады и шесть блоков `try/except ImportError` в инициализаторах.
- `ForumTopics` / `ThreadStore` — ноль потребителей; `is_topic_gone` переехал в `tgbot.forum`.
- Lifecycle-раннеры `run_webhook`, `run_polling`, `MaxPollingManager` — процессом владеет бот.
- `scripts/smoke_extra.py`, `tests/test_extras_contract.py`, `tests/test_public_api.py` —
  контракт установки теперь смоук колеса в CI (`smoke-wheel`, 8 профилей).
- Extras-алиасы `alembic`, `protect`, `dialogs` влиты в `db`, `redis`, `tgbot` (10 → 7).

### Контракт установки

CI собирает wheel и импортирует публичные модули в чистом venv по каждому extra.
Отсутствующий пакет — штатный `ModuleNotFoundError` с именем реального модуля.

## v0.2.2 (2026-09-08)

Найдено при миграции metrikamedia: `py.typed` в пакете есть, но половина публичного API
приезжала потребителю как `Any`.

### Исправления

- **Ленивые фасады стирали типы.** Символы, выдаваемые через `__getattr__` (ленивый импорт
  под extras), для mypy потребителя были `Any` — и весь код вокруг них не проверялся.
  Задело девять фасадов: корневой, `db`, `di`, `maxbot`, `notify`, `protect`, `redis`,
  `testing`, `web`. Например `deliver` в адоптере давал `no-any-return` на функции,
  честно объявленной как `-> DeliveryResult`. Теперь у каждого ленивого символа есть
  зеркальный импорт под `if TYPE_CHECKING`: рантайм остаётся ленивым, mypy видит
  настоящие сигнатуры.
- Гард `tests/test_facade_typing.py`: обходит все фасады с `__getattr__` и требует, чтобы
  каждое имя из `__all__` было видимо статически. Новый ленивый экспорт без зеркала
  роняет тест, а не тихо приезжает как `Any` через полгода.

## v0.2.1 (2026-09-07)

Подготовка к первому боту-адоптеру (metrikamedia). Два пробела, найденные при сверке
либы с кодом бота: харвест `Base` взял версию без конвенции имён, а детекция «топик
удалён» была спрятана в приватную функцию.

### Breaking

- `Base.metadata` теперь несёт флотовую naming convention. Модели на этом `Base` получают
  предсказуемые имена ограничений (`pk__<table>`, `uq__<table>__<col0>`, …) вместо
  постгресовых дефолтов. Проекту, у которого схема уже создана под другими именами,
  переезд на этот `Base` даст дифф в автогенерации alembic — сверять до миграции.

### Новое

- `bira_core.db.NAMING_CONVENTION` — словарь конвенции отдельно от `Base`. Нужен тем, у
  кого одно правило отличается. Родословная: словарь пришёл из `shvatka` и оттуда
  скопирован в solodki-bot; в metrika-bot, metrikamedia, max-reposter и sitegen-bot ключ
  `fk` позже переписали на явную форму с `referred_table`. В либу взята версия четырёх
  ботов из пяти; кому нужен исходный shvatka-вариант
  (`%(table_name)s_%(column_0_name)s_fkey`) — собирает свою `MetaData` из этого словаря,
  заменив один ключ.
- `bira_core.forum.is_topic_gone(exc)` — публичная. Распознать «топика больше нет» нужно и
  тем, кто его не пересоздаёт, а скипает: политика доставки у потребителей разная, а
  список маркеров один.
- `ForumTopics.ensure_topic(..., chat_id=...)` и `ForumTopics.send(..., chat_id=...)` —
  чат можно передать вызовом, перекрыв конструктор. Для ботов, у которых форум свой на
  каждого владельца (metrika-bot: форум на менеджера). Ключ тогда обязан включать чат.

## v0.2.0 — фикс-раунд №2 (2026-08-31)

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

## v0.2.0 — харвест (2026-08-28)

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
