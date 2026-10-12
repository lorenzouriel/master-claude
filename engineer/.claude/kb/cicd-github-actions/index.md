# CI/CD with GitHub Actions Knowledge Base

> **Purpose**: GitHub Actions to GHCR to EC2 (Docker Compose) via SSM, with OIDC, migrations and hardening
> **MCP Validated**: 2026-10-02

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/workflow-fundamentals.md](concepts/workflow-fundamentals.md) | Triggers, jobs, matrix, concurrency, environments, cache, artifacts, reusable workflows |
| [concepts/oidc-aws-federation.md](concepts/oidc-aws-federation.md) | Keyless AWS auth, trust policy conditions, immutable `sub` change |
| [concepts/permissions-supply-chain.md](concepts/permissions-supply-chain.md) | GITHUB_TOKEN least privilege, SHA pinning, Dependabot, secrets |
| [concepts/ghcr-multiarch-images.md](concepts/ghcr-multiarch-images.md) | ARM runners vs QEMU, GHCR auth/visibility/retention |
| [concepts/ssm-run-command.md](concepts/ssm-run-command.md) | send-command, wait, output limits, IAM scoping |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/ci-test-pipeline.md](patterns/ci-test-pipeline.md) | Postgres service container, testcontainers note, Playwright |
| [patterns/build-publish-image.md](patterns/build-publish-image.md) | Reusable arm64 build and GHCR push |
| [patterns/ec2-compose-ssm-deploy.md](patterns/ec2-compose-ssm-deploy.md) | Deploy, migrate, health gate, rollback |
| [patterns/environment-gated-release.md](patterns/environment-gated-release.md) | staging -> approved production chain |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **OIDC** | Per-job JWT exchanged for temporary AWS credentials; trust policy pins `aud` + `sub` |
| **Environment** | Approval gate plus scoped secrets/variables for a deploy job |
| **Immutable tags** | Deploy by SHA tag/digest so rollback is exact |
| **SSM Run Command** | Deploy without SSH/inbound ports; mind exit codes and 24k output cap |
| **Expand/contract migrations** | Keep the previous image compatible with the new schema |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/workflow-fundamentals.md, patterns/ci-test-pipeline.md |
| **Intermediate** | concepts/oidc-aws-federation.md, patterns/build-publish-image.md |
| **Advanced** | patterns/ec2-compose-ssm-deploy.md, patterns/environment-gated-release.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| aws-app-platform-specialist | concepts/oidc-aws-federation.md, concepts/ssm-run-command.md, patterns/ec2-compose-ssm-deploy.md | Deploy path, IAM roles, SSM |
| fastapi-backend-specialist | patterns/ci-test-pipeline.md, patterns/build-publish-image.md | API tests with Postgres, image build |
| react-frontend-specialist | patterns/ci-test-pipeline.md | Playwright E2E in CI |
| aws-container-ops (existing) | [aws KB github-actions-ci](../aws/containers/patterns/github-actions-ci.md) | ECS path (out of this domain's focus) |

Related: [terraform](../terraform/index.md), [testing](../testing/index.md), [aws](../aws/index.md).
Out of scope: Azure DevOps, Databricks bundles, Terraform syntax.
