# CI/CD GitHub Actions Quick Reference

> Fast lookup tables. For code examples, see linked files. Verified 2026-10-02.

## Current action majors (latest GitHub releases, checked 2026-10-02; floating tags, pin by SHA in real workflows)

| Action | Major |
|--------|-------|
| aws-actions/configure-aws-credentials | v6 |
| docker/build-push-action | v7 |
| docker/setup-buildx-action, setup-qemu-action, login-action | v4 |
| docker/metadata-action | v6 |
| actions/upload-artifact | v7 |
| actions/checkout | v7 (GitHub's publish-images example still shows v6) |
| actions/cache | v6 |
| actions/setup-node | v7 |
| actions/attest | v4 |

## Limits and defaults

| Item | Value |
|------|-------|
| Job timeout | 360 min default |
| Cache | 10 GB/repo, 7 days unused eviction |
| Artifact retention | 90 d default |
| Environment reviewers | max 6 |
| Pending runs per concurrency group | 1 (`queue: single`), up to 100 (`queue: max`) |
| SSM API output | stdout 24,000 / stderr 8,000 chars |
| `aws ssm wait command-executed` | 5 s x 20 attempts |
| `send-command --instance-ids` | max 50 |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| arm64 image for Graviton | `runs-on: ubuntu-24.04-arm` + `platforms: linux/arm64` |
| Multi-arch on x86 runner | setup-qemu + `linux/amd64,linux/arm64` (slower) |
| Cloud auth | OIDC role, never stored keys |
| Push to GHCR in CI | `GITHUB_TOKEN` + `packages: write` |
| Pull GHCR on EC2 | PAT (classic) `read:packages` |
| DB for tests | `services: postgres` (+ health-cmd); localhost + port map on runner |

## OIDC sub

| Context | sub |
|---------|-----|
| environment | `repo:O/R:environment:NAME` |
| branch | `repo:O/R:ref:refs/heads/B` |
| immutable (repos created after 2026-07-15) | `repo:O@OID/R@RID:...` |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| `cancel-in-progress: true` on deploys | `false`, group per environment |
| `uses: x@v1` / `@main` | full-length SHA + Dependabot |
| Trust `repo:ORG/*` | Pin repo + environment |
| Trust policy for legacy sub on new repo | Check sub format; see oidc concept |
| Rely on last-command exit code in SSM | `set -euo pipefail` |
| Deploy `latest` | Deploy SHA tag, record previous |
| `${{ github.event.* }}` inside `run:` | Pass via `env:` |
| Cache Playwright browsers | Install each run (`--with-deps`) |

## Related Documentation

| Topic | Path |
|-------|------|
| Getting Started | `concepts/workflow-fundamentals.md` |
| Full Index | `index.md` |
