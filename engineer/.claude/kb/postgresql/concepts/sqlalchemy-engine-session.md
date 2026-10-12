# SQLAlchemy Engine, Pool and Session (sync + async)

> **Purpose**: Engine/pool/session setup for PostgreSQL with SQLAlchemy 2.x, sync and asyncio
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

SQLAlchemy 2.1.1 is the current stable release; 2.0 is in maintenance (docs.sqlalchemy.org).
The code below is valid on both. 2.1 needs Python 3.11+, makes psycopg 3 the default driver for
plain `postgresql://` URLs, and no longer installs greenlet by default, so async users must
install the `[asyncio]` extra (e.g. `pip install "sqlalchemy[asyncio]" psycopg[binary]`).

## The Concept

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

class Base(AsyncAttrs, DeclarativeBase): ...

class Company(Base):
    __tablename__ = "company"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]                      # NOT NULL (non-Optional)
    note: Mapped[str | None]               # NULL

# --- sync ---
engine = create_engine("postgresql+psycopg://u:p@host/db", pool_pre_ping=True)
Session = sessionmaker(engine)
with Session.begin() as s:                 # commit on exit, rollback on exception
    s.add(Company(name="Acme"))

# --- async ---
aengine = create_async_engine("postgresql+psycopg_async://u:p@host/db", pool_pre_ping=True)
ASession = async_sessionmaker(aengine, expire_on_commit=False)
async def create(name: str) -> None:
    async with ASession.begin() as s:
        s.add(Company(name=name))
# on shutdown:  await aengine.dispose()
```

## Quick Reference

| Topic | Fact |
|-------|------|
| URL forms | `postgresql+psycopg://`, `postgresql+psycopg_async://`, `postgresql+asyncpg://`, `postgresql+psycopg2://` |
| Pool default | `QueuePool`: `pool_size=5`, `max_overflow=10`, `timeout=30`; connections created lazily |
| Async pool | `create_async_engine` uses `AsyncAdaptedQueuePool` (plain `QueuePool` is not asyncio-compatible) |
| Stale connections | `pool_pre_ping=True` emits a ping on checkout; `pool_recycle=N` replaces old connections |
| Forking | call `engine.dispose(close=False)` in the child process |
| Transactions | `Session.begin()` context manager, or commit-as-you-go with `commit()`/`rollback()` |
| Savepoint | `session.begin_nested()`; rollback keeps outer work (handy for `IntegrityError`) |
| Isolation | engine `isolation_level="REPEATABLE READ"` or `session.connection(execution_options={"isolation_level": "SERIALIZABLE"})` |
| Test isolation | `Session(bind=conn, join_transaction_mode="create_savepoint")` inside an outer transaction rolled back at teardown |
| Bulk | `session.execute(insert(Model).returning(Model), [dict, ...])`; bulk update by PK via `update(Model)` + list of dicts |
| Mutable JSON | in-place `obj.data["k"] = v` is not detected; use `MutableDict.as_mutable(JSONB)` or reassign |

## Async rules (docs.sqlalchemy.org asyncio extension)

- One `AsyncSession` per task: a single instance is not safe for concurrent tasks.
- `expire_on_commit=False` so attributes stay readable after commit without implicit I/O.
- Avoid implicit lazy loads: `selectinload(...)`, `AsyncAttrs.awaitable_attrs`, or `run_sync`.
- Attach event listeners to `.sync_engine` / `.sync_session`.
- Always `await engine.dispose()` on shutdown.

## Common Mistakes

### Wrong

```python
async with ASession() as s:          # shared across gather()ed tasks
    await asyncio.gather(job(s), job(s))
```

### Correct

```python
async def job():
    async with ASession.begin() as s:   # one session per task
        ...
await asyncio.gather(job(), job())
```

Also wrong: sizing `pool_size` x worker processes beyond the database `max_connections`
(budget connections per process; see [rds-specifics](rds-specifics.md)).

## Related

- [Alembic migrations](alembic-migrations.md)
- [Transactions and constraints](transactions-and-constraints.md)
- [Idempotent writes](../patterns/idempotent-writes.md)
- [pydantic KB](../../pydantic/index.md), [python KB](../../python/index.md)

## Sources

- https://docs.sqlalchemy.org/en/21/changelog/migration_21.html
- https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- https://docs.sqlalchemy.org/en/20/core/pooling.html
- https://docs.sqlalchemy.org/en/20/orm/session_transaction.html
- https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html
- https://docs.sqlalchemy.org/en/20/orm/extensions/mutable.html
- https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
