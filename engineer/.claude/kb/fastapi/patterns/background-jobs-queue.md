# Background Jobs: Queue Instead of BackgroundTasks

> **Purpose**: Hand long or critical work to a durable job queue (procrastinate shown) from FastAPI
> **MCP Validated**: 2026-10-02

## When to Use

- Work is heavy, slow, or must survive a process restart or be retried
- Work can run in another process or host (no shared memory needed)
- `BackgroundTasks` is only suitable for light, same-process follow-ups

## Decision

| Aspect | `BackgroundTasks` | Job queue (procrastinate, Celery, ...) |
|--------|-------------------|----------------------------------------|
| Runs | After the response, in the same process | In separate worker process(es) |
| Fits | Light work, e.g. small notifications | Heavy computation, multi-process/multi-server |
| Infra | None | Queue manager (procrastinate: PostgreSQL 13+; Celery: RabbitMQ/Redis) |
| Durability / retry | Not provided by the docs' description | Provided by the queue library (check its docs) |

The FastAPI docs say to use bigger tools like Celery for heavy background computation when you do not
need the same process; they require a message/job queue manager. Durability/retries of
`BackgroundTasks` are not discussed in the docs; the contrast above is inference.

## Implementation

```python
# app/jobs.py (procrastinate; connector reads PG* env vars or conninfo)
from procrastinate import App, PsycopgConnector
queue = App(connector=PsycopgConnector())

@queue.task(queue="extracao")
async def extrair_documento(documento_id: int) -> None: ...
```

```python
# app/main.py: open the queue app in lifespan so endpoints can defer
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.jobs import queue, extrair_documento

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with queue.open_async():
        yield

app = FastAPI(lifespan=lifespan)

@router.post("/{documento_id}/extrair", status_code=202)
async def start(documento_id: int):
    await extrair_documento.defer_async(documento_id=documento_id)
    return {"status": "queued"}
```

```bash
# worker: separate process/container, same code image
procrastinate --app=app.jobs.queue worker
```

## Configuration

| Item | Value | Source note |
|------|-------|-------------|
| Defer (async) | `await task.defer_async(**kwargs)` | procrastinate docs |
| Defer (sync) | `task.defer(**kwargs)` | Not for use inside a running event loop (practitioner note) |
| Open connection | `async with app.open_async():` | procrastinate docs |
| Worker CLI | `procrastinate --app=dotted.path worker [queue ...]` | worker how-to |
| In-process worker | `run_worker_async(install_signal_handlers=False)` | Docs' lifespan example; prefer a separate worker process for production |
| Requirements | Python 3.10+, PostgreSQL 13+ | procrastinate docs |

## Example Usage

Make job arguments small and JSON-serializable (IDs, not blobs); load data inside the task. Make tasks
idempotent so retries are safe. Return 202 and expose a status endpoint.

Practitioner note: GitHub issue #852 reported event-loop errors deferring from FastAPI with the old
aiopg connector; the current docs use `PsycopgConnector`. Test deferring from a route in your
version. Procrastinate schema migrations (applied with its CLI) and retry/lock settings were not
verified here.

## See Also

- [lifespan-and-async](../concepts/lifespan-and-async.md)
- [aws KB](../../aws/index.md) (SQS alternative in `containers/concepts/sqs-queues.md`)

## Sources

- https://fastapi.tiangolo.com/tutorial/background-tasks/
- https://procrastinate.readthedocs.io/en/stable/
- https://procrastinate.readthedocs.io/en/stable/howto/basics/worker.html
- https://github.com/procrastinate-org/procrastinate/issues/852 (community, practitioner note)
