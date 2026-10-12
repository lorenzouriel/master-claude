# Transactional Enqueue (outbox via procrastinate)

> **Purpose**: Create a job in the same database transaction as business writes, so both commit or neither does
> **MCP Validated**: 2026-10-02

## When to Use

- "Save the record, then process it in the background" where losing or double-creating the job is unacceptable
- Replacing a separate outbox table + relay process (procrastinate's job table is the outbox)
- Enqueueing from inside a FastAPI request handler that already holds a DB session

## Implementation

`Task.configure(connection=...)` accepts an externally managed connection: "the job INSERT will run
on this connection instead of the connector's pool". Supported connectors and the connection type
each expects (not validated at runtime, so a mismatch fails when called):

| Connector | Connection type |
|-----------|-----------------|
| `PsycopgConnector` (async) | `psycopg.AsyncConnection` |
| `SyncPsycopgConnector` (sync, defer-only) | `psycopg.Connection` |
| `SQLAlchemyPsycopg2Connector` (sync, psycopg2; `procrastinate.contrib.sqlalchemy`) | `sqlalchemy.engine.Connection` |

Async, plain psycopg (shares one transaction for data + job):

```python
import json
import psycopg

async def create_case_and_enqueue(dsn: str, payload: dict) -> int:
    async with await psycopg.AsyncConnection.connect(dsn) as conn:   # commits on clean exit
        async with conn.transaction():
            cur = await conn.execute(
                "INSERT INTO case_file (data) VALUES (%s::jsonb) RETURNING id", (json.dumps(payload),))
            (case_id,) = await cur.fetchone()
            await process_case.configure(connection=conn).defer_async(case_id=case_id)
    return case_id
```

Sync SQLAlchemy (psycopg2 connector; the `engine` must be a psycopg2 engine since the connection is handed to that connector), same transaction as the ORM session's connection:

```python
from sqlalchemy.orm import Session
with Session(engine) as session, session.begin():
    case = Case(...)
    session.add(case)
    session.flush()                                     # get case.id
    process_case.configure(connection=session.connection()).defer(case_id=case.id)
```

Procrastinate's `SQLAlchemyPsycopg2Connector` uses the SQLAlchemy `create_engine` pool (sync only). A
task consumed by a worker still needs an async connector (`PsycopgConnector`) in the worker process;
the web process and worker process may use different connectors for the same database.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `configure(connection=conn)` | none (uses pool) | Run the job INSERT on your connection/transaction |
| NOTIFY timing | on commit | Workers are woken only after your commit; polling (`fetch_job_polling_interval`, 5 s) is the fallback |
| Savepoints | n/a | A failing job INSERT can abort your transaction; wrap in a savepoint (`begin_nested()`) if you must continue |
| `queueing_lock` | none | Combine to dedupe: second `defer` raises `AlreadyEnqueued` (also an INSERT error: use a savepoint) |

## Example Usage

Make the job idempotent too: delivery is at-least-once (retries, stalled-job requeue). Pass IDs, not
payloads; the task re-reads state from the database and uses a unique constraint or
[idempotency key](idempotent-writes.md) for side effects.

Practitioner note (inferred from the documented semantics, not quoted): deferring through the connector's own pool inside a request transaction. The job is
committed independently: if the request later rolls back, the worker may run against rows that do
not exist; if the job commits first, it can run before the data commits.

## See Also

- [Procrastinate tasks and workers](procrastinate-tasks-and-workers.md)
- [Idempotent writes](idempotent-writes.md)
- [SQLAlchemy engine/session](../concepts/sqlalchemy-engine-session.md)

## Sources

- https://procrastinate.readthedocs.io/en/stable/howto/production/external_connection.html
- https://procrastinate.readthedocs.io/en/stable/reference.html
- https://procrastinate.readthedocs.io/en/stable/howto/basics/connector.html
- https://procrastinate.readthedocs.io/en/stable/howto/advanced/sync_defer.html
- https://raw.githubusercontent.com/procrastinate-org/procrastinate/main/procrastinate/contrib/sqlalchemy/psycopg2_connector.py
