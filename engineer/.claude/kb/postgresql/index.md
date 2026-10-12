# PostgreSQL Knowledge Base

> **Purpose**: PostgreSQL 18 as an application database on Amazon RDS: SQLAlchemy 2.x, Alembic, indexing, transactions, RLS, JSONB, audit trails, RDS operations, and procrastinate job queue
> **MCP Validated**: 2026-10-02

Versions checked 2026-10-02: PostgreSQL 18.6 (latest major), SQLAlchemy 2.1.1 (2.0 maintenance),
Alembic 1.20.0, procrastinate 3.10.0 (PyPI), RDS offers PG 18/17/16/15.

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/sqlalchemy-engine-session.md](concepts/sqlalchemy-engine-session.md) | Engine, pool, Session, async rules, drivers |
| [concepts/alembic-migrations.md](concepts/alembic-migrations.md) | Async env.py, autogenerate limits, concurrent index ops |
| [concepts/transactions-and-constraints.md](concepts/transactions-and-constraints.md) | Isolation, 40001 retries, ON CONFLICT, constraints |
| [concepts/indexing-and-explain.md](concepts/indexing-and-explain.md) | Index types, JSONB operators/indexes, reading EXPLAIN |
| [concepts/row-level-security.md](concepts/row-level-security.md) | RLS policies, tenant setting, privileges |
| [concepts/rds-specifics.md](concepts/rds-specifics.md) | Encryption, TLS, parameter groups, backups/PITR, connection budget |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/idempotent-writes.md](patterns/idempotent-writes.md) | Idempotency keys and unique constraints |
| [patterns/zero-downtime-migrations.md](patterns/zero-downtime-migrations.md) | Expand/contract, NOT VALID, concurrent indexes |
| [patterns/audit-trail-append-only.md](patterns/audit-trail-append-only.md) | Audit table, capture triggers, append-only enforcement |
| [patterns/procrastinate-tasks-and-workers.md](patterns/procrastinate-tasks-and-workers.md) | Tasks, workers, retries, periodic, locks, stalled jobs |
| [patterns/transactional-enqueue.md](patterns/transactional-enqueue.md) | Enqueue jobs in the same transaction as data writes |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Read Committed** | Default isolation; per-statement snapshots; RR/Serializable need `40001` retry |
| **ON CONFLICT** | Atomic upsert / dedupe; DO NOTHING returns no row on conflict |
| **NOT VALID + VALIDATE** | Add constraints with light locking |
| **CONCURRENTLY** | Non-blocking index build; outside a transaction |
| **RLS** | Default-deny policies; owner bypasses unless FORCE |
| **jsonb** | Binary JSON, GIN-indexable; `jsonb_path_ops` smaller but no `?` |
| **procrastinate** | Postgres-backed queue; `configure(connection=...)` for transactional enqueue |

Scope fence: generic technical knowledge only. FastAPI routing, SQL Server, and cross-dialect
analytics SQL ([sql-patterns](../sql-patterns/index.md)) are out of scope; schema design lives in
[data-modeling](../data-modeling/index.md).

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/sqlalchemy-engine-session.md, concepts/transactions-and-constraints.md |
| **Intermediate** | concepts/alembic-migrations.md, concepts/indexing-and-explain.md, patterns/idempotent-writes.md |
| **Advanced** | patterns/zero-downtime-migrations.md, patterns/audit-trail-append-only.md, patterns/transactional-enqueue.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| fastapi-backend-specialist | concepts/sqlalchemy-engine-session.md, concepts/transactions-and-constraints.md, patterns/idempotent-writes.md, patterns/transactional-enqueue.md | Sessions per request, upserts, retry-safe endpoints, enqueue jobs atomically |
| fastapi-backend-specialist | concepts/alembic-migrations.md, patterns/zero-downtime-migrations.md, patterns/procrastinate-tasks-and-workers.md | Write migrations, define background tasks and workers |
| fastapi-backend-specialist | concepts/row-level-security.md, patterns/audit-trail-append-only.md | Tenant isolation and audit trail design |
| aws-app-platform-specialist | concepts/rds-specifics.md | RDS encryption, TLS, parameter groups, backups/PITR, connection limits |
| aws-app-platform-specialist | patterns/procrastinate-tasks-and-workers.md | Worker process deployment, shutdown, connection budget |
| react-frontend-specialist | quick-reference.md | Only to understand API retry/idempotency semantics (read-only context) |

Related domains: [pydantic](../pydantic/index.md), [python](../python/index.md),
[testing](../testing/index.md), [aws](../aws/index.md), [terraform](../terraform/index.md).

Sources: see the "Sources" footer of each file; research notes list every claim with its URL.
