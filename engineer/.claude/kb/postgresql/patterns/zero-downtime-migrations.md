# Zero-Downtime Migrations (expand / contract)

> **Purpose**: Change a live PostgreSQL schema without long locks or breaking running app versions
> **MCP Validated**: 2026-10-02

## When to Use

- Adding/removing columns, constraints, or indexes on tables that serve traffic
- Renaming or retyping a column while old and new app versions run together
- Any migration that would take `ACCESS EXCLUSIVE` on a large table

## Implementation

Expand/contract is a practitioner discipline; the lock facts below come from the PostgreSQL docs.

```text
1. EXPAND   : add new nullable column / new table / new index (backward compatible)
2. DEPLOY   : app writes both old and new; reads old
3. BACKFILL : batch UPDATE, small transactions
4. DEPLOY   : app reads new
5. CONTRACT : drop old column/constraint in a later release
```

```python
"""Alembic: safe patterns."""
from alembic import op

def upgrade():
    # Bound lock waits so a blocked DDL fails fast instead of queueing everything behind it.
    op.execute("SET LOCAL lock_timeout = '5s'")

    # 1. Non-volatile DEFAULT is metadata-only (no rewrite); volatile default would rewrite the table.
    op.execute("ALTER TABLE document ADD COLUMN status text DEFAULT 'new'")

    # 2. NOT NULL without a long scan: NOT VALID check, then VALIDATE (SHARE UPDATE EXCLUSIVE).
    op.execute("ALTER TABLE document ADD CONSTRAINT ck_doc_company_nn "
               "CHECK (company_id IS NOT NULL) NOT VALID")
    # VALIDATE must run in its own transaction: inside this migration's transaction the ACCESS
    # EXCLUSIVE lock from ADD CONSTRAINT is held until commit, so the scan would block everything.
    with op.get_context().autocommit_block():
        op.execute("ALTER TABLE document VALIDATE CONSTRAINT ck_doc_company_nn")
    op.execute("ALTER TABLE document ALTER COLUMN company_id SET NOT NULL")  # scan skipped: valid CHECK proves it
    op.execute("ALTER TABLE document DROP CONSTRAINT ck_doc_company_nn")

    # 3. Foreign key: NOT VALID first (SHARE ROW EXCLUSIVE), validate separately.
    op.execute("ALTER TABLE document ADD CONSTRAINT fk_doc_company "
               "FOREIGN KEY (company_id) REFERENCES company (id) NOT VALID")
    with op.get_context().autocommit_block():      # same reason: validate outside the DDL transaction
        op.execute("ALTER TABLE document VALIDATE CONSTRAINT fk_doc_company")

    # 4. Index without blocking writes: outside a transaction.
    with op.get_context().autocommit_block():
        op.create_index("ix_doc_company", "document", ["company_id"],
                        postgresql_concurrently=True)
```

Batch backfill (separate script or migration step, one short transaction per batch):

```sql
UPDATE document SET status = 'new'
WHERE id IN (SELECT id FROM document WHERE status IS NULL ORDER BY id LIMIT 5000);
```

## Configuration

| Setting / fact | Default | Description |
|----------------|---------|-------------|
| `lock_timeout` | 0 (off) | Abort statements waiting too long on a lock; docs advise session/role scope, not `postgresql.conf` |
| `statement_timeout` | 0 (off) | Same advice; set per session for migrations |
| `ADD COLUMN ... DEFAULT <non-volatile>` | no rewrite | Volatile default, identity, stored generated column rewrite the table |
| `ALTER COLUMN TYPE` | rewrite | Skipped only when binary-coercible with unchanged contents (indexes may still rebuild); run `ANALYZE` after |
| `CREATE INDEX CONCURRENTLY` | n/a | Two scans, waits on old transactions, failure leaves an INVALID index to drop and retry |
| `transaction_per_migration` | False | Recommended by Alembic docs when using `autocommit_block()` |

## Example Usage

Rename `document.kind` to `document.category`: add `category`, dual-write in app, backfill, switch
reads, then drop `kind` next release. Never use a bare `op.alter_column(new_column_name=...)` while
an older app version still reads the old name.

If a `CREATE INDEX CONCURRENTLY` fails, find INVALID indexes (`pg_index.indisvalid = false`), drop
them, retry.

## See Also

- [Alembic migrations](../concepts/alembic-migrations.md)
- [Indexing and EXPLAIN](../concepts/indexing-and-explain.md)

## Sources

- https://www.postgresql.org/docs/current/sql-altertable.html
- https://www.postgresql.org/docs/current/sql-createindex.html
- https://www.postgresql.org/docs/current/runtime-config-client.html
- https://alembic.sqlalchemy.org/en/latest/api/runtime.html
- https://alembic.sqlalchemy.org/en/latest/autogenerate.html
