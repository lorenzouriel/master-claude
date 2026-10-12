# Alembic Migrations

> **Purpose**: Alembic setup, autogenerate limits, async env.py, PostgreSQL-specific op usage
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

Alembic 1.20.0 (docs "latest") supports Python 3.10+ and requires SQLAlchemy 2.0.0 or newer.
Its versioning is not semver: the middle digit can bring breaking changes, so pin major.minor.
PostgreSQL has transactional DDL, but some operations (e.g. `CREATE INDEX CONCURRENTLY`) cannot
run inside a transaction block.

## The Concept

Async-ready `env.py` (bootstrap with `alembic init -t async <dir>`; recipe from the Alembic cookbook):

```python
import asyncio
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())
```

Name every constraint so autogenerate can diff and drop them:

```python
from sqlalchemy import MetaData
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)
```

## Autogenerate: what it does NOT detect

| Not detected | What you must do |
|--------------|------------------|
| Table / column renames (seen as drop + add) | Hand-edit to `op.rename_table` / `op.alter_column(new_column_name=...)` |
| Anonymously named constraints | Give every constraint a name |
| Some constraint changes: PRIMARY KEY, EXCLUDE | Write `op.*` by hand |
| Sequence add/remove | Write by hand |
| Enum-like special types | Review output |

Defaults: `compare_type` is on; `compare_server_default` is off (enable in `context.configure`).
Docs: "autogenerate is not intended to be perfect" - always review candidate migrations.

## PostgreSQL ops

| Need | Use |
|------|-----|
| Index without blocking writes | `with op.get_context().autocommit_block(): op.create_index(..., postgresql_concurrently=True)` |
| Add enum value | `with op.get_context().autocommit_block(): op.execute("ALTER TYPE mood ADD VALUE 'soso'")` |
| Raw SQL (triggers, policies) | `op.execute("...")` (plain string is coerced to `text()`) |
| Check constraint | `op.create_check_constraint(name, table, condition)` |

`autocommit_block()` commits the preceding transaction first, which affects atomicity; the docs
recommend `transaction_per_migration=True` when migrations use it.

## Common Mistakes

### Wrong

```python
op.create_index("ix_doc_company", "document", ["company_id"], postgresql_concurrently=True)
# fails: CREATE INDEX CONCURRENTLY cannot run inside a transaction block
```

### Correct

```python
with op.get_context().autocommit_block():
    op.create_index("ix_doc_company", "document", ["company_id"],
                    postgresql_concurrently=True)
```

## Related

- [Zero-downtime migrations](../patterns/zero-downtime-migrations.md)
- [Indexing and EXPLAIN](indexing-and-explain.md)
- [SQLAlchemy engine/session](sqlalchemy-engine-session.md)

## Sources

- https://alembic.sqlalchemy.org/en/latest/front.html
- https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- https://alembic.sqlalchemy.org/en/latest/cookbook.html
- https://alembic.sqlalchemy.org/en/latest/ops.html
- https://alembic.sqlalchemy.org/en/latest/api/runtime.html
- https://docs.sqlalchemy.org/en/20/core/constraints.html
- https://www.postgresql.org/docs/current/sql-createindex.html
