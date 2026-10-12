# Cognito Tokens, Groups, and Login UI

> **Purpose**: How Cognito user pool tokens are shaped, verified, and used for group-based authorization
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

A user pool issues three tokens: ID, access, and refresh. ID and access tokens are RS256 JWTs;
the API verifies them offline against the pool's JWKS. Groups appear as the `cognito:groups`
claim in both ID and access tokens. Hosted login is optional; an app can instead call the
user pool API from its own UI.

## Token Comparison

| Aspect | ID token | Access token |
|--------|----------|--------------|
| `token_use` | `id` | `access` |
| Audience claim | `aud` = app client ID | `client_id` = app client ID; no `aud` unless a resource-server binding was requested (then `aud` = resource identifier) |
| Carries | user attributes (`email`, `custom:*`), `cognito:groups`, `cognito:roles`, `cognito:preferred_role` | `scope`, `cognito:groups`, `username`, `origin_jti` |
| Use for | identity in the client app | authorizing API calls |
| Signing key | its own key pair | a different key pair (different `kid`) |
| Lifetime (per app client) | 5 minutes - 1 day | 5 minutes - 1 day |

Refresh token lifetime: 1 hour - 3,650 days. Use `sub` (not username) as the stable user key;
do not validate the `sub` format strictly.

## Verification Checklist (server side)

```text
1. Split header.payload.signature; read kid + alg (RS256 only)
2. Fetch JWKS: https://cognito-idp.{region}.amazonaws.com/{userPoolId}/.well-known/jwks.json
   - cache by kid; on unknown kid with correct iss, refresh the cache
3. Verify signature, then exp
4. iss == https://cognito-idp.{region}.amazonaws.com/{userPoolId}
5. ID token: aud == app client ID.  Access token: client_id == app client ID
6. token_use == "access" (or "id") as your API expects
7. Revocation is NOT detectable offline: keep access tokens short, or check with Cognito
```

## Groups

| Fact | Value |
|------|-------|
| Claim | `cognito:groups` (array of group names) in ID and access tokens |
| Quotas | 10,000 groups per pool; a user can be in 100 groups (not adjustable) |
| Limits | groups cannot be nested; users cannot be searched by group; groups cannot be searched by name (list only) |
| Precedence | non-negative integer, lower wins; same precedence with different role ARNs leaves `cognito:preferred_role` unset |
| IAM role | optional role per group; only matters with identity pools |

Authorize in the API by checking group names from the verified token; do not trust the claim
before signature verification.

## Hosted Login Options

| Option | Notes |
|--------|-------|
| Managed login | needs a user pool domain; branding editor; passkeys; localization needs Essentials/Plus plan |
| Classic hosted UI | only option on the Lite feature plan; fewer features |
| Custom UI + user pool API | required for profile management and custom auth challenges |

Choose managed login or classic hosted UI per domain (not both). Managed login does not support
custom authentication challenge Lambda triggers and does not provide profile self-service.
It sets a 1-hour session cookie, so shorter token lifetimes do not force re-authentication
within that hour. Authentication requests time out after 5 minutes.
Region: `cognito-idp.sa-east-1.amazonaws.com` exists (Sao Paulo).

## Common Mistakes

### Wrong

```python
# Treating an access token like an ID token
claims = decode(token, audience=CLIENT_ID)   # access tokens have no aud -> fails or is skipped
```

### Correct

```python
# Access token: check client_id and token_use manually after signature+exp+iss verification
assert claims["token_use"] == "access" and claims["client_id"] == CLIENT_ID
```

## Related

- [cognito-jwt-verification](../patterns/cognito-jwt-verification.md)
- [Pydantic settings](../../pydantic/index.md)

## Sources

- https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-id-token.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-user-groups.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-managed-login.html
- https://docs.aws.amazon.com/general/latest/gr/cognito_identity.html
