# FastAPI Quick Reference

> Fast lookup tables. For code examples, see linked files. Validated 2026-10-02 against FastAPI 0.142.2.

## Core API

| Need | Use | Notes |
|------|-----|-------|
| Group routes | `APIRouter(prefix, tags, dependencies, responses)` | `app.include_router(r)` |
| Inject | `Annotated[T, Depends(fn)]` | `use_cache=True` default |
| Cleanup per request | `yield` dependency | Default exit after response; `scope="function"` = before |
| Startup/shutdown | `FastAPI(lifespan=cm)` | `on_event` deprecated, ignored if lifespan set |
| Response filtering | `-> Out` or `response_model=Out` | `response_model` wins |
| ORM -> schema | `ConfigDict(from_attributes=True)` | |
| Partial update | `model_dump(exclude_unset=True)` | |
| Config | `BaseSettings` + `@lru_cache` dependency | `env_prefix`, `env_file`, `SecretStr` |
| Error | `raise HTTPException(status, detail, headers)` | custom: `@app.exception_handler` |
| Test override | `app.dependency_overrides[fn] = stub` | reset with `= {}` |

## Execution model

| Declared as | Runs |
|-------------|------|
| `async def` | On event loop; never block |
| `def` | In threadpool |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Tiny same-process follow-up | `BackgroundTasks` |
| Heavy/durable/retried work | Job queue worker (procrastinate, Celery) |
| Sync test of routes | `TestClient` |
| Async test with awaits | `AsyncClient(transport=ASGITransport(app=app))` + `pytest.mark.anyio` |
| Lifespan in async tests | `asgi-lifespan` `LifespanManager` |
| Missing bearer header -> own error shape | `HTTPBearer(auto_error=False)` + explicit 401 |
| External IdP tokens | `PyJWKClient` + `jwt.decode(algorithms=[...], issuer=...)` |
| Typed frontend client | `npx @hey-api/openapi-ts -i openapi.json -o src/client` |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Swallow exceptions in yield deps | `raise` after logging |
| Share one `AsyncSession` across concurrent tasks | One session per task/request |
| Leave `expire_on_commit=True` with AsyncSession | `async_sessionmaker(engine, expire_on_commit=False)` |
| Lazy-load relationships in async | `selectinload`, `awaitable_attrs`, `run_sync` |
| Blocking calls in `async def` | Use `def` or an async library |
| Echo input models as responses | Separate In/Out models |
| Trust token without iss/exp/client checks | Verify signature, `iss`, `exp`, `client_id`/`aud`, `token_use` |
| Rely on route-less tags with custom unique-id | Tag every route when id uses `route.tags[0]` |

## Related Documentation

| Topic | Path |
|-------|------|
| Getting Started | `concepts/routers-and-app-structure.md` |
| Auth | `patterns/jwt-jwks-auth.md` |
| Full Index | `index.md` |
