# CI Test Pipeline (Postgres, Testcontainers, Playwright)

> **Purpose**: Backend tests against real Postgres, plus browser E2E tests, on every PR
> **MCP Validated**: 2026-10-02

## When to Use

- API tests that need a real PostgreSQL (migrations applied, no mocks)
- Frontend E2E with Playwright
- Gate before any image build or deploy

## Implementation

```yaml
name: ci
on: { pull_request: {}, push: { branches: [main] } }
concurrency: { group: "ci-${{ github.ref }}", cancel-in-progress: true }
permissions: { contents: read }

jobs:
  api-tests:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: postgres }
        ports: ["5432:5432"]          # required: job runs on the runner, host = localhost
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres
    steps:
      - uses: actions/checkout@<sha>
      - run: pip install -e "apps/api[test]"
      - run: alembic upgrade head      # validates migrations on every PR
        working-directory: apps/api
      - run: pytest -q
        working-directory: apps/api

  e2e:
    runs-on: ubuntu-24.04
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@<sha>
      - uses: actions/setup-node@<sha>
        with: { node-version: lts/* }
      - run: npm ci
        working-directory: apps/web
      - run: npx playwright install --with-deps chromium
        working-directory: apps/web
      - run: npx playwright test
        working-directory: apps/web
      - uses: actions/upload-artifact@<sha>   # v7
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: apps/web/playwright-report/
          retention-days: 14
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| Service host (job on runner) | `localhost` + `ports: 5432:5432` | Mapping required |
| Service host (job in `container:`) | service label (`postgres`) | No port mapping needed |
| Playwright `workers` | `process.env.CI ? 1 : undefined` | Playwright's CI recommendation for stability |
| Browser cache | not recommended | Playwright: restore time is comparable to download |
| Playwright docker image | `mcr.microsoft.com/playwright:<ver>-noble` | Alternative that skips dependency install |
| Report artifact | HTML report, 30 days in Playwright's example | May contain tokens/credentials; keep retention short |

## Example Usage

Testcontainers alternative (practitioner note, community sources only): ubuntu runners ship
Docker, so tests that start Postgres via testcontainers need no `services:` block. Prefer
service containers when one shared DB per job is enough; see
[testing integration patterns](../../testing/patterns/integration-tests.md).

## See Also

- [workflow-fundamentals](../concepts/workflow-fundamentals.md)
- [build-publish-image](build-publish-image.md)

## Sources

- https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers
- https://playwright.dev/docs/ci
- https://playwright.dev/docs/ci-intro
- https://alembic.sqlalchemy.org/en/latest/tutorial.html
- https://github.com/actions/upload-artifact
