# Feature Folders for a Role-Based App

> **Purpose**: Organize a React SPA with separate admin / company / doctor areas
> **MCP Validated**: 2026-10-02

## When to Use

- One SPA serves several user roles with different screens.
- You want code for one feature (UI, hooks, queries, tests) kept together.
- You want generated API code isolated from hand-written code.

## Implementation

React itself has no prescribed structure; its docs describe grouping by feature/route or by file
type, recommend colocation, and advise against deep nesting (3-4 levels). The layout below is one
conventional feature-based application of that guidance (practitioner pattern, not a standard).

```text
src/
  app/                  # providers, router, layouts, route guards
    router.tsx
    providers.tsx       # QueryClientProvider, auth provider
    guards/
  features/
    admin/              # role area: pages + feature-only components/hooks
      users/
        UsersPage.tsx
        queries.ts      # queryOptions + mutation hooks for this feature
        users.test.tsx
    company/
    doctor/
  shared/               # role-agnostic: ui/, hooks/, lib/ (formatters, a11y helpers)
  generated/            # OpenAPI client output; never edited by hand
  main.tsx
```

Rules (practitioner notes):

| Rule | Reason |
|------|--------|
| Features do not import from other features | Prevents hidden coupling; lift shared code to `shared/` |
| `shared/` never imports from `features/` | Keeps dependency direction one-way |
| Only `app/` wires routes to feature pages | Single place to see role access |
| Lazy-load each role area (`lazy` route property or `React.lazy`) | A doctor never downloads admin code (UX/perf; not a security control) |
| Path alias `@/*` -> `src/*` | Avoid `../../..` chains; set in both `tsconfig` `paths` and tooling |

## Configuration

| Setting | Where | Description |
|---------|-------|-------------|
| `paths: { "@/*": ["./src/*"] }` | `tsconfig.json` | Type resolution for the alias |
| Alias resolution | Vite config or the Vite 8 `resolve.tsconfigPaths` option (per Vite 8 release notes) | Runtime/build resolution |

## Example Usage

```tsx
// app/router.tsx (React Router data mode)
{ path: '/doctor', Component: DoctorLayout, lazy: () => import('@/features/doctor/routes') }
```

## See Also

- [Role-guarded routes](role-guarded-routes.md) , [Client routing](../concepts/client-routing.md)
- [OpenAPI client](openapi-client-consumption.md)

## Sources

- https://legacy.reactjs.org/docs/faq-structure.html (no-opinion, feature grouping, colocation, nesting depth)
- https://reactrouter.com/start/data/route-object (`lazy`) ; https://vite.dev/blog/announcing-vite8 (`resolve.tsconfigPaths`)
- Folder rules above: practitioner convention, not verified against a standard
