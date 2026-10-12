# Environment-Gated Release Pipeline

> **Purpose**: Chain test -> build -> staging -> approved production using environments and OIDC
> **MCP Validated**: 2026-10-02

## When to Use

- Production must need human approval; staging auto-deploys
- Different AWS roles per environment, no stored cloud keys

## Implementation

```yaml
name: release
on:
  push: { branches: [main] }

permissions: { contents: read }

jobs:
  ci:
    uses: ./.github/workflows/ci.yml
  build:
    needs: ci
    uses: ./.github/workflows/build.yml
    with: { context: apps/api, image: api }
    permissions: { contents: read, packages: write, id-token: write, attestations: write }
  staging:
    needs: build
    uses: ./.github/workflows/deploy.yml
    with: { environment: staging, tag: "${{ needs.build.outputs.tag }}" }
    permissions: { id-token: write, contents: read }
  production:
    needs: staging
    uses: ./.github/workflows/deploy.yml     # job inside sets `environment: production`
    with: { environment: production, tag: "${{ needs.build.outputs.tag }}" }
    permissions: { id-token: write, contents: read }
```

`deploy.yml` declares `on: workflow_call` with an `environment` input and uses
`environment: ${{ inputs.environment }}` on its job. Role ARN and instance id live in
environment *variables* (`vars.`), per environment.

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| Required reviewers | up to 6 on `production` | One approval suffices; enable prevent-self-review |
| Wait timer | minutes | Optional soak delay |
| Deployment branches | `main` only | Stops feature branches from deploying |
| OIDC `sub` | `repo:ORG/REPO:environment:production` | Trust policy pins the environment name; check legacy vs immutable format |
| Secrets | environment-level | Not passable through `workflow_call` from the caller; define them on the environment used inside the called job |
| Plan | Free: public repos only | Private repo environments need Team/Pro or higher |

## Example Usage

Approval pauses the `production` job before it can access environment secrets or assume the
environment-scoped role. Failure at `staging` stops the chain (`needs`).

## See Also

- [workflow-fundamentals](../concepts/workflow-fundamentals.md)
- [oidc-aws-federation](../concepts/oidc-aws-federation.md)
- [ec2-compose-ssm-deploy](ec2-compose-ssm-deploy.md)

## Sources

- https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
- https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
- https://docs.github.com/en/actions/reference/security/oidc
