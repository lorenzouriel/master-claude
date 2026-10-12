# PostgreSQL Quick Reference

> Fast lookup tables. For code examples, see linked files. MCP Validated: 2026-10-02

## Versions (checked 2026-10-02)

| Component | Version | Note |
|-----------|---------|------|
| PostgreSQL | 18.6 latest major | 14 EOL 2026-11-12; RDS offers 18/17/16/15 |
| SQLAlchemy | 2.1.1 stable; 2.0 maintenance | 2.1: Python 3.11+, psycopg3 default, `[asyncio]` extra for greenlet |
| Alembic | 1.20.0 | Python 3.10+, SQLAlchemy 2.0+; pin major.minor |
| procrastinate | 3.10.0 (PyPI) | Python 3.10+, PostgreSQL 13+, `psycopg[pool]` |

## Driver URLs

| Use | URL |
|-----|-----|
| sync psycopg3 | `postgresql+psycopg://` |
| async psycopg3 | `postgresql+psycopg_async://` |
| async asyncpg | `postgresql+asyncpg://` |
| legacy | `postgresql+psycopg2://` |

## Defaults to remember

| Item | Default |
|------|---------|
| Isolation | Read Committed |
| `QueuePool` | size 5, overflow 10, timeout 30 s |
| `lock_timeout` / `statement_timeout` | 0 (off); set per session/role |
| `rds.force_ssl` | 1 on PG 15+ |
| RDS backup retention | 0-35 days (console 7, CLI/API 1) |
| PITR log upload | every 5 min; restore = new instance |
| procrastinate worker `concurrency` | 1; `listen_notify` True; `delete_jobs` "never" |

## Locking cheat sheet

| DDL | Lock / cost |
|-----|-------------|
| `ADD COLUMN ... DEFAULT <non-volatile>` | metadata only |
| volatile default / identity / stored generated | table rewrite |
| `ADD CONSTRAINT ... NOT VALID` | skips scan |
| `VALIDATE CONSTRAINT` | SHARE UPDATE EXCLUSIVE |
| `ADD FOREIGN KEY` | SHARE ROW EXCLUSIVE |
| other `ADD constraint` | ACCESS EXCLUSIVE |
| `SET NOT NULL` | scan, unless a valid CHECK proves it |
| `CREATE INDEX CONCURRENTLY` | outside txn; failure leaves INVALID index |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Dedupe retried writes | unique index + `ON CONFLICT DO NOTHING RETURNING` |
| Upsert | `ON CONFLICT (target) DO UPDATE ... EXCLUDED` |
| Filter JSONB containment only | GIN `jsonb_path_ops` |
| JSONB key existence (`?`) | GIN default `jsonb_ops` |
| Tenant isolation | RLS + `set_config('app.x', v, true)` per txn |
| Immutable audit | trigger block on UPDATE/DELETE/TRUNCATE + `GRANT INSERT, SELECT` only |
| Job + data atomic | `task.configure(connection=conn).defer()` |
| Prevent duplicate queued job | `queueing_lock` (catch `AlreadyEnqueued`) |
| Serialize jobs per entity | `lock="entity-id"` |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Trust autogenerate blindly | Review; renames appear as drop+add; name all constraints |
| `create_index(postgresql_concurrently=True)` in a txn | wrap in `op.get_context().autocommit_block()` |
| Share an `AsyncSession` across tasks | one session per task, `expire_on_commit=False` |
| `SET app.x` on pooled connections | `set_config(..., true)` (transaction-local) |
| `EXPLAIN ANALYZE` on DML directly | `BEGIN; EXPLAIN ANALYZE ...; ROLLBACK;` |
| Check-then-insert | unique constraint + `ON CONFLICT` |
| Disable autovacuum on RDS | leave on; tune parameters |
| Run app as table owner with RLS | non-owner role (or `FORCE ROW LEVEL SECURITY`) |
| Defer job via pool inside a request txn | `configure(connection=...)` on the same txn |

## Related Documentation

| Topic | Path |
|-------|------|
| Getting Started | `concepts/sqlalchemy-engine-session.md` |
| Full Index | `index.md` |
| Cross-dialect SQL | `../sql-patterns/index.md` |
