# Idempotent Writes (idempotency keys + unique constraints)

> **Purpose**: Make retried requests/jobs safe by letting a unique constraint arbitrate duplicates
> **MCP Validated**: 2026-10-02

## When to Use

- Client or worker retries (HTTP retries, job retries, at-least-once delivery)
- Webhook/event handlers that may receive the same event twice
- Creating a resource exactly once per natural key

## Implementation

```sql
CREATE TABLE idempotency_key (
    key          text PRIMARY KEY,
    request_hash text NOT NULL,
    response     jsonb,                      -- stored result, replayed on duplicates
    created_at   timestamptz NOT NULL DEFAULT now()
);
```

```python
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

async def run_once(session, key: str, request_hash: str, work):
    """Call inside ONE transaction: claim key, do work, store response, commit."""
    claimed = await session.scalar(
        pg_insert(IdempotencyKey)
        .values(key=key, request_hash=request_hash)
        .on_conflict_do_nothing(index_elements=[IdempotencyKey.key])
        .returning(IdempotencyKey.key)
    )
    if claimed is None:                      # DO NOTHING returns no row -> key already exists
        row = await session.scalar(select(IdempotencyKey).where(IdempotencyKey.key == key))
        if row.request_hash != request_hash:
            raise ValueError("idempotency key reused with different payload")
        return row.response                  # may be None if the first attempt is still running
    result = await work()
    await session.execute(
        update(IdempotencyKey).where(IdempotencyKey.key == key).values(response=result)
    )
    return result
```

Because claim, work and response share one transaction, a crash rolls the claim back and a retry
starts clean. The caller commits (`async with ASession.begin()`).

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `ON CONFLICT DO NOTHING` target | optional | Without a target all unique violations are ignored; name the index for precision |
| `RETURNING` on conflict | no row | Documented PostgreSQL behavior; use it to detect "already existed" |
| `UNIQUE ... NULLS NOT DISTINCT` | NULLs distinct (PG 15+ option) | Use when a nullable column is part of the natural key |
| Isolation | Read Committed | Fine for this pattern; the unique index is the arbiter |

## Example Usage

```python
async with ASession.begin() as s:
    out = await run_once(s, key=request.headers["Idempotency-Key"], request_hash=h, work=create_case)
```

Natural-key variant: `UNIQUE (company_id, external_id)` and
`pg_insert(Case).values(...).on_conflict_do_update(index_elements=[...], set_={...})` for upsert.

Practitioner note (not verified in the PostgreSQL pages fetched): a concurrent second insert of the
same key is expected to wait for the first transaction to finish, then see the conflict. Keep these
transactions short, and set `lock_timeout` per session to bound the wait.

## See Also

- [Transactions and constraints](../concepts/transactions-and-constraints.md)
- [Transactional enqueue](transactional-enqueue.md)

## Sources

- https://www.postgresql.org/docs/current/sql-insert.html
- https://www.postgresql.org/docs/current/ddl-constraints.html
- https://www.postgresql.org/docs/current/runtime-config-client.html
- https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
