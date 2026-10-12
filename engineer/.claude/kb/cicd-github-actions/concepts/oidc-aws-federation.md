# OIDC Federation to AWS

> **Purpose**: Keyless AWS access from GitHub Actions; IAM trust policy conditions
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

GitHub mints a short-lived JWT per job; AWS STS exchanges it (AssumeRoleWithWebIdentity) for
temporary credentials. No access keys are stored. The IAM role's trust policy is the only
security boundary: it must pin `aud` and `sub`, otherwise other repos could assume the role.

## The Concept

```yaml
permissions:
  id-token: write       # required to request the JWT
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@<full-sha>   # v6.x
    with:
      role-to-assume: arn:aws:iam::<account>:role/gha-deploy
      aws-region: sa-east-1
      role-session-name: gha-${{ github.run_id }}
```

Trust policy (principal = the IAM OIDC provider `token.actions.githubusercontent.com`):

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub": "repo:ORG/REPO:environment:production"
  }
}
```

## Subject claim formats

| Context | `sub` |
|---------|-------|
| Environment | `repo:ORG/REPO:environment:NAME` |
| Branch | `repo:ORG/REPO:ref:refs/heads/BRANCH` |
| Pull request | `repo:ORG/REPO:pull_request` |
| Tag | `repo:ORG/REPO:ref:refs/tags/TAG` |
| Immutable (new) | `repo:OWNER@OWNER_ID/REPO@REPO_ID:ref:refs/heads/BRANCH` |

**Breaking change:** repos created after 2026-07-15 (and repos renamed/transferred after that
date) emit the immutable `@ID` format by default. Older repos keep the legacy format until
they opt in (org/repo OIDC settings UI or REST API; a preview endpoint exists). A trust policy
written for the legacy format will fail with `AccessDenied` on a new repo. Check the actual
format before writing the condition.

## Quick Reference

| Item | Value |
|------|-------|
| Required job permission | `id-token: write` |
| Action params | `role-to-assume`, `aws-region`, `role-session-name` (default `GitHubActions`), `role-duration-seconds` (default 3600) |
| Trust policy rule | GitHub: "you must define at least one condition" |
| Operators | Use `StringEquals`/`StringLike`; avoid `ForAllValues:` in Allow (true when claim absent) |
| Thumbprints | AWS validates the JWKS TLS cert via trusted root CAs; thumbprints are a fallback only |
| Same account | OIDC provider must be in the same account as the role |

## Common Mistakes

### Wrong

```json
"StringLike": { "token.actions.githubusercontent.com:sub": "repo:ORG/*" }   // any repo in org
```

### Correct

Pin the repo AND the environment (or branch): `repo:ORG/REPO:environment:production`. Use a
separate role per environment (least privilege: deploy role only needs `ssm:SendCommand`
scoped to tagged instances, see [ssm-run-command](ssm-run-command.md)).

## Practitioner notes (not from docs)

- To tolerate both sub formats during migration, list both strings in a `StringLike` array
  (reported in aws-actions issue #1888); verify with the preview endpoint.

## Related

- [permissions-supply-chain](permissions-supply-chain.md)
- [AWS KB](../../aws/index.md)
- [Terraform KB](../../terraform/index.md) (provisioning the provider/role)

## Sources

- https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws
- https://docs.github.com/en/actions/reference/security/oidc
- https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/
- https://github.com/aws-actions/configure-aws-credentials
- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html
- https://github.com/aws-actions/configure-aws-credentials/issues/1888 (community note)
