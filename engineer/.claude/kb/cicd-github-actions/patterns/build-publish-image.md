# Build and Publish Image to GHCR

> **Purpose**: Reusable workflow that builds an arm64 image and pushes immutable tags to GHCR
> **MCP Validated**: 2026-10-02

## When to Use

- Every merge to `main` produces a deployable image
- Target host is ARM (Graviton) and you want native builds, no QEMU
- Deploy workflow consumes the resulting tag/digest

## Implementation

```yaml
# .github/workflows/build.yml
name: build
on:
  workflow_call:
    inputs:
      context: { type: string, required: true }
      image:   { type: string, required: true }   # e.g. api
    outputs:
      digest: { value: "${{ jobs.build.outputs.digest }}" }
      tag:    { value: "${{ jobs.build.outputs.tag }}" }

permissions: { contents: read }

jobs:
  build:
    runs-on: ubuntu-24.04-arm
    timeout-minutes: 30
    permissions:
      contents: read
      packages: write
      id-token: write          # only if attesting
      attestations: write
    outputs:
      digest: ${{ steps.push.outputs.digest }}
      tag: ${{ steps.vars.outputs.tag }}
    steps:
      - uses: actions/checkout@<sha>
      - id: vars
        run: echo "tag=sha-${GITHUB_SHA::12}" >> "$GITHUB_OUTPUT"
      - uses: docker/setup-buildx-action@<sha>
      - uses: docker/login-action@<sha>
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@<sha>
        with:
          images: ghcr.io/${{ github.repository }}/${{ inputs.image }}
          tags: |
            type=sha,format=long
            type=raw,value=${{ steps.vars.outputs.tag }}
      - id: push
        uses: docker/build-push-action@<sha>
        with:
          context: ${{ inputs.context }}
          platforms: linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `runs-on: ubuntu-24.04-arm` | n/a | Native arm64; private repos get 2 vCPU/8 GB, billed |
| `permissions.packages` | none | `write` needed to push with `GITHUB_TOKEN` |
| `metadata-action` default tags | branch/tag/PR refs | Override `tags:` to get SHA tags |
| Package visibility | private | Link to repo with `org.opencontainers.image.source` label |
| Attestation | off | GitHub's publish example adds an attest step (`actions/attest`) |

## Example Usage

```yaml
jobs:
  build-api:
    uses: ./.github/workflows/build.yml
    with: { context: apps/api, image: api }
```

Caller must grant at least the permissions the reusable workflow requests; permissions can
only be kept or reduced down the chain.

## See Also

- [ghcr-multiarch-images](../concepts/ghcr-multiarch-images.md)
- [ec2-compose-ssm-deploy](ec2-compose-ssm-deploy.md)
- [permissions-supply-chain](../concepts/permissions-supply-chain.md)

## Sources

- https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images
- https://docs.docker.com/build/ci/github-actions/multi-platform/
- https://github.com/docker/metadata-action
- https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
