# Audit Trail (append-only table + triggers)

> **Purpose**: Record who changed what, and make the history tamper-resistant at the database layer
> **MCP Validated**: 2026-10-02

## When to Use

- Regulated or sensitive data where changes must be reconstructable
- Need history that application bugs (or app-role credentials) cannot rewrite
- Capturing changes made outside the ORM (SQL scripts, other services)

## Implementation

```sql
CREATE TABLE audit_log (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    at         timestamptz NOT NULL DEFAULT now(),
    actor      text,                          -- from app.user_id setting
    table_name text NOT NULL,
    op         text NOT NULL,                 -- INSERT / UPDATE / DELETE
    old_row    jsonb,
    new_row    jsonb
);

-- 1. Capture changes
CREATE FUNCTION audit_capture() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO audit_log (actor, table_name, op, old_row, new_row)
  VALUES (current_setting('app.user_id', true), TG_TABLE_NAME, TG_OP,
          CASE WHEN TG_OP <> 'INSERT' THEN to_jsonb(OLD) END,
          CASE WHEN TG_OP <> 'DELETE' THEN to_jsonb(NEW) END);
  RETURN NULL;                                -- AFTER trigger: return value ignored
END $$;

CREATE TRIGGER trg_audit_document
AFTER INSERT OR UPDATE OR DELETE ON document
FOR EACH ROW EXECUTE FUNCTION audit_capture();

-- 2. Make audit_log append-only
CREATE FUNCTION audit_block_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'audit_log is append-only';
END $$;

CREATE TRIGGER trg_audit_log_no_row_mutation
BEFORE UPDATE OR DELETE ON audit_log
FOR EACH ROW EXECUTE FUNCTION audit_block_mutation();

CREATE TRIGGER trg_audit_log_no_truncate
BEFORE TRUNCATE ON audit_log
FOR EACH STATEMENT EXECUTE FUNCTION audit_block_mutation();   -- TRUNCATE triggers must be statement-level

-- 3. Privileges: the runtime role can only add and read
REVOKE ALL ON audit_log FROM PUBLIC;
GRANT INSERT, SELECT ON audit_log TO app_rw;
```

Set the actor once per transaction from the application:

```python
await session.execute(text("SELECT set_config('app.user_id', :u, true)"), {"u": str(user_id)})
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Trigger timing | n/a | AFTER row trigger sees final data; BEFORE row trigger returning NULL skips the operation |
| `FOR EACH ROW` vs `STATEMENT` | STATEMENT | TRUNCATE triggers are statement-level only |
| Firing order | alphabetical | Multiple triggers on one table fire by name |
| `WHEN (OLD.* IS DISTINCT FROM NEW.*)` | none | Skip no-op updates to reduce noise |
| `REFERENCING NEW TABLE AS ...` | none | Transition tables for set-based statement triggers on bulk changes |
| `set_config(..., true)` | session if false | Transaction-local actor, safe with pooling |

## Example Usage

```sql
SELECT at, actor, op, old_row ->> 'status' AS was, new_row ->> 'status' AS now
FROM audit_log WHERE table_name = 'document' AND (new_row ->> 'id')::bigint = 42 ORDER BY id;
```

Limits: owners keep all privileges by default (a table owner can revoke its own rights, but also
regain them), and practitioner knowledge says owners/superusers can disable triggers, so run the
application as a non-owner role and keep migrations on a separate owner role. For stronger
tamper evidence, ship rows to external immutable storage (out of scope here). Partition or archive
`audit_log` by time if it grows large.

## See Also

- [Row-level security and privileges](../concepts/row-level-security.md)
- [Alembic migrations](../concepts/alembic-migrations.md) (create triggers with `op.execute`)

## Sources

- https://www.postgresql.org/docs/current/sql-createtrigger.html
- https://www.postgresql.org/docs/current/sql-grant.html
- https://www.postgresql.org/docs/current/functions-admin.html
- https://www.postgresql.org/docs/current/datatype-json.html
