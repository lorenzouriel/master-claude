# Cognito JWT Verification in a FastAPI Dependency

> **Purpose**: Verify Cognito access/ID tokens on every request and enforce group membership
> **MCP Validated**: 2026-10-02 (AWS steps verified; PyJWT call shape checked against PyJWT master source)

## When to Use

- A Python API (FastAPI) receives `Authorization: Bearer <token>` from a SPA signed in via Cognito
- Role checks come from `cognito:groups`
- No API Gateway/ALB authorizer in front (those can verify tokens for you instead)

## Implementation

```python
from functools import lru_cache

import jwt                      # PyJWT
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

REGION = "sa-east-1"
USER_POOL_ID = "sa-east-1_EXAMPLE"
APP_CLIENT_ID = "1example23456789"
ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"

bearer = HTTPBearer(auto_error=False)


@lru_cache
def jwks_client() -> PyJWKClient:
    # PyJWKClient looks keys up by kid and refreshes the JWKS when the kid is unknown
    return PyJWKClient(f"{ISSUER}/.well-known/jwks.json")


def verify_token(token: str, expected_use: str = "access") -> dict:
    try:
        key = jwks_client().get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],            # Cognito signs with RS256
            issuer=ISSUER,                   # iss must match this user pool
            options={"require": ["exp", "iss", "token_use"], "verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token") from exc

    if claims["token_use"] != expected_use:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "wrong token type")
    # access token -> client_id ; id token -> aud (access tokens have no aud by default)
    audience = claims.get("client_id") if expected_use == "access" else claims.get("aud")
    if audience != APP_CLIENT_ID:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "wrong app client")
    return claims


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing token")
    return verify_token(creds.credentials)


def require_group(*allowed: str):
    def dep(claims: dict = Depends(current_user)) -> dict:
        if not set(claims.get("cognito:groups", [])) & set(allowed):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "forbidden")
        return claims
    return dep
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `ISSUER` | `https://cognito-idp.{region}.amazonaws.com/{poolId}` | must equal token `iss` exactly |
| JWKS URL | `{ISSUER}/.well-known/jwks.json` | public keys; cache by `kid` |
| `algorithms` | `["RS256"]` | never accept `none` or HS* |
| Access token lifetime | 5 min - 1 day per app client | shorter = faster revocation effect |

## Example Usage

```python
@router.get("/admin/cases", dependencies=[Depends(require_group("admin"))])
def list_cases(user: dict = Depends(current_user)):
    return {"sub": user["sub"]}   # sub is the stable user key
```

## Notes

- Offline verification cannot see revocation (sign-out, `RevokeToken`); keep access tokens short.
- Verify ID and access tokens independently: they use different signing keys and `kid`s.
- Test with a stub JWKS and self-signed RS256 keys; see [testing](../../testing/index.md).
- Validate settings (pool ID, client ID) with [pydantic settings](../../pydantic/index.md).

## See Also

- [cognito-tokens-groups](../concepts/cognito-tokens-groups.md)
- [s3-upload-scan-gate](s3-upload-scan-gate.md)

## Sources

- https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html
- https://github.com/jpadilla/pyjwt (`jwt/jwks_client.py`, `jwt/api_jwt.py`, `jwt/exceptions.py`: `PyJWKClient`,
  `decode(issuer=, options={"require", "verify_aud"})`, `PyJWTError`). Run the code against a test token.
- Note: if a client requests a resource-server-bound access token, `aud` is the resource identifier
  (still no app client ID), so the `client_id` check above stays correct.
