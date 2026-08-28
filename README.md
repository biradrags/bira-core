# bira-core

Fleet plumbing for aiogram bots: logging, web bootstrap, cron gates, DAO, notifier, protect, dialogs, MAX.

## Install

```bash
uv add "bira-core[db,di,redis,dialogs,protect] @ git+https://github.com/biradrags/bira-core@v0.2.0"
```

### Extras

| Extra | Зависимости | Модули |
|-------|-------------|--------|
| `db` | SQLAlchemy, asyncpg, pydantic | `bira_core.db`, `TimestampMixin`, `DbTenantSettings` |
| `alembic` | alembic | `resolve_ddl_url`, `run_migrations` |
| `redis` | redis-py | `bira_core.redis` |
| `di` | dishka | `bira_core.di` |
| `dialogs` | aiogram-dialog | `bira_core.dialogs` |
| `protect` | redis (опционально для L2+) | `bira_core.protect` |
| `payments` | tenacity | `bira_core.payments` |
| `max` | maxo | `bira_core.maxbot` |

`maxo` не на PyPI — в `pyproject.toml` потребителя укажите git-source:

```toml
[tool.uv.sources]
maxo = { git = "https://github.com/biradrags/maxo", rev = "..." }
```

## Module map (v0.2)

- `log` — logfmt `setup_logging`, redaction
- `db` — `build_url`, `BaseDAO`, alembic helpers, query builders
- `web` — webhook app, `attach_cron_site`, `CRON_PORT=8081`
- `notify` — `safe_send`, `deliver`, `send_bulk`, `split_message`
- `protect` — L1 in-memory `FloodGuard` (per-machine budget), L2 Redis `RateLimiter`, L3 `UsageGate`, L4 heuristics
- `tg` — debug commands, keyboards, `media_transfer`, filters
- `dialogs` / `maxbot` — aiogram-dialog и maxo слои
- `forum` — узкий `ForumTopics` + `ThreadStore`
- `testing` — mock DI, db fixtures (`rollback_session`, `savepoint_session`)

## Development

```bash
make install
make docker-up   # Postgres :5499, Redis :6399
make check
```

Module maturity: [PACKAGE_STATUS.md](PACKAGE_STATUS.md).
