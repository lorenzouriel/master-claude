# Indexing, JSONB and EXPLAIN

> **Purpose**: Choose indexes, query JSONB, and read EXPLAIN output
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

PostgreSQL 18 is the current major (18.6); index types are B-tree, hash, GiST, SP-GiST, GIN, BRIN.
Use `EXPLAIN` to compare estimated vs actual rows rather than trusting cost numbers, which are
arbitrary planner units, not milliseconds.

## The Concept

```sql
CREATE INDEX ix_case_company_status ON case_file (company_id, status);          -- B-tree
CREATE INDEX ix_open_cases ON case_file (company_id) WHERE closed_at IS NULL;   -- partial
CREATE UNIQUE INDEX ux_doc ON document (company_id, hash) INCLUDE (name);       -- covering (B-tree/GiST/SP-GiST)
CREATE INDEX ix_payload ON extraction USING GIN (payload jsonb_path_ops);       -- JSONB containment

BEGIN; EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...; ROLLBACK;           -- safe for DML
```

SQLAlchemy equivalents: `Index("ix", col, postgresql_where=..., postgresql_using="gin",
postgresql_include=[...], postgresql_concurrently=True)`.

## JSONB

| Topic | Fact |
|-------|------|
| Choice | Prefer `jsonb` over `json` unless you need key order/duplicates/whitespace preserved |
| `jsonb` storage | Drops whitespace and key order; keeps last value of duplicate keys; indexable |
| `jsonb_ops` GIN (default) | Supports `?`, `?\|`, `?&`, `@>`, `@?`, `@@`; larger |
| `jsonb_path_ops` GIN | Only `@>`, `@?`, `@@`; usually smaller/faster; cannot test key existence |
| Operators | `@>` containment, `?` key exists (keys/top-level elements only), `@?`/`@@` jsonpath |
| Subscripting | `col['a']['b']`; `UPDATE t SET col['k'] = '"v"'` |
| Expression index | `GIN ((payload -> 'tags'))` serves `payload -> 'tags' ? 'x'` |
| SQLAlchemy | `JSONB` type with `.contains()`, `.has_key()`, `.path_exists()`; wrap in `MutableDict` for in-place edits |

Guideline: keep fields you filter/join/constrain on as real columns; use JSONB for variable payloads.

## Reading EXPLAIN

| Item | Meaning |
|------|---------|
| `cost=a..b rows=r width=w` | startup..total cost, estimated rows, avg row bytes |
| `actual time rows loops` | Real per-loop values (ANALYZE); multiply by loops |
| `Index Cond` vs `Filter` | Index Cond narrows via the index; Filter discards after fetch (`Rows Removed by Filter`) |
| `Index Only Scan` | Needs visibility map, which needs VACUUM |
| `Buffers: shared hit/read` | Cache hits vs disk reads; automatic with ANALYZE in PG 18 |
| Seq Scan | Fine for small tables or low selectivity; not automatically a bug |

`EXPLAIN ANALYZE` executes the statement. Stale statistics cause bad estimates: run `ANALYZE`.
Foreign-key referencing columns are not indexed automatically; index them if you delete/join on them.

## Common Mistakes

### Wrong

```sql
CREATE INDEX ix_payload ON extraction USING GIN (payload jsonb_path_ops);
SELECT * FROM extraction WHERE payload ? 'cid';     -- path_ops cannot serve ?
```

### Correct

```sql
CREATE INDEX ix_payload ON extraction USING GIN (payload);   -- default jsonb_ops
SELECT * FROM extraction WHERE payload ? 'cid';
```

## Related

- [Alembic migrations](alembic-migrations.md) (create indexes concurrently)
- [Zero-downtime migrations](../patterns/zero-downtime-migrations.md)
- [sql-patterns KB](../../sql-patterns/index.md)

## Sources

- https://www.postgresql.org/docs/current/sql-createindex.html
- https://www.postgresql.org/docs/current/datatype-json.html
- https://www.postgresql.org/docs/current/sql-explain.html
- https://www.postgresql.org/docs/current/using-explain.html
- https://www.postgresql.org/docs/18/release-18.html
- https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
