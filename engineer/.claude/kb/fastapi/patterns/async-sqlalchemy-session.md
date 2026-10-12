# Async SQLAlchemy Session per Request

> **Purpose**: One `AsyncSession` per request via a yield dependency, engine owned by lifespan
> **MCP Validated**: 2026-10-02

## When to Use

- Async FastAPI endpoints talking to PostgreSQL through SQLAlchemy 2.0
- You need a single unit of work per request with guaranteed close
- You need to swap the DB in tests via `dependency_overrides`

## Implementation

```python
# app/core/db.py
from collections.abc import AsyncIterator
from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

class Base(AsyncAttrs, DeclarativeBase):      # AsyncAttrs: awaitable_attrs (SQLAlchemy 2.0.13+)
    pass

def make_engine(url: str):
    # postgresql+asyncpg://user:pass@host/db   (or postgresql+psycopg:// for psycopg 3)
    return create_async_engine(url, pool_pre_ping=True)

def make_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)

# lifespan (see lifespan-and-async): app.state.session_factory = make_session_factory(engine)

async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.session_factory() as session:   # closes on exit
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
```

```python
# service / endpoint: explicit transaction boundary, eager loading
from sqlalchemy import select
from sqlalchemy.orm import selectinload

@router.post("/", status_code=201)
async def create(payload: CasoCreate, session: SessionDep) -> CasoOut:
    caso = Caso(**payload.model_dump())
    session.add(caso)
    await session.commit()            # explicit; attributes stay loaded (expire_on_commit=False)
    return caso                       # CasoOut has from_attributes=True

@router.get("/{caso_id}")
async def read(caso_id: int, session: SessionDep) -> CasoOut:
    stmt = select(Caso).options(selectinload(Caso.documentos)).where(Caso.id == caso_id)
    caso = (await session.execute(stmt)).scalar_one_or_none()
    if caso is None:
        raise HTTPException(404, "Caso not found")
    return caso
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `expire_on_commit` | `True` | Set `False` for async: expired attributes would trigger implicit IO after commit |
| `pool_pre_ping` | `False` | Practitioner choice: test connections before use |
| Lazy loading | Not allowed implicitly | Use `selectinload`, `awaitable_attrs`, or `run_sync` |
| Session sharing | n/a | One `AsyncSession` per task; never share across `asyncio.gather` tasks |
| Shutdown | n/a | `await engine.dispose()` in lifespan |

## Example Usage

```python
# Concurrent work needs its own sessions
async def a(factory):
    async with factory() as s: ...
await asyncio.gather(a(factory), a(factory))
```

## Notes

- Alembic, drivers and PgBouncer: asyncpg has a prepared-statement cache and special naming needs
  behind PgBouncer; read the SQLAlchemy asyncpg dialect page before pooling through PgBouncer.
- Do not return ORM objects whose relationships were not loaded and then serialize them: lazy load
  during serialization fails under asyncio.
- Commit location (endpoint/service vs dependency) is a design choice; see the scope note in
  [dependency-injection](../concepts/dependency-injection.md).

## See Also

- [lifespan-and-async](../concepts/lifespan-and-async.md)
- [testing-overrides](testing-overrides.md)
- [sql-patterns](../../sql-patterns/index.md)
- [data-modeling](../../data-modeling/index.md)

## Sources

- https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- https://docs.sqlalchemy.org/en/20/dialects/postgresql.html (asyncpg, psycopg)
- https://fastapi.tiangolo.com/tutorial/sql-databases/ (session-per-request yield dependency)
