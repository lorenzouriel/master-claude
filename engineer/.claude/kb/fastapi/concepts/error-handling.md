# Error Handling

> **Purpose**: `HTTPException`, custom exception handlers, and overriding validation errors
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

Raise `HTTPException` to stop a request with a status code; register `@app.exception_handler` for
domain exceptions so services stay HTTP-agnostic. Request validation failures raise
`RequestValidationError`, which has its own overridable handler.

## The Concept

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import JSONResponse

class DomainError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code, self.message, self.status = code, message, status

app = FastAPI()

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status,
                        content={"error": {"code": exc.code, "message": exc.message}})

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    log.info("invalid request: %s", exc.errors())      # keep default response shape
    return await request_validation_exception_handler(request, exc)

# inside an endpoint:
raise HTTPException(status_code=404, detail="Not found", headers={"X-Error": "x"})
```

## Quick Reference

| Item | Behavior |
|------|----------|
| `HTTPException(status_code, detail, headers)` | `raise`, never `return`; `detail` may be any JSON-able value |
| FastAPI vs Starlette `HTTPException` | FastAPI's subclasses Starlette's; `detail` any JSON vs string only |
| Catch both | `@app.exception_handler(StarletteHTTPException)` (`from starlette.exceptions import HTTPException`) |
| Validation errors | `RequestValidationError`; `exc.errors()`, `exc.body` available |
| Default handlers | `fastapi.exception_handlers.http_exception_handler`, `request_validation_exception_handler` |
| Default error body | `{"detail": ...}` |
| Handler scope | Docs show app-level `@app.exception_handler`; per-router handlers are not documented there |

## Practitioner notes

- The documented "return the body" validation example echoes the raw payload; do not do that for
  payloads that may contain personal or health data.
- Unhandled non-HTTP exceptions become 500 responses; add a catch-all `Exception` handler only for
  logging or a uniform error shape.

## Common Mistakes

### Wrong

```python
return HTTPException(status_code=404)      # returned, not raised: not an error response
```

### Correct

```python
raise HTTPException(status_code=404, detail="Not found")
```

## Related

- [dependency-injection](dependency-injection.md) (re-raise rule in yield dependencies)
- [pydantic error-handling](../../pydantic/patterns/error-handling.md)

## Sources

- https://fastapi.tiangolo.com/tutorial/handling-errors/
- https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
