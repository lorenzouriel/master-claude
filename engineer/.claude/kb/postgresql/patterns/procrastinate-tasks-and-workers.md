# Procrastinate: Tasks, Workers, Retries, Periodic, Locks

> **Purpose**: Run background jobs from PostgreSQL with procrastinate (no separate broker)
> **MCP Validated**: 2026-10-02

## When to Use

- Background work (document extraction, notifications, reports) in an app that already has PostgreSQL
- Jobs that must be enqueued atomically with data writes (see [transactional-enqueue](transactional-enqueue.md))
- Scheduled maintenance via cron-style periodic tasks

Version note: PyPI shows procrastinate 3.10.0 (Python 3.10+); docs say it targets PostgreSQL 13+ and
depends on `psycopg[pool]`. Workers require an async connector.

## Implementation

```python
import procrastinate
from procrastinate import RetryStrategy

app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(conninfo="postgresql://user:pw@host/db"),
    import_paths=["myapp.tasks"],                  # modules the worker imports to register tasks
)

@app.task(queue="extraction",
          retry=RetryStrategy(max_attempts=5, exponential_wait=5, retry_exceptions={ConnectionError}))
async def extract_document(document_id: int) -> None:     # async tasks share one event loop
    ...

@app.task(queue="mail", pass_context=True)                 # JobContext passed as first argument
def send_email(context, to: str) -> None:                  # sync tasks run in their own thread
    if context.should_abort():
        return

@app.periodic(cron="0 4 * * *")                            # decorator goes ABOVE @app.task
@app.task(queueing_lock="nightly_cleanup")
async def nightly_cleanup(timestamp: int) -> None:         # periodic tasks receive `timestamp`
    ...
```

Deferring and opening the app:

```python
async with app.open_async():                               # opens the connector pool
    await extract_document.defer_async(document_id=42)
    await extract_document.configure(lock=f"company-{cid}", schedule_in={"minutes": 5}).defer_async(document_id=43)
```

Operations:

```bash
procrastinate --app=myapp.jobs.app schema --apply          # create tables/functions (no migration tracking)
procrastinate --app=myapp.jobs.app worker --concurrency=10 --queues=extraction,mail
procrastinate --app=myapp.jobs.app worker --no-listen-notify   # saves one connection per worker
```

Stalled jobs (worker killed): detect via heartbeat and requeue with a periodic task:

```python
@app.periodic(cron="*/10 * * * *")
@app.task(queueing_lock="retry_stalled_jobs", pass_context=True)
async def retry_stalled_jobs(context, timestamp):
    for job in await app.job_manager.get_stalled_jobs():
        await app.job_manager.retry_job(job)
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `concurrency` (worker) | 1 | Async jobs in parallel inside one worker; scale CPU-bound work with more worker processes |
| `queues` (worker) | all queues | Pass queue names to restrict |
| `listen_notify` | True | Uses one extra connection per worker; `False` saves it (docs). Practitioner note, not in docs: LISTEN needs a session-level connection, so avoid it behind transaction-pooling proxies |
| `fetch_job_polling_interval` | 5.0 s | Max seconds between DB polls |
| `delete_jobs` | `"never"` | `"always"`, `"successful"`, `"never"`; built-in `remove_old_jobs` task purges old rows |
| `retry` | none | `int` (N retries = N+1 attempts), `True` (indefinite), or `RetryStrategy(max_attempts, wait, linear_wait, exponential_wait, retry_exceptions)` |
| `lock` | none | Jobs with same lock run strictly one at a time, in priority then creation order |
| `queueing_lock` | none | At most one `todo` job per value; second defer raises `AlreadyEnqueued` |
| `shutdown_graceful_timeout` | none | After SIGINT/SIGTERM, running jobs get abort signal after this time; killed jobs become stalled |
| Heartbeat / stalled | 10 s heartbeat; 30 s window | Used by `get_stalled_jobs()` |
| Periodic late limit | 10 min | Missed periodic runs older than this are not deferred (configurable) |

Job statuses: `TODO`, `DOING`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `ABORTED`, `ABORTING` (reference page; prose docs say jobs in `todo`/`doing` state).

## Example Usage

Ignore duplicate deferral instead of failing:

```python
from procrastinate.exceptions import AlreadyEnqueued
try:
    await nightly_cleanup.configure(queueing_lock="x").defer_async(timestamp=0)
except AlreadyEnqueued:
    pass
```

Caveats: a locked job scheduled in the future blocks later jobs with the same lock; a lock whose
oldest job sits in a queue no worker consumes blocks the rest. Periodic tasks only fire while at
least one worker runs. Schema upgrades are manual: SQL files in `procrastinate schema --migrations-path`,
named `{version}_{n}_{pre|post}_name.sql`; track applied ones yourself.

## See Also

- [Transactional enqueue](transactional-enqueue.md)
- [RDS specifics](../concepts/rds-specifics.md) (connection budget)
- [Idempotent writes](idempotent-writes.md) (retries mean at-least-once; make tasks idempotent)

## Sources

- https://procrastinate.readthedocs.io/en/stable/ (home, reference.html)
- https://procrastinate.readthedocs.io/en/stable/howto/basics/tasks.html
- https://procrastinate.readthedocs.io/en/stable/howto/basics/worker.html
- https://procrastinate.readthedocs.io/en/stable/howto/basics/connector.html
- https://procrastinate.readthedocs.io/en/stable/howto/advanced/retry.html
- https://procrastinate.readthedocs.io/en/stable/howto/advanced/locks.html
- https://procrastinate.readthedocs.io/en/stable/howto/advanced/queueing_locks.html
- https://procrastinate.readthedocs.io/en/stable/howto/advanced/cron.html
- https://procrastinate.readthedocs.io/en/stable/howto/advanced/shutdown.html
- https://procrastinate.readthedocs.io/en/stable/howto/production/retry_stalled_jobs.html
- https://procrastinate.readthedocs.io/en/stable/howto/production/delete_finished_jobs.html
- https://procrastinate.readthedocs.io/en/stable/howto/production/connections.html
- https://procrastinate.readthedocs.io/en/stable/howto/production/schema.html
- https://procrastinate.readthedocs.io/en/stable/howto/production/migrations.html
