# bira-core

Fleet plumbing for aiogram/MAX bots: logging, web bootstrap, cron gates, DAO, notifier, protect, dialogs.

## Install

```bash
uv add "bira-core[db,di,redis,tgbot,dialogs,protect] @ git+https://github.com/biradrags/bira-core@v0.3.0"
```

### Extras

| Extra | Зависимости | Модули |
|-------|-------------|--------|
| `tgbot` | aiogram | `bira_core.tgbot`, `bira_core.notify` (TG) |
| `dialogs` | aiogram, aiogram-dialog | `bira_core.tgbot.dialogs` |
| `max` | maxo | `bira_core.maxbot` |
| `db` | SQLAlchemy, asyncpg, pydantic | `bira_core.db`, `TimestampMixin`, `DbTenantSettings` |
| `alembic` | alembic | `resolve_ddl_url`, `run_migrations` |
| `redis` | redis-py | `bira_core.redis` |
| `di` | dishka | `bira_core.di` |
| `protect` | redis (опционально для L2) | `bira_core.protect` |
| `payments` | tenacity | `bira_core.payments` |
| `testing` | dishka, pytest | `bira_core.testing` (платформа — своим extra: `[testing,tgbot]`, `[testing,max]`, `[testing,db]`) |

Контракт установки, проверяемый в CI на каждом extra отдельно:

- **Чистые фасады импортируются при голой установке** — `log`, `dt`, `kbd`, `tls`, `auth`,
  `web`, `forum`, `notify`, `protect`, `testing`. Функция, которой нужен extra, живёт в
  подмодуле, который его требует: `notify.send` (`deliver`, `safe_send`),
  `tgbot.web_bootstrap` (`create_app`, `run_polling`), `protect.rate_limit` (`RateLimiter`),
  `di.db` / `di.redis`, `maxbot.di`, `testing.db` / `.providers_tg` / `.providers_max`.
- **Фасад слоя импортируется ⇔ стоит его extra** — `db`, `di`, `redis`, `tgbot`, `maxbot`,
  `payments`. Без него import падает `ImportError` с подсказкой, какой extra ставить.
  Ленивых `__getattr__` нет: всё, что фасад экспортирует, mypy потребителя видит.

MAX-only бот ставит `bira-core[max]` и aiogram не тянет.

`maxo` ставится с PyPI; потребителю на форке достаточно объявить git-source:

```toml
[tool.uv.sources]
maxo = { git = "https://github.com/biradrags/maxo", rev = "..." }
```

## Module map (v0.2)

Зеркальные неймспейсы платформ:

| Пакет | Содержимое |
|-------|------------|
| `bira_core.tgbot` | commands, keyboards, filters, media_transfer, errors |
| `bira_core.tgbot.dialogs` | starters, widgets, stale-intent, notifier |
| `bira_core.maxbot` | polling, filters, web, di |
| `bira_core.maxbot.dialogs` | widgets, stale-intent, notifier |

Общие слои:

- `log` — logfmt `setup_logging`, redaction (`LOG_LEVEL` из env только при `level=None`)
- `db` — `build_url`, `BaseDAO`, alembic helpers, query builders; `Base` с флотовой конвенцией имён ограничений (словарь отдельно — `NAMING_CONVENTION`, для проектов с одним отличающимся правилом)
- `dt` — timezone helpers
- `web` — cron app, `attach_cron_site`, `CRON_PORT=8081`; `create_app`/`run_polling` — extra `tgbot`
- `notify` — `safe_send` (обычный код), `deliver`/`DeliveryResult` (рассылки; категории failure закрыты enum)
- `protect` — L1 in-memory `FloodGuard`, `StartDeduper`; L2 `RateLimiter` — `protect.rate_limit`; `IsLikelyBot` — aiogram-фильтр, `bira_core.tgbot`
- `forum` — `ForumTopics` + `ThreadStore` protocol; `is_topic_gone(exc)` отдельно, для тех, кто топик не пересоздаёт
- `tls` — `russian_trusted_ssl_context()` для ru-API за цепочкой НУЦ Минцифры
- `payments` — T-Bank client
- `testing` — mock DI, db fixtures (`rollback_session`, `savepoint_session`)

### ForumTopics + ThreadStore

Потребитель реализует `ThreadStore` поверх своего DAO и регистрирует `ForumTopics` в Dishka:

```python
from dishka import Provider, Scope, provide
from bira_core.forum import ForumTopics, ThreadStore


class MyThreadStore:
    async def get_thread_id(self, key: str) -> int | None: ...
    async def set_thread_id(self, key: str, thread_id: int) -> None: ...


class ForumProvider(Provider):
    @provide(scope=Scope.APP)
    def forum(self, bot: Bot, store: MyThreadStore) -> ForumTopics:
        return ForumTopics(bot, forum_chat_id=-100123, store=store)
```

### protect: лимиты без UsageGate

Двухуровневый рецепт (L1 per-machine + L2 Redis):

```python
if not flood_guard.allow(user_id):
  return
if not await rate_limiter.allow(f"action:{user_id}", limit=10, window_s=60):
  return
```

`RateLimiter(..., fail_open=True)` при недоступном Redis не блокирует трафик: каждая машина держит свой in-memory бюджет без общего окна (N×лимит, см. докстринг `bira_core.protect`).

### ru-API: сертификат НУЦ Минцифры

`securepay.tinkoff.ru` и другие ru-хосты отдают цепочку НУЦ, корня которой нет в системном
bundle образа. Контекст вешается **на запрос**, не на общий connector, — иначе доверие к НУЦ
расширится на все хосты, куда ходит бот.

```python
from bira_core.tls import russian_trusted_ssl_context

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
