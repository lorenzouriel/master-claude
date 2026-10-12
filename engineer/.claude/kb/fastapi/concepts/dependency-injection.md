# Dependency Injection

> **Purpose**: `Depends`, `Annotated` aliases, yield dependencies and their `scope`
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

A dependency is any callable declared with `Depends(...)`. FastAPI resolves sub-dependencies in
order, caches a dependency's result per request (`use_cache=True` default), and for `yield`
dependencies runs the code after `yield` as cleanup. Dependencies are also the seam for testing
via `app.dependency_overrides`.

## The Concept

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException

async def get_session():
    async with SessionLocal() as session:   # see async-sqlalchemy-session pattern
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]   # reusable alias

async def get_caso_or_404(caso_id: int, session: SessionDep) -> Caso:
    caso = await session.get(Caso, caso_id)
    if caso is None:
        raise HTTPException(status_code=404, detail="Caso not found")
    return caso

@app.get("/casos/{caso_id}")
async def read(caso: Annotated[Caso, Depends(get_caso_or_404)]) -> CasoOut:
    return caso
```

## Yield dependency scope

| `Depends(..., scope=)` | Exit code runs | Sub-dependency rule |
|------------------------|----------------|---------------------|
| `"request"` (default for yield deps, per docs) | After the response is sent | Only `"request"` sub-deps |
| `"function"` | Before the response is sent | Either scope |

`Depends` is a frozen dataclass in FastAPI source: `dependency`, `use_cache=True`,
`scope: Literal["function", "request"] | None`. A parent's exit code runs after its children's, and
children's values stay available to it. `scope=` was introduced in FastAPI 0.121.0 (2025-11-03; top-level fix in
0.121.1), so it is available in the validated 0.142.2.

## Exceptions in yield dependencies

| Situation | Behavior |
|-----------|----------|
| `except X: raise` | Correct; error still propagates and is logged |
| `except X:` without re-raise | FastAPI never sees the error; client gets 500, no proper logging |
| `except X as e: raise HTTPException(...)` | Allowed conversion |

## sync vs async dependencies

`def` dependencies run in a threadpool; `async def` are awaited on the event loop. Mixing is fine.
Never call blocking I/O inside `async def`.

## Common Mistakes

### Wrong

```python
async def get_session():
    try:
        yield session
    except Exception:
        log.error("fail")      # swallowed: client sees 500, no traceback
```

### Correct

```python
async def get_session():
    try:
        yield session
    except Exception:
        log.error("fail")
        raise
```

Practitioner note (inference from the documented timing, not stated verbatim): with the default
request scope, cleanup runs after the response is sent, so a failure there (e.g. a commit) cannot
change the status already sent. If the commit must be able to fail the response, commit inside the
endpoint/service or use `scope="function"`.

## Related

- [async-sqlalchemy-session](../patterns/async-sqlalchemy-session.md)
- [jwt-jwks-auth](../patterns/jwt-jwks-auth.md)
- [testing-overrides](../patterns/testing-overrides.md)
- [lifespan-and-async](lifespan-and-async.md)

## Sources

- https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
- https://raw.githubusercontent.com/fastapi/fastapi/master/fastapi/params.py
- https://fastapi.tiangolo.com/release-notes/ (0.121.0 scope)
- https://fastapi.tiangolo.com/async/
- https://fastapi.tiangolo.com/tutorial/bigger-applications/
