# Changelog

## v0.6.1 (2026-10-15)

Не breaking - необязательный параметр с прежним поведением по умолчанию.

### Новое

- `db.alembic.run_migrations(..., include_object=...)` пробрасывает фильтр autogenerate
  alembic в `context.configure` offline- и online-ветки. Раньше бот на хелпере не мог
  исключить из `alembic check` таблицы без моделей: metrikamedia держит архивные
  `legacy_subscription_*` (аудит платежей), и autogenerate предлагал их удалить.

## v0.6.0 (2026-10-15)

### Новое

- `tgbot.emoji`: `emoji_id(glyph)` и `tg_emoji(glyph)` - анимированные кастом-эмодзи
  стандартного набора Telegram `RestrictedEmoji` (995 символов, `emoji_pack.json` -
  данные пакета). `emoji_id` годится для `icon_custom_emoji_id` кнопок и
  `Style(emoji_id=...)` aiogram_dialog, `tg_emoji` - для HTML-текста. Рендер требует
  Premium у владельца бота; без него клиент показывает символ. Проверено на тест-боте:
  отправка и правка сообщения с такими эмодзи в тексте и на кнопках проходят.
- Харвест из бота-донора; адаптация: пак читается через `importlib.resources` с
  `functools.cache` вместо глобала и пути от файла, а символ без id экранируется
  (`html.escape`), как и обёрнутый.

## v0.5.0 (2026-10-14)

### Breaking

- Удалён `tgbot.dialogs.release` (`ReleasingMessageManager`, `bind_release`,
  `release_current`). Сессию апдейта закрывает REQUEST-область dishka в конце
  апдейта, как в shvatka; шов «геттер -> рендер» остаётся только в solodki-bot
  своей копией (канон dialogs.md, 14.10.2026). Потребителей во флоте нет.

## v0.4.0 (2026-10-14)

Обвязка Telegram-бота из замечаний к plastic-bot#1: `__main__` бота сводится к склейке.
Тег v0.3.4 не ставился - его правка ПДн входит сюда. Не breaking: старые вызовы
`create_app(..., webhook_path=..., webhook_secret=...)` работают как раньше.

### Новое

- `tgbot.web_bootstrap.create_app(base_url=...)` ставит вебхук на старте, после
  startup-хендлеров диспетчера. Без `webhook_secret` секрет случайный на процесс
  (`secrets.token_hex(32)`): из env и fly secrets он уходит. Цена - на время
  деплоя старая машина отвечает 401, Telegram повторяет апдейт на новую.
- `create_app(handle_in_background=...)` - ответ Telegram после обработки (`False`)
  для ботов с идемпотентными хендлерами; дефолт aiogram (`True`) не менялся.
- `tgbot.web_bootstrap.used_update_types(dp)` - `allowed_updates` из хендлеров
  диспетчера без служебного `aiogd_update`; для `set_webhook` и `start_polling`.
- `rules_check`: чек `dishka-request` - `FromDishka[...Dao|...Service]` в слое `tgbot`.
  Штатный `dishka.integrations.aiogram.setup_dishka` открывает REQUEST-область на
  каждом observer: DAO из middleware на `dp.update` и `FromDishka[HolderDao]` хендлера -
  два объекта с двумя сессиями, и eager release отпускает не ту транзакцию. REQUEST-
  объекты хендлеры берут из data (как в shvatka); APP-сервис глушится `# dishka-request-ok`.
- `di.db.DbProvider(pool_recycle=..., connect_timeout=...)` - короткий recycle для Fly
  suspend, который рвёт простаивающие соединения; дефолты прежние (1800, без таймаута).
- `tgbot.dialogs.release`: `ReleasingMessageManager`, `bind_release(dao)`,
  `release_current` - eager release из канона dialogs.md (инцидент solodki
  20.08.2026), до этого копией в каждом боте с диалогами. `bind_release` зовётся
  в InitMiddleware бота на `dp.update` с тем же DAO, что лежит в `data["dao"]`.

### Исправления

- `redact_extra` и `RedactionFilter` маскируют поля `extra` с ключами `phone`, `username`,
  `transcript`, `description` и суффиксом `_phone`. Раньше телефон пользователя бота в `extra`
  проходил целиком: числовое значение считалось счётчиком и не редактировалось.

## v0.3.3 (2026-09-17)

Свип по классу бага из v0.3.2: тот же пробел «токен без имени ключа» нашёлся ещё
у трёх провайдеров флота. Не breaking — только добавления.

### Исправления

