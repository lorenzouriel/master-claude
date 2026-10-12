# EC2 + Docker Compose Deploy via SSM (with migrations and rollback)

> **Purpose**: Deploy an immutable image tag to an EC2 host, migrate the DB, gate on health, roll back
> **MCP Validated**: 2026-10-02 (commands/flags); the script layout itself is a recommended design, not a vendor-specified procedure

## When to Use

- Single EC2 host (or few) running Compose, no inbound SSH
- DB schema managed by Alembic; deploy must not leave app and schema out of step

## Implementation

Workflow side (OIDC role, then SendCommand; see [ssm-run-command](../concepts/ssm-run-command.md)):

```yaml
deploy:
  runs-on: ubuntu-24.04
  environment: production
  concurrency: { group: deploy-production, cancel-in-progress: false }
  permissions: { id-token: write, contents: read }
  steps:
    - uses: aws-actions/configure-aws-credentials@<sha>
      with: { role-to-assume: "${{ vars.DEPLOY_ROLE_ARN }}", aws-region: sa-east-1 }
    - env: { TAG: "${{ inputs.tag }}", IID: "${{ vars.INSTANCE_ID }}" }
      run: |
        [[ "$TAG" =~ ^sha-[0-9a-f]{12}$ ]] || { echo bad tag; exit 1; }
        CMD=$(aws ssm send-command --document-name AWS-RunShellScript \
          --instance-ids "$IID" --timeout-seconds 900 --comment "deploy $TAG" \
          --parameters "commands=[\"/opt/app/deploy.sh $TAG\"]" \
          --query Command.CommandId --output text)
        aws ssm wait command-executed --command-id "$CMD" --instance-id "$IID" \
          || { aws ssm get-command-invocation --command-id "$CMD" --instance-id "$IID"; exit 1; }
```

Host side `/opt/app/deploy.sh` (design sketch):

```bash
#!/usr/bin/env bash
set -euo pipefail
NEW="$1"; cd /opt/app
PREV=$(cat .current_tag 2>/dev/null || echo "")
export IMAGE_TAG="$NEW"
docker compose pull                              # fail fast before touching running containers
docker compose run --rm api alembic upgrade head # migrate BEFORE switching traffic
docker compose up -d --remove-orphans --wait --wait-timeout 120   # waits running/healthy
curl -fsS http://localhost:8000/healthz >/dev/null || HEALTH_FAIL=1
if [[ -n "${HEALTH_FAIL:-}" ]]; then
  [[ -n "$PREV" ]] && { export IMAGE_TAG="$PREV"; docker compose up -d --wait --wait-timeout 120; }
  exit 1
fi
echo "$NEW" > .current_tag
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `compose up --wait` | implies detached | Waits for services running/healthy; `--wait-timeout` seconds |
| `compose pull` | `--quiet`, `--policy always\|missing`, `--ignore-pull-failures`, `--include-deps` | Do not use `--ignore-pull-failures` in deploys |
| `depends_on.condition` | `service_healthy` | Needs a `healthcheck` on the dependency |
| `alembic upgrade head` | / `downgrade -1` | Inspect with `alembic current`, `history`, `heads` |
| GHCR login on host | PAT (classic) `read:packages` | `GITHUB_TOKEN` is not usable outside the workflow; store PAT in SSM Parameter Store/Secrets Manager, not in the repo |

## Rollback rules

- Image rollback = redeploy `PREV` tag (immutable SHA tags make this exact).
- Migrations: make them backward compatible (expand, deploy, contract) so the previous image
  still runs on the new schema. `alembic downgrade -1` can destroy data; use it only for
  migrations written and tested as reversible. This is a recommended practice, not a vendor rule.
- A script exit code is only the last command's unless `set -e` is used; the sketch uses it.

## Practitioner notes (not from docs)

- Run migrations from the new image (`compose run --rm`) so code and revision files match.
- Take an RDS snapshot before destructive migrations.

## See Also

- [ssm-run-command](../concepts/ssm-run-command.md)
- [environment-gated-release](environment-gated-release.md)
- [data-modeling schema-migration](../../data-modeling/patterns/schema-migration.md)

## Sources

- https://docs.docker.com/reference/cli/docker/compose/up/
- https://docs.docker.com/reference/cli/docker/compose/pull/
- https://docs.docker.com/reference/compose-file/services/#healthcheck
- https://alembic.sqlalchemy.org/en/latest/tutorial.html
- https://docs.aws.amazon.com/cli/latest/reference/ssm/send-command.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command-handle-exit-status.html
- https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
