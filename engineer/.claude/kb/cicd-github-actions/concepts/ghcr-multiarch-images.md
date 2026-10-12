# Multi-Arch Images and GHCR

> **Purpose**: Building ARM/multi-platform images (QEMU vs native runners) and publishing to GHCR
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

An ARM EC2 host (Graviton) needs `linux/arm64` images. Options: QEMU emulation on an x86
runner (simple, slower) or native arm64 runners. Docker docs state building multiple
platforms on one runner "can significantly extend build times", and offer a
split-across-runners approach (`docker/github-builder`).

## The Concept

```yaml
runs-on: ubuntu-24.04-arm          # native arm64 build, no QEMU needed
steps:
  - uses: docker/setup-buildx-action@<sha>      # v4
  - uses: docker/login-action@<sha>             # v4
    with: { registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
  - id: meta
    uses: docker/metadata-action@<sha>          # v6
    with: { images: "ghcr.io/${{ github.repository }}/api" }
  - uses: docker/build-push-action@<sha>        # v7
    with:
      context: apps/api
      platforms: linux/arm64                    # add linux/amd64 only if needed
      push: true
      tags: ${{ steps.meta.outputs.tags }}
      labels: ${{ steps.meta.outputs.labels }}
```

For multi-arch via QEMU add `docker/setup-qemu-action` (v4) and
`platforms: linux/amd64,linux/arm64`.

## Quick Reference

| Topic | Fact |
|-------|------|
| ARM runner labels | `ubuntu-24.04-arm`, `ubuntu-22.04-arm` |
| Public repo ARM runner | 4 vCPU / 16 GB, free |
| Private repo ARM runner | 2 vCPU / 8 GB, bills against account minutes. Available since 2026-01-29 (earlier docs said private repos unsupported; superseded) |
| GHCR auth in workflow | `GITHUB_TOKEN` + `permissions: packages: write` |
| Pull from outside Actions (e.g. EC2) | Only a PAT (classic) with `read:packages` works for `docker login ghcr.io` |
| New package visibility | Private by default; linking to repo via `org.opencontainers.image.source` label |
| Retention | No automatic retention documented; delete via UI/REST; restorable 30 days; public package with a version >5000 downloads cannot be deleted |
| Default tags (metadata-action, empty `tags`) | branch, tag, PR refs; `latest` only for tag/semver/match types |
| Provenance/SBOM | `provenance` / `sbom` inputs on build-push-action |

## Common Mistakes

### Wrong

`tags: latest` only; deploy pulls a moving tag, so rollback is impossible.

### Correct

Also tag with the commit SHA (`type=sha` in metadata-action) and deploy by immutable tag or
digest; keep the previous tag recorded for [rollback](../patterns/ec2-compose-ssm-deploy.md).

## Practitioner notes (not from docs)

- Registry cache (`cache-from`/`cache-to`) options exist on build-push-action; the `type=gha`
  backend was not re-verified here, check Docker's cache docs before using.

## Related

- [build-publish-image](../patterns/build-publish-image.md)
- [aws KB: github-actions-ci (ECS path)](../../aws/containers/patterns/github-actions-ci.md)

## Sources

- https://docs.docker.com/build/ci/github-actions/multi-platform/
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://github.blog/changelog/2026-01-29-arm64-standard-runners-are-now-available-in-private-repositories/
- https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- https://docs.github.com/en/packages/learn-github-packages/deleting-and-restoring-a-package
- https://github.com/docker/metadata-action
- https://github.com/docker/build-push-action