- `RedactionFilter` не маскировал голые `xai-…` (metrikamedia), `gsk_…` (metrikamedia)
  и `AKIA…`/`ASIA…` (Tigris/S3 — metrika-bot, metrikamedia, solodki-bot, cbexchange).
  Все три проверены прогоном до правки — утекали; kv-формы (`XAI_API_KEY=…`) закрывались
  и раньше. Добавлены `XAI_KEY_RE`, `GROQ_KEY_RE`, `AWS_KEY_ID_RE`. Ложных срабатываний
  на коротких строках (`AKIA`, `gsk_ short`, `xai-short`) нет — минимальные длины в
  паттернах проверены тестом.
- Маскируется только AWS access key **id**: сам secret access key — 40 символов base64
  без префикса, по форме от случайной строки неотличим, ловится лишь по имени ключа
  (`AWS_SECRET_ACCESS_KEY` уже в `SENSITIVE_KEY_NAMES`).

## v0.3.2 (2026-09-17)

Один пробел в редактировании логов, найденный при пересборке btt-bot (первый бот
флота с Яндекс.Диском). Не breaking — только добавления, публичные сигнатуры не менялись.

### Исправления

- `RedactionFilter` не маскировал OAuth-токен Яндекс.Диска, когда тот попадает в лог
  без имени ключа. Форма `YADISK_TOKEN=y0_…` закрывалась и раньше — ключ оканчивается
  на `_token`, его ловит `_is_sensitive_key`. Но библиотека `yadisk` отдаёт токен ещё
  двумя путями, и оба проверены живым прогоном `redact_log_message` — утекали:
  заголовком `Authorization: OAuth y0_…` и голым значением в тексте исключения
  (`yadisk request failed: y0_…`). Добавлены `OAUTH_SCHEME_RE` (по образцу `BEARER_RE`:
  имя схемы сохраняется, маскируется значение за ним) и `YANDEX_TOKEN_RE` на префикс
  `y0_`/`y0-`. Лямбда маскирования схемы вынесена в `_mask_scheme_value` и переиспользована
  для `Bearer` — поведение Bearer не менялось, покрыто прежним тестом.
- `YADISK_TOKEN` добавлен в `SECRET_ENV_NAMES`, форма `yandex_oauth` — в
  `SECRET_SHAPE_SAMPLES`.

## v0.3.1 (2026-09-10)

Ревью-раунд сверки `tgbot.forum` и `db.alembic` с кодом ботов флота: два пробела —
неполный набор маркеров «топик удалён» и отсутствующий sync-режим миграций.
Не breaking — только добавления, публичные сигнатуры не менялись.

### Исправления

- `TOPIC_GONE_MARKERS` не ловил `TOPIC_ID_INVALID` — маркер, на который уже
  опирается `metrika-bot/metrika/services/forum_cleanup.py`; миграция бота на
  `is_topic_gone` тихо теряла бы часть удалённых топиков в суточной чистке.
  Обход всех восьми ботов флота грепом по маркерам нашёл ещё два реальных,
  уже эксплуатируемых варианта — добавлены и они: `"topic not found"`
  (`solodki-bot/app/services/forum.py`) и `"topic_not_found"`
  (`metrika-bot/scripts/cleanup_self_userbot_clients.py`). Дубль
  `"topic_deleted"`/`"TOPIC_DELETED"` (после `.lower()` в `is_topic_gone` — одна
  и та же строка) сознательно не тронут: `TOPIC_GONE_MARKERS` — публичный
  `frozenset` в `__all__`, а не только input для `is_topic_gone`; убрать один
  регистр — риск сломать код, который делает точное членство по конкретному
  кейсу, а не только вызывает функцию. Не breaking для самой `is_topic_gone` —
  дедуп не даёт функционального выигрыша, только скрытый риск.
- `run_migrations` не имел sync-ветки. Локальный `metrika-bot/metrika/migrations/env.py`
  умеет гонять миграции через `create_engine` (sync), когда URL не `+asyncpg` —
  на этом стоят три integration/e2e фикстуры (metrika-bot, metrikamedia), которые
  подменяют `+asyncpg` на `+psycopg` перед `alembic upgrade head` в подпроцессе.
  Ветка перенесена в либу 1:1 (новые `run_migrations_sync` + предикат
  `_use_sync_engine`), без изменения сигнатуры `run_migrations`.

### Проверено, не тронуто

- `_connect_args_for_host` (условный `ssl=False` только для `.flycast`/`.internal`)
  не ломает `make db-upgrade` в dev/CI — подтверждено живым подключением: `+asyncpg`
  без явного `ssl=False` коннектится к локальному docker Postgres без проблем
  (asyncpg не поднимает TLS, если сервер его не предлагает). Безусловный
  `ssl=False` в локальном `env.py` metrika-bot — более широкая, но не более
  корректная форма того же самого; либа оставлена как есть.

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
