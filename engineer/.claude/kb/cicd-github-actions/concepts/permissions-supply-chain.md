# GITHUB_TOKEN Permissions and Supply-Chain Hardening

> **Purpose**: Least-privilege tokens, secrets handling, SHA pinning, Dependabot
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

Every job gets a `GITHUB_TOKEN`. Declare `permissions` explicitly: once any scope is
listed, all unlisted scopes become `none`. Third-party actions run with your job's
secrets, so pin them to immutable references and keep them updated.

## The Concept

```yaml
permissions:            # workflow default: read only
  contents: read

jobs:
  publish:
    permissions:        # elevate per job
      contents: read
      packages: write   # GHCR push
      id-token: write   # OIDC (also needed for attestations)
    steps:
      - uses: actions/checkout@<40-char-sha>   # v7
```

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: { interval: "weekly" }
```

## Quick Reference

| Control | Rule |
|---------|------|
| Scopes | `contents`, `packages`, `id-token`, `pull-requests`, `actions`, `checks`, `deployments`, ... each `read`/`write`/`none` |
| Default | Set repo default to read-only for contents; elevate per job |
| Pinning | Pin to a full-length commit SHA (tags can be moved); GitHub's own examples do this |
| Secrets | Use `::add-mask::` for derived values; no JSON/YAML blobs as one secret; rotate; prefer OIDC over stored cloud keys |
| Script injection | Pass untrusted input via `env:` then `"$VAR"`, never `${{ github.event... }}` inside `run:` |
| `pull_request_target` / `workflow_run` | Privileged; never check out untrusted PR code there |
| Dependabot | `github-actions` ecosystem, directory `/`, interval e.g. weekly |

## Common Mistakes

### Wrong

```yaml
- run: echo "${{ github.event.pull_request.title }}" | ./script.sh   # injection
- uses: some/action@main                                              # mutable ref
```

### Correct

```yaml
- env: { TITLE: "${{ github.event.pull_request.title }}" }
  run: printf '%s' "$TITLE" | ./script.sh
- uses: some/action@<40-char-sha>   # v1.2.3
```

## Related

- [oidc-aws-federation](oidc-aws-federation.md)
- [workflow-fundamentals](workflow-fundamentals.md)

## Sources

- https://docs.github.com/en/actions/reference/security/secure-use
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot
- https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images
