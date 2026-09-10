# bira-core

Fleet plumbing for aiogram/MAX bots: logging, web bootstrap, cron gates, DAO, notifier, protect, dialogs.

## Install

```bash
uv add "bira-core[db,di,redis,tgbot,testing] @ git+https://github.com/biradrags/bira-core@v0.3.1"
```

### Extras

| Extra | Зависимости | Модули |
|-------|-------------|--------|
| `tgbot` | aiogram, aiogram-dialog | `bira_core.tgbot.*`, `bira_core.notify.send`, `bira_core.notify.classifier` |
| `max` | maxo | `bira_core.maxbot.*` |
| `db` | SQLAlchemy, asyncpg, pydantic, alembic | `bira_core.db.*` |
| `redis` | redis-py | `bira_core.redis.client`, `bira_core.protect.rate_limit` |
| `di` | dishka | `bira_core.di.warmup`, `bira_core.di.notify` (+ `di.db`/`di.redis` с `[db,di]`/`[redis,di]`) |
| `payments` | tenacity | `bira_core.payments.tbank` |
| `testing` | dishka, pytest | `bira_core.testing.*` (платформа — своим extra: `[testing,tgbot]`, `[testing,max]`, `[testing,db]`) |

Публичный контракт — модуль, который им владеет: `bira_core.db.dao`, `bira_core.notify.send`,
`bira_core.tgbot.filters`. Инициализаторы пакетов пустые: `import bira_core.db` ничего не
тянет и ничего не даёт. Модуль, которому нужен отсутствующий пакет, падает штатным
`ModuleNotFoundError` с именем этого пакета — какой профиль его ставит, видно в таблице выше.

MAX-only бот ставит `bira-core[max]` и aiogram не тянет.

`maxo` ставится с PyPI; потребителю на форке достаточно объявить git-source:

```toml
[tool.uv.sources]
maxo = { git = "https://github.com/biradrags/maxo", rev = "..." }
```

## Module map (v0.3)

Зеркальные неймспейсы платформ:

| Пакет | Содержимое |
|-------|------------|
| `bira_core.tgbot.commands` | `CANCEL_COMMAND`, `cancel_command` |
| `bira_core.tgbot.filters` | `IsLikelyBot`, `IsSuperAdmin`, `is_superadmin` |
| `bira_core.tgbot.errors` | `register_error_handlers` |
| `bira_core.tgbot.keyboards` | payment/inline keyboards |
| `bira_core.tgbot.last` | `setup_last_router` |
| `bira_core.tgbot.media_transfer` | cross-chat media helpers |
| `bira_core.tgbot.forum` | `is_topic_gone`, `TOPIC_GONE_MARKERS` |
| `bira_core.tgbot.web_bootstrap` | `create_app` (webhook app builder) |
| `bira_core.tgbot.dialogs.*` | starters, widgets, stale-intent, notifier |
| `bira_core.maxbot.filters` | `IsSuperAdmin` |
| `bira_core.maxbot.web` | `drop_webhook_subscriptions` |
| `bira_core.maxbot.dialogs.*` | widgets, stale-intent, notifier |

Общие слои:

| Модуль | Символы |
|--------|---------|
| `bira_core.log.setup` | `setup_logging`, `LogfmtFormatter`, `ProbeAccessFilter` |
| `bira_core.log.redaction` | `RedactionFilter`, `RECORD_ATTRS`, `redact_log_message` |
| `bira_core.dt.timezone` | `DEFAULT_TIMEZONE`, `get_timezone`, `now_in_timezone`, … |
| `bira_core.kbd.wrap` | `DEFAULT_ROW_CHARS`, `wrap_by_label_width` |
| `bira_core.tls.russian_trusted` | `CA_BUNDLE_NAME`, `load_ca_bundle_context`, `russian_trusted_ssl_context` |
| `bira_core.auth` | `is_superadmin` (SDK-free) |
| `bira_core.web.cron` | `CRON_PORT`, `cron_protocol`, `fly_src_gate` |
| `bira_core.web.bootstrap` | `attach_cron_site`, `create_cron_app`, `health_handler` |
| `bira_core.notify.alerts` | `Alerts` |
| `bira_core.notify.bulk` | `BulkReport`, `send_bulk` |
| `bira_core.notify.delivery` | `DeliveryFailure`, `DeliveryResult`, `FailureCategory` |
| `bira_core.notify.sender` | `MessageSender` |
| `bira_core.notify.split` | `split_message` |
| `bira_core.notify.send` | `deliver`, `safe_send` |
| `bira_core.notify.classifier` | `classify_aiogram` |
| `bira_core.db.base` | `Base`, `NAMING_CONVENTION` |
| `bira_core.db.dao` | `BaseDAO` |
| `bira_core.db.url` | `DbDsn`, `build_url` |
| `bira_core.db.settings` | `DbTenantSettings` |
| `bira_core.db.mixins` | `TimestampMixin` |
| `bira_core.db.alembic` | `resolve_ddl_url`, `run_migrations` |
| `bira_core.redis.client` | `make_redis_client`, `redis_connection_kwargs` |
| `bira_core.di.db` / `.redis` / `.notify` / `.warmup` | Dishka providers, `warm_up` |
| `bira_core.protect.flood_guard` | `FloodGuard` |
| `bira_core.protect.heuristics` | `StartDeduper` |
| `bira_core.protect.rate_limit` | `RateLimiter` |
| `bira_core.protect.middleware` | `flood_guard_middleware` |
| `bira_core.payments.tbank` | `TBankClient`, token helpers |
| `bira_core.testing.db` | `rollback_session`, `savepoint_session` |

### protect: лимиты без UsageGate

Двухуровневый рецепт (L1 per-machine + L2 Redis):

```python
if not flood_guard.allow(user_id):
  return
if not await rate_limiter.allow(f"action:{user_id}", limit=10, window_s=60):
  return
```

`RateLimiter(..., fail_open=True)` при недоступном Redis не блокирует трафик: каждая машина держит свой in-memory бюджет без общего окна (N×лимит, см. докстринг `bira_core.protect.rate_limit`).

### ru-API: сертификат НУЦ Минцифры

`securepay.tinkoff.ru` и другие ru-хосты отдают цепочку НУЦ, корня которой нет в системном
bundle образа. Контекст вешается **на запрос**, не на общий connector, — иначе доверие к НУЦ
расширится на все хосты, куда ходит бот.

```python
from bira_core.tls.russian_trusted import russian_trusted_ssl_context

async with session.post(url, json=body, ssl=russian_trusted_ssl_context()) as resp:
    ...
```

`TBankClient` применяет его сам; переопределяется параметром `ssl_context`. Бандл едет внутри
пакета, тест-страж падает за 60 дней до истечения — обновлять с `gosuslugi.ru/crt`.

## Development

```bash
make install
make docker-up   # Postgres :5499, Redis :6399
make check
```

Module maturity: [PACKAGE_STATUS.md](PACKAGE_STATUS.md).
