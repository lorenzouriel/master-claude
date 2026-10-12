# Routers and App Structure

> **Purpose**: Organize a FastAPI app as one `APIRouter` per domain module, assembled in a single `main.py`
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

`APIRouter` is a "mini FastAPI": it declares path operations in a module and is attached to the app
with `include_router`. Router-level `prefix`, `tags`, `dependencies` and `responses` apply to every
operation in it, so cross-cutting concerns (auth, OpenAPI grouping) are declared once per module.
Current release at validation: FastAPI 0.142.2 (Python >= 3.10, Pydantic >= 2.9, Starlette >= 0.46).

## The Concept

```python
# app/casos/router.py  (one package per domain module)
from typing import Annotated
from fastapi import APIRouter, Depends
from app.auth.deps import require_user          # router-wide dependency

router = APIRouter(
    prefix="/casos",                 # no trailing slash
    tags=["casos"],                  # OpenAPI grouping (also drives client method names)
    dependencies=[Depends(require_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/{caso_id}")
async def get_caso(caso_id: int) -> CasoOut: ...

# app/main.py
from fastapi import FastAPI
from app.casos.router import router as casos_router
from app.empresas.router import router as empresas_router

app = FastAPI(lifespan=lifespan)
app.include_router(casos_router)
app.include_router(empresas_router, prefix="/v1")   # include-time overrides/additions
```

Suggested layout per module: `router.py` (HTTP), `schemas.py` (Pydantic), `service.py` (logic),
`models.py` (ORM), `deps.py` (module dependencies). The official tutorial layout is
`app/main.py`, `app/dependencies.py`, `app/routers/{items,users}.py`.

## Quick Reference

| Feature | Behavior | Notes |
|---------|----------|-------|
| `APIRouter(prefix=, tags=, dependencies=, responses=)` | Applied to all operations | Official tutorial |
| `app.include_router(r, prefix=, tags=, dependencies=)` | Overrides/adds at include time | Reuse a router unchanged |
| `router.include_router(other)` | Nested routers | Works before or after the parent is included |
| `FastAPI(dependencies=[...])` | Global dependencies | All path operations |
| Dependency order | router -> decorator `dependencies=` -> parameters | All evaluated |

## Common Mistakes

### Wrong

```python
# Mutating router.routes after inclusion; mounting routers as if they were sub-apps
router.routes.append(...)
app.mount("/casos", casos_router)   # a router is not an ASGI sub-application
```

### Correct

```python
@router.get("/")            # use decorators and include_router only
app.include_router(casos_router)
```

Routers are "live-included" (not isolated sub-apps): path operations added later to a router are
visible through its earlier inclusion. Per the 0.137.0 release notes, `router.routes` can now contain intermediate tree objects
instead of only `APIRoute`, so do not iterate it expecting a flat list of routes.

Lifespan handlers run only for the main app, not for mounted sub-applications.

## Related

- [dependency-injection](dependency-injection.md)
- [lifespan-and-async](lifespan-and-async.md)
- [openapi-ts-client](../patterns/openapi-ts-client.md)
- [python clean-architecture](../../python/patterns/clean-architecture.md)

## Sources

- https://fastapi.tiangolo.com/tutorial/bigger-applications/
- https://fastapi.tiangolo.com/tutorial/dependencies/global-dependencies/
- https://fastapi.tiangolo.com/advanced/events/
- https://fastapi.tiangolo.com/release-notes/ (0.137.0 router tree note)
- https://pypi.org/pypi/fastapi/json (version/requirements)
