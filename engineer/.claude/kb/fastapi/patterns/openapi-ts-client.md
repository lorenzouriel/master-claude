# OpenAPI Schema and TypeScript Client Generation

> **Purpose**: Stable operation IDs and a generated TS client from FastAPI's OpenAPI document
> **MCP Validated**: 2026-10-02

## When to Use

- A TypeScript frontend should consume typed API calls instead of hand-written fetchers
- You want client method names that do not change when paths change
- You need an offline `openapi.json` artifact for CI

## Implementation

```python
# app/main.py: operation_id = "<tag>-<function name>"
from fastapi import FastAPI
from fastapi.routing import APIRoute

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"      # every route MUST have a tag, else IndexError

app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
```

```python
# scripts/export_openapi.py: export without running a server (practitioner note: app.openapi() not verified in this pass)
import json
from app.main import app
open("openapi.json", "w").write(json.dumps(app.openapi()))
```

```bash
# generate (Hey API, the tool the FastAPI docs recommend)
npx @hey-api/openapi-ts -i http://localhost:8000/openapi.json -o src/client
# or from the exported file
npx @hey-api/openapi-ts -i ./openapi.json -o src/client
```

## Configuration

| Item | Value | Notes |
|------|-------|-------|
| OpenAPI version | 3.1 | Per FastAPI client docs |
| Default operationId | verbose, e.g. `createItemItemsPost` | Per docs |
| `generate_unique_id_function` | `Callable[[APIRoute], str]` | Combine tag + name |
| Optional preprocessing | Strip `"{tag}-"` prefix from `operationId` | Docs give Python/Node scripts so the client has `createItem` not `items-create_item` |
| Spec URL | `/openapi.json` | Docs UI served by FastAPI by default |

## Example Usage

Per-route override: `@router.get("/", operation_id="listCasos")`. Annotate every route with a
return type or `response_model` so request and response types appear in the schema (the client's
types come from your Pydantic models). Regenerate the client in CI and fail on diff to catch
drift. Hey API version and plugin options (`@hey-api/openapi-ts` config file) were not verified;
pin the version in `package.json` and read its docs.

Practitioner note: because the tag drives names, keep one tag per router (set at the `APIRouter`).

## See Also

- [routers-and-app-structure](../concepts/routers-and-app-structure.md)
- [schemas-and-settings](../concepts/schemas-and-settings.md)
- [javascript KB](../../javascript/index.md)

## Sources

- https://fastapi.tiangolo.com/advanced/generate-clients/
- https://fastapi.tiangolo.com/tutorial/response-model/
- https://fastapi.tiangolo.com/tutorial/bigger-applications/ (router tags)
