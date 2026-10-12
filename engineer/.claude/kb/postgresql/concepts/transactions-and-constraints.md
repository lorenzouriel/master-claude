# Transactions, Isolation and Constraints

> **Purpose**: Isolation levels, retry rules, upsert semantics, and constraints as the integrity layer
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

PostgreSQL defaults to Read Committed: each statement sees a fresh snapshot of committed data.
Repeatable Read and Serializable can abort with SQLSTATE `40001`; the application must retry the
whole transaction. Constraints (unique, check, foreign key, exclusion) enforce invariants no
matter how many app instances write concurrently.

## The Concept

```sql
-- Atomic insert-or-update (conflict_target required for DO UPDATE)
INSERT INTO plan (code, label) VALUES ('A', 'Alpha')
ON CONFLICT (code) DO UPDATE SET label = EXCLUDED.label
RETURNING id;

-- Insert-if-absent (target optional); RETURNING yields no row on conflict
INSERT INTO event_seen (event_id) VALUES ($1) ON CONFLICT DO NOTHING RETURNING event_id;
```

```python
from sqlalchemy.dialects.postgresql import insert as pg_insert
stmt = pg_insert(Plan).values(code="A", label="Alpha")
stmt = stmt.on_conflict_do_update(index_elements=[Plan.code], set_={"label": stmt.excluded.label})
```

## Isolation

| Level | Behavior (PostgreSQL docs) | App duty |
|-------|----------------------------|----------|
| Read Committed (default) | New snapshot per statement; two SELECTs in one txn can differ | Use constraints / `FOR UPDATE` for invariants |
| Repeatable Read | Snapshot for whole txn; `could not serialize access due to concurrent update` | Retry on `40001` |
| Serializable | As above plus read/write dependency failures | Retry on `40001`, generic handler |
| Read Uncommitted | Behaves exactly like Read Committed | none |

Docs: under Repeatable Read only updating transactions need retry (read-only never conflict). Under Serializable, retry on `40001` for any transaction type.

## Constraints

| Constraint | Notes |
|------------|-------|
| `UNIQUE` | NULLs are distinct by default; `NULLS NOT DISTINCT` (PG 15+) treats them as equal; only B-tree indexes can be unique |
| `CHECK` | Passes when expression is NULL, so add `NOT NULL` separately |
| `FOREIGN KEY` | Default action `NO ACTION`; also `RESTRICT`, `CASCADE`, `SET NULL`; referencing columns are not auto-indexed |
| `EXCLUDE` | `EXCLUDE USING gist (c WITH &&)`; builds an index automatically |
| Partial unique index | `CREATE UNIQUE INDEX ... WHERE deleted_at IS NULL` enforces uniqueness on a subset |

Gotchas: `ON CONFLICT DO UPDATE` raises a cardinality violation if one statement would touch the same
row twice; `MERGE` is the alternative for mixed insert/update/delete. PG 18 adds `OLD`/`NEW` in
`RETURNING` and temporal constraints.

## Common Mistakes

### Wrong

```python
if not await session.scalar(select(Doc).where(Doc.hash == h)):   # check-then-insert race
    session.add(Doc(hash=h))
```

### Correct

```python
await session.execute(pg_insert(Doc).values(hash=h).on_conflict_do_nothing(index_elements=[Doc.hash]))
```

## Related

- [Idempotent writes](../patterns/idempotent-writes.md)
- [SQLAlchemy engine/session](sqlalchemy-engine-session.md)
- [data-modeling KB](../../data-modeling/index.md)

## Sources

- https://www.postgresql.org/docs/current/transaction-iso.html
- https://www.postgresql.org/docs/current/sql-insert.html
- https://www.postgresql.org/docs/current/ddl-constraints.html
- https://www.postgresql.org/docs/current/indexes-unique.html
- https://www.postgresql.org/docs/18/release-18.html
- https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
