# Testing: Vitest + Testing Library + Playwright

> **Purpose**: Unit/component tests with Vitest and E2E with Playwright, including auth reuse
> **MCP Validated**: 2026-10-02

## When to Use

- Vitest + Testing Library: components, hooks, form behavior, guarded-route logic with a memory router.
- Playwright: full flows per role against a running app.

## Implementation

Requirements (verified 2026-10-02): Vitest 5.0.x needs Vite >= 6.4 and Node >= 22.12; Playwright
1.63 needs Node 22.x/24.x/26.x. Vitest reads `vite.config.*` unless a `vitest.config.*` exists
(which wins).

```ts
// vitest.config.ts
import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(viteConfig, defineConfig({
  test: { environment: 'jsdom', setupFiles: ['./src/test/setup.ts'] },
}))
```

```tsx
// component test: fresh QueryClient per test, retry off
function renderWithProviders(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}
test('shows validation error', async () => {
  renderWithProviders(<PersonForm onSave={vi.fn()} />)
  await userEvent.click(screen.getByRole('button', { name: /save/i }))
  expect(await screen.findByRole('alert')).toBeVisible()
})
```

```ts
// playwright.config.ts
export default defineConfig({
  use: { baseURL: 'http://localhost:5173' },
  webServer: { command: 'npm run dev', url: 'http://localhost:5173', reuseExistingServer: !process.env.CI },
  projects: [
    { name: 'setup', testMatch: /auth\.setup\.ts/ },
    { name: 'doctor', dependencies: ['setup'], use: { storageState: 'playwright/.auth/doctor.json' } },
  ],
})
// auth.setup.ts ends with: await page.context().storageState({ path: authFile })
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `test.environment` | `node` (default) / `jsdom` / `happy-dom` | happy-dom is faster but lacks some APIs; per-file `// @vitest-environment jsdom` |
| `vitest run` | | Single run (plain `vitest` watches) |
| RTL install | `@testing-library/react` + `@testing-library/dom` | Not a runner; query like a user |
| Locator priority | `getByRole` > text > label > test id > CSS | Locators auto-wait and are strict (multiple matches throw) |
| `.gitignore` | `playwright/.auth`, `.vitest/` | Auth state can impersonate the test account |
| One `storageState` per role | admin / company / doctor | Auth doc: shared-account approach unsuitable for tests that mutate server state |

## Example Usage

```ts
await page.goto('/doctor')
await expect(page.getByRole('heading', { name: /cases/i })).toBeVisible()   // web-first assertion
```

Practitioner notes: mock the network in unit tests (e.g. MSW, npm 3.x; not re-verified), keep E2E to
critical journeys per role, and assert unauthorized roles are redirected.

## See Also

- [Server state](../concepts/server-state-tanstack-query.md) , [Accessibility](../concepts/accessibility-basics.md)
- [testing KB](../../testing/index.md)

## Sources

- https://vitest.dev/guide/ , /config/ , /guide/environment.html ; https://testing-library.com/docs/react-testing-library/intro/
- https://playwright.dev/docs/intro , /docs/auth , /docs/locators , /docs/test-webserver
- https://tanstack.com/query/latest/docs/framework/react/guides/testing ; npm engines (2026-10-02)
