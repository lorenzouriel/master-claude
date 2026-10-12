# Workflow Fundamentals

> **Purpose**: Triggers, jobs, matrix, concurrency, environments, caching, artifacts, reusable workflows
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

A workflow is a YAML file in `.github/workflows/`. Jobs run in parallel unless sequenced
with `needs`. Deployment safety comes from three levers: `concurrency` (serialise),
`environment` (approval gates, scoped secrets) and explicit `permissions`.

## The Concept

```yaml
name: ci
on:
  push:
    branches: [main]
    paths: ["apps/api/**"]
  pull_request:
  workflow_dispatch:
    inputs:
      image_tag: { type: string, required: false }

concurrency:                       # serialise deploys, never cancel a running one
  group: deploy-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: read                   # unspecified scopes become `none`

jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 15            # default is 360
    strategy:
      fail-fast: true              # default
      matrix:
        python: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@<full-sha>   # vX.Y.Z
  deploy:
    needs: test
    environment: production        # reviewers / wait timer enforced here
    runs-on: ubuntu-24.04
    steps: [...]
```

## Quick Reference

| Feature | Rule | Notes |
|---------|------|-------|
| `concurrency.group` | any string/expression; contexts `github, inputs, vars, needs, strategy, matrix` | At most one pending run per group |
| `queue` | `single` (default; newer pending replaces older) or `max` (up to 100 pending) | `queue: max` + `cancel-in-progress: true` is a validation error |
| Environment reviewers | up to 6; one approval suffices | Optional "prevent self-review" |
| Environment secrets | available only after protection rules pass | Free plan: environments on public repos only; private needs Team/Pro+ |
| Cache | 10 GB/repo default; unused 7 days evicted | Restore only from current, default or base branch |
| Artifact | `upload-artifact` latest major v7; retention default 90 d (min 1) | Names unique per run; hidden files excluded by default |
| Reusable workflow | `on: workflow_call`; `uses: ./.github/workflows/x.yml` | Permissions can only be kept or reduced; env-level secrets cannot be passed from caller; max 10 levels |
| Job timeout | `timeout-minutes`, default 360 | Always set lower |

## Common Mistakes

### Wrong

```yaml
concurrency: { group: deploy, cancel-in-progress: true }   # kills a half-finished deploy/migration
```

### Correct

```yaml
concurrency: { group: deploy-production, cancel-in-progress: false }
```

Use `cancel-in-progress: true` only for PR test runs (`group: ci-${{ github.ref }}`).

## Practitioner notes (not from docs)

- Put deploy in its own job with `environment:` so only that job can read environment secrets.

## Related

- [oidc-aws-federation](oidc-aws-federation.md)
- [permissions-supply-chain](permissions-supply-chain.md)
- [environment-gated-release](../patterns/environment-gated-release.md)

## Sources

- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
- https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
- https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching
- https://github.com/actions/upload-artifact
- https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
