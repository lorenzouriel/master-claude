# JWT Bearer Auth with an External IdP (JWKS)

> **Purpose**: Verify access/ID tokens issued by an external IdP (example: Amazon Cognito) in a dependency
> **MCP Validated**: 2026-10-02

## When to Use

- The API trusts tokens minted elsewhere (Cognito user pool) and never issues tokens itself
- You need signature, issuer, expiry and client checks on every request
- You need the user/claims injected into endpoints and overridable in tests

## Implementation

```python
# app/auth/deps.py
from typing import Annotated
import jwt                                    # PyJWT
from jwt import PyJWKClient
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

REGION, POOL_ID, CLIENT_ID = "us-east-1", "us-east-1_EXAMPLE", "exampleclientid"  # from Settings
ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{POOL_ID}"
jwks = PyJWKClient(f"{ISSUER}/.well-known/jwks.json", cache_jwk_set=True, lifespan=300)

bearer = HTTPBearer(auto_error=False)         # we raise our own 401 below

def _unauthorized(msg: str = "Invalid token") -> HTTPException:
    return HTTPException(401, msg, headers={"WWW-Authenticate": "Bearer"})

def current_claims(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict:
    # plain `def`: PyJWKClient does blocking network I/O; FastAPI runs def deps in a threadpool
    if creds is None:
        raise _unauthorized("Not authenticated")
    try:
        key = jwks.get_signing_key_from_jwt(creds.credentials)
        claims = jwt.decode(
            creds.credentials, key.key,
            algorithms=["RS256"],                       # Cognito signs with RS256
            issuer=ISSUER,
            options={"require": ["exp", "iss", "sub"], "verify_aud": False},
            leeway=5,
        )
    except jwt.PyJWTError:                              # covers expired/invalid/JWKS errors
        raise _unauthorized()
    # Access tokens carry client_id (no aud); ID tokens carry aud. Check by token_use.
    if claims.get("token_use") != "access" or claims.get("client_id") != CLIENT_ID:
        raise _unauthorized()
    return claims

Claims = Annotated[dict, Depends(current_claims)]

def require_group(group: str):
    def dep(claims: Claims) -> dict:
        if group not in claims.get("cognito:groups", []):
            raise HTTPException(403, "Forbidden")
        return claims
    return dep
```

## Configuration

| Setting | Value | Source note |
|---------|-------|-------------|
| JWKS URL | `https://cognito-idp.{region}.amazonaws.com/{poolId}/.well-known/jwks.json` | AWS docs |
| `iss` | `https://cognito-idp.{region}.amazonaws.com/{poolId}` | AWS docs |
| Algorithm | `RS256` | AWS docs; pin `algorithms=` explicitly |
| Access token | `client_id` claim, `token_use=access`; no `aud` (without resource-server binding) | AWS docs |
| ID token | `aud` = app client id, `token_use=id` | AWS docs |
| `PyJWKClient` | `cache_jwk_set=True`, `lifespan=300`, `timeout=30`, `cooldown_duration=30` | PyJWT API ref defaults |
| `HTTPBearer(auto_error=True)` | 401 `Not authenticated` + `WWW-Authenticate: Bearer` | FastAPI source/reference |

## Example Usage

```python
@router.get("/me")
def me(claims: Claims): return {"sub": claims["sub"]}

router = APIRouter(dependencies=[Depends(require_group("medicos"))])
```

## Notes

- Offline signature + `exp` checks cannot detect revoked tokens (AWS docs); keep access-token
  lifetimes short or check with the IdP when revocation must be honored.
- AWS: "cache public keys ... kid as cache key ... refresh periodically"; on unknown `kid` with the
  right issuer the pool may have rotated keys. PyJWKClient's own cache/cooldown handles refresh;
  verify rotation behavior against your installed PyJWT version.
- FastAPI >= 0.122.0 (2025-11-24) returns 401 (not 403) from `HTTPBearer` for a missing/non-Bearer
  header; older releases returned 403. `auto_error=False` + explicit 401 keeps our own error shape and is
  version-independent.
- Never log tokens. Group names (`cognito:groups`) are Cognito-specific claims.

## See Also

- [dependency-injection](../concepts/dependency-injection.md)
- [testing-overrides](testing-overrides.md) (override `current_claims`)
- [aws KB](../../aws/index.md)

## Sources

- https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html
- https://pyjwt.readthedocs.io/en/stable/usage.html and /api.html
- https://fastapi.tiangolo.com/reference/security/
- https://fastapi.tiangolo.com/release-notes/ (0.122.0: 401 for missing credentials)
- https://raw.githubusercontent.com/fastapi/fastapi/master/fastapi/security/http.py
- https://fastapi.tiangolo.com/async/ (def dependencies run in threadpool)
