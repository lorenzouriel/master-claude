# Testing with TestClient, AsyncClient and dependency_overrides

> **Purpose**: Test endpoints without real auth, DB or settings by swapping dependencies
> **MCP Validated**: 2026-10-02

## When to Use

- Unit/API tests for routes: sync `TestClient`
- Tests that also `await` async code (DB fixtures, etc.): httpx `AsyncClient`
- Replacing auth, settings, session or external-service dependencies

## Implementation

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.deps import current_claims
from app.core.config import get_settings, Settings
from app.core.db import get_session

@pytest.fixture
def client():
    app.dependency_overrides[current_claims] = lambda: {"sub": "u1", "cognito:groups": ["medicos"]}
    app.dependency_overrides[get_settings] = lambda: Settings(database_url="postgresql+asyncpg://t/t",
                                                              jwt_issuer="https://issuer.test",
                                                              secret_key="x")
    with TestClient(app) as c:              # `with` runs lifespan (FastAPI testing-events docs)
        yield c
    app.dependency_overrides = {}           # documented reset

def test_me(client):
    r = client.get("/me")                   # plain def test, no await
    assert r.status_code == 200
```

```python
# Async variant (documented)
import pytest
from httpx import ASGITransport, AsyncClient

@pytest.mark.anyio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/")
    assert r.status_code == 200
```

```python
# Override a yield dependency with a test session (real test DB, rolled back per test)
async def override_session():
    async with TestSessionFactory() as s:
        yield s
app.dependency_overrides[get_session] = override_session
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `TestClient` | sync, httpx-based | `def` tests, no `await`; install `httpx` |
| `AsyncClient` | needs `ASGITransport(app=app)` | `TestClient` "magic" does not work inside `async def` tests |
| Lifespan with `AsyncClient` | Not triggered | Use `LifespanManager` from `asgi-lifespan` |
| `pytest.mark.anyio` | n/a | Marker used by the official async-tests page |
| `app.dependency_overrides` | `{}` | Key = original callable object; reset by assigning `{}` |

## Example Usage

Overrides apply to dependencies used anywhere (path operations, decorators, router includes) and the
override signature should be compatible with the original. Key by the same function object that
`Depends(...)` references; a wrapper or re-created `lru_cache` function will not match.

Practitioner note: create event-loop-bound objects (engines, clients) inside async fixtures/tests;
the docs warn that otherwise `RuntimeError: Task attached to a different loop` can occur.

## See Also

- [dependency-injection](../concepts/dependency-injection.md)
- [jwt-jwks-auth](jwt-jwks-auth.md)
- [testing KB](../../testing/index.md)

## Sources

- https://fastapi.tiangolo.com/tutorial/testing/
- https://fastapi.tiangolo.com/advanced/async-tests/
- https://fastapi.tiangolo.com/advanced/testing-events/
- https://fastapi.tiangolo.com/advanced/testing-dependencies/
- https://fastapi.tiangolo.com/advanced/settings/
