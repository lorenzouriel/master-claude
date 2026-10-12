# Lifespan and Async Execution

> **Purpose**: App startup/shutdown with `lifespan`, and how `def` vs `async def` execute
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

Resources shared by all requests (DB engine, HTTP clients, job-queue connection) are created before
`yield` in a `lifespan` async context manager and released after it. `@app.on_event` is deprecated.

## The Concept

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(settings.database_url)
    app.state.engine = engine
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
    yield                       # app serves requests here
    await engine.dispose()      # shutdown

app = FastAPI(lifespan=lifespan)

def get_factory(request: Request):
    return request.app.state.session_factory
```

The FastAPI events page shows module-level globals and only mentions that Starlette supports
"lifespan state". `app.state` here is a practitioner choice (Starlette's generic holder), not
something the FastAPI page documents; a module-level factory also works.

## Quick Reference

| Fact | Detail |
|------|--------|
| Before `yield` | Startup |
| After `yield` | Shutdown |
| `on_event("startup"/"shutdown")` | Deprecated; NOT called if `lifespan=` is set (all or nothing) |
| Sub-applications (mounts) | Their lifespan is not run; only the main app's |
| `async def` endpoint/dependency | Run directly on the event loop |
| `def` endpoint/dependency | Run in an external threadpool |
| Blocking I/O in `async def` | Blocks the loop for all requests; use `def` or an async library |

## Test caveat

httpx `AsyncClient` does not trigger lifespan events (documented); wrap the app with
`asgi-lifespan`'s `LifespanManager`. See [testing-overrides](../patterns/testing-overrides.md).

## Common Mistakes

### Wrong

```python
@app.on_event("startup")           # deprecated
async def startup(): ...
app = FastAPI(lifespan=lifespan)   # the above handler now never runs
```

### Correct

```python
app = FastAPI(lifespan=lifespan)   # all startup/shutdown logic in one place
```

## Related

- [async-sqlalchemy-session](../patterns/async-sqlalchemy-session.md)
- [background-jobs-queue](../patterns/background-jobs-queue.md)
- [python context-managers](../../python/concepts/context-managers.md)

## Sources

- https://fastapi.tiangolo.com/advanced/events/
- https://fastapi.tiangolo.com/async/
- https://fastapi.tiangolo.com/advanced/async-tests/
