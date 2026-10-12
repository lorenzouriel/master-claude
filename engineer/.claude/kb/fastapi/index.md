# FastAPI Knowledge Base

> **Purpose**: FastAPI app structure, dependency injection, Pydantic v2 schemas/settings, async SQLAlchemy, external-IdP JWT auth, testing, OpenAPI client generation, job queues
> **MCP Validated**: 2026-10-02 (FastAPI 0.142.2, released 2026-09-30; Python >= 3.10, Pydantic >= 2.9)

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/routers-and-app-structure.md](concepts/routers-and-app-structure.md) | APIRouter per domain module, include_router, layout |
| [concepts/dependency-injection.md](concepts/dependency-injection.md) | Depends, Annotated aliases, yield deps, `scope` |
| [concepts/schemas-and-settings.md](concepts/schemas-and-settings.md) | Request/response models, from_attributes, pydantic-settings |
| [concepts/lifespan-and-async.md](concepts/lifespan-and-async.md) | lifespan, def vs async def, threadpool |
| [concepts/error-handling.md](concepts/error-handling.md) | HTTPException, exception handlers, validation errors |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/async-sqlalchemy-session.md](patterns/async-sqlalchemy-session.md) | AsyncSession per request via yield dependency |
| [patterns/jwt-jwks-auth.md](patterns/jwt-jwks-auth.md) | Verify Cognito-style JWTs via JWKS in a dependency |
| [patterns/testing-overrides.md](patterns/testing-overrides.md) | TestClient, AsyncClient, dependency_overrides |
| [patterns/openapi-ts-client.md](patterns/openapi-ts-client.md) | Operation IDs and TypeScript client generation |
| [patterns/background-jobs-queue.md](patterns/background-jobs-queue.md) | Queue (procrastinate) vs BackgroundTasks |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **APIRouter** | Per-module router with prefix/tags/dependencies, attached via include_router |
| **Depends** | Callable injection; yield deps give per-request setup/cleanup; `scope` controls exit timing |
| **Response model** | Return annotation / `response_model` filters and validates output |
| **Lifespan** | Single async context manager for startup/shutdown resources |
| **dependency_overrides** | Test-time swap of any dependency |
| **Job queue** | Durable out-of-process work, instead of in-process BackgroundTasks |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/routers-and-app-structure.md, concepts/schemas-and-settings.md |
| **Intermediate** | concepts/dependency-injection.md, patterns/async-sqlalchemy-session.md, patterns/testing-overrides.md |
| **Advanced** | patterns/jwt-jwks-auth.md, patterns/background-jobs-queue.md, patterns/openapi-ts-client.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| fastapi-backend-specialist | all concepts, patterns/async-sqlalchemy-session.md, patterns/jwt-jwks-auth.md, patterns/testing-overrides.md | Build and review API modules, auth, DB access, tests |
| react-frontend-specialist | patterns/openapi-ts-client.md, concepts/error-handling.md | Consume the generated TS client; map error shapes |
| aws-app-platform-specialist | patterns/jwt-jwks-auth.md, patterns/background-jobs-queue.md, concepts/schemas-and-settings.md | Cognito settings, worker process deployment, env-based config |

## Related Domains

[pydantic](../pydantic/index.md), [python](../python/index.md), [testing](../testing/index.md),
[aws](../aws/index.md), [sql-patterns](../sql-patterns/index.md), [data-modeling](../data-modeling/index.md),
[javascript](../javascript/index.md), [terraform](../terraform/index.md)

## Sources

- https://fastapi.tiangolo.com/ , https://pypi.org/pypi/fastapi/json , https://pydantic.dev/docs/validation/latest/ , https://docs.sqlalchemy.org/en/20/
