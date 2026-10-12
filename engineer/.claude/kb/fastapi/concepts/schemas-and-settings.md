# Schemas and Settings

> **Purpose**: Pydantic v2 request/response models and pydantic-settings configuration in FastAPI
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

FastAPI validates request bodies with Pydantic models, and filters/validates responses through the
return annotation or `response_model`. Keep separate Create/Update/Out models so persistence-only or
sensitive fields never reach the client. Configuration lives in a `BaseSettings` subclass exposed
through a cached dependency. See the [pydantic KB](../../pydantic/index.md) for model basics.

## The Concept

```python
from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel, ConfigDict, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class CasoBase(BaseModel):
    titulo: str

class CasoCreate(CasoBase): ...

class CasoUpdate(BaseModel):                 # PATCH: everything optional
    titulo: str | None = None

class CasoOut(CasoBase):
    model_config = ConfigDict(from_attributes=True)   # build from ORM objects
    id: int

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")
    database_url: str
    jwt_issuer: str
    secret_key: SecretStr

@lru_cache
def get_settings() -> Settings:
    return Settings()

SettingsDep = Annotated[Settings, Depends(get_settings)]
```

PATCH body: `data = payload.model_dump(exclude_unset=True)` applies only fields the client sent.

## Quick Reference

| Need | Use | Notes |
|------|-----|-------|
| Response type | `-> CasoOut` annotation or `response_model=` | `response_model` wins if both given |
| Hide fields | Output model without them, or a base-class return annotation | Filtering is automatic |
| ORM object -> model | `ConfigDict(from_attributes=True)` / `model_validate(obj)` | Pydantic v2 name |
| Omit unset defaults | `response_model_exclude_unset=True` | Also `_include` / `_exclude` sets |
| Env prefix | `env_prefix="APP_"` | `database_url` reads `APP_DATABASE_URL` |
| Nested env | `env_nested_delimiter="__"` | `A__B=1` -> `{"a": {"b": "1"}}` |
| `.env` file | `env_file=".env"` | FastAPI docs say install python-dotenv |
| Secrets | `SecretStr` | Masked in repr/logs |

Settings facts (pydantic-settings docs): env var names are case-insensitive by default; the documented
priority is init args > env vars > dotenv > secrets_dir > defaults (a summary; the full docs list more
sources); with dotenv the default is `extra="forbid"`, so unmatched `.env` keys raise a validation
error (set `extra="ignore"` if that is not wanted). `@lru_cache` makes `Settings()` load once; tests
override via `app.dependency_overrides[get_settings]`.

## Common Mistakes

### Wrong

```python
@app.post("/users")
async def create(user: UserIn) -> UserIn:   # echoes the password back
    return user
```

### Correct

```python
@app.post("/users")
async def create(user: UserIn) -> UserOut:  # or response_model=UserOut with -> Any
    ...
```

## Related

- [dependency-injection](dependency-injection.md)
- [pydantic base-model](../../pydantic/concepts/base-model.md)
- [testing-overrides](../patterns/testing-overrides.md)

## Sources

- https://fastapi.tiangolo.com/tutorial/response-model/
- https://fastapi.tiangolo.com/advanced/settings/
- https://fastapi.tiangolo.com/tutorial/sql-databases/ (PATCH with exclude_unset)
- https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
- https://pydantic.dev/docs/validation/latest/concepts/models/ (from_attributes)
