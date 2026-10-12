# React Frontend Quick Reference

> Fast lookup tables. For code examples, see linked files. Versions verified 2026-10-02 (npm + docs).

## Latest Versions (npm `latest`)

| Package | Version | Notes |
|---------|---------|-------|
| react / react-dom | 19.3.0 | react.dev/versions |
| vite | 8.3.x | Rolldown-based; Node 20.19+/22.12+ |
| @vitejs/plugin-react | 6.1 | peer vite ^8 |
| tailwindcss, @tailwindcss/vite | 4.3.3 | |
| typescript | 7.0.2 | native compiler; `tsc` unchanged |
| @tanstack/react-query | 5.104 | React 18+ |
| react-router | 8.4 | Node >= 22.22, React >= 19.2.7 |
| @tanstack/react-router | 1.170 | |
| react-hook-form / zod / @hookform/resolvers | 7.89 / 4.6 / 5.9 | |
| recharts | 3.10 | |
| vitest / @playwright/test | 5.0 / 1.63 | Node 22+ |
| @hey-api/openapi-ts / openapi-fetch | 0.99 / 0.17 | hey-api pre-1.0: pin exact |

## Commands

| Task | Command |
|------|---------|
| Scaffold | `npm create vite@latest` |
| Tailwind | `npm install tailwindcss @tailwindcss/vite` |
| Query | `npm i @tanstack/react-query` |
| Unit tests | `npx vitest` / `npx vitest run` |
| E2E init / run | `npm init playwright@latest` / `npx playwright test` |
| openapi-typescript | `npx openapi-typescript spec.yaml -o src/generated/schema.d.ts` |

## TanStack Query Defaults

| Setting | Default |
|---------|---------|
| staleTime | 0 (stale immediately) |
| gcTime | 5 min |
| retry | 3, exponential backoff |
| Refetch | mount, focus, reconnect |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Typed search params, fully inferred routes | TanStack Router |
| Familiar ecosystem, loaders/actions, optional SSR | React Router (data or framework mode) |
| Simple form, few fields | React 19 `<form action>` + `useActionState` |
| Many fields, schema reuse | React Hook Form + Zod |
| Full SDK + Query hooks from spec | `@hey-api/openapi-ts` + tanstack-query plugin |
| Thin typed fetch from spec | openapi-typescript + openapi-fetch |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| `bg-${color}-600` | Map to complete static class strings |
| Secrets in `VITE_*` | Keep secrets server-side |
| Omit variables from `queryKey` | Include every dependency |
| `<div onClick>` / `role="button"` | `<button>` |
| Trust client role guards | Authorize on the API |
| Share one QueryClient across tests | New client per test, `retry: false` |
| Commit `playwright/.auth` | Gitignore it |
| Chart in parent without height | Give parent a defined size |

## Related Documentation

| Topic | Path |
|-------|------|
| Getting Started | `concepts/toolchain-vite-tailwind.md` |
| Full Index | `index.md` |
