# Row-Level Security and Privileges

> **Purpose**: Tenant/row isolation with RLS policies, plus table privileges as a second layer
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

With RLS enabled, a table denies all access to non-exempt roles unless a policy allows it.
Superusers and roles with `BYPASSRLS` always bypass; the table owner bypasses unless the table is
`FORCE`d. So the application must connect as a role that is neither owner nor superuser.

## The Concept

```sql
ALTER TABLE document ENABLE ROW LEVEL SECURITY;
ALTER TABLE document FORCE ROW LEVEL SECURITY;   -- owner also subject to policies

CREATE POLICY tenant_isolation ON document
    USING      (company_id = NULLIF(current_setting('app.company_id', true), '')::bigint)
    WITH CHECK (company_id = NULLIF(current_setting('app.company_id', true), '')::bigint);
```

Set the tenant per transaction from the app (transaction-local, so it cannot leak across pooled
connections):

```python
from sqlalchemy import text
async with ASession.begin() as s:
    await s.execute(text("SELECT set_config('app.company_id', :cid, true)"), {"cid": str(company_id)})
    rows = (await s.scalars(select(Document))).all()
```

## Quick Reference

| Rule | Detail |
|------|--------|
| Default | RLS on + no policy = deny all |
| `USING` | Which existing rows are visible / targetable |
| `WITH CHECK` | Which new/updated rows are allowed; defaults to the `USING` expression |
| Combination | Permissive policies OR together (default); `AS RESTRICTIVE` ANDs |
| `current_setting(name, true)` | Returns NULL instead of error if the setting does not exist. Practitioner note (not in docs): on a pooled connection that earlier used `set_config(..., true)` it can read back as `''`, so the `::bigint` cast errors; use `NULLIF(current_setting(...), '')` |
| `set_config(name, value, true)` | `is_local=true` applies only to the current transaction; `false` = rest of session |
| Debug | `SET row_security = off` errors if RLS would filter results |

## Caveats (PostgreSQL docs)

- Referential-integrity checks bypass RLS, which can leak existence through FK errors.
- The planner may run leakproof functions before policy checks.
- Policies with sub-SELECTs can race with concurrent changes; use locking where it matters.
- Practitioner note: RLS adds per-query predicates, so index the policy column (e.g. `company_id`)
  and test plans with `EXPLAIN`.

## Privileges as a second layer

Table privileges: `SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER, MAINTAIN`. Owners
have all by default but may revoke their own. Use separate roles for migrations (owner) and
runtime (least privilege):

```sql
CREATE ROLE app_rw LOGIN;
GRANT SELECT, INSERT, UPDATE ON document TO app_rw;     -- no DELETE
```

## Common Mistakes

### Wrong

```python
await s.execute(text("SET app.company_id = '42'"))   # session-wide; survives on a pooled connection
```

### Correct

```python
await s.execute(text("SELECT set_config('app.company_id', '42', true)"))   # transaction-local
```

## Related

- [Audit trail (append-only)](../patterns/audit-trail-append-only.md)
- [SQLAlchemy engine/session](sqlalchemy-engine-session.md)

## Sources

- https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- https://www.postgresql.org/docs/current/functions-admin.html
- https://www.postgresql.org/docs/current/sql-grant.html
