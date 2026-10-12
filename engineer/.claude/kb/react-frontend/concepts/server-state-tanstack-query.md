# Server State with TanStack Query

> **Purpose**: Fetch, cache, and mutate server data with TanStack Query v5
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

`@tanstack/react-query` (v5, npm 5.104.x; React 18+) manages fetching, caching, deduplication and
background sync of server state. Keep server data in the query cache and UI-only state in React
state; do not copy query results into `useState`.

## The Concept

```tsx
import { QueryClient, QueryClientProvider, queryOptions, useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 60_000 } } })

// App root: <QueryClientProvider client={queryClient}><App /></QueryClientProvider>

export const casesQuery = (filters: { status?: string; page: number }) =>
  queryOptions({
    queryKey: ['cases', filters],                 // include every variable the fn depends on
    queryFn: () => api.listCases(filters),
  })

function CaseList() {
  const { data, isPending, error } = useQuery(casesQuery({ page: 1 }))
  // ...
}

function useCreateCase() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.createCase,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cases'] }),   // prefix match
  })
}
```

## Quick Reference

| Topic | Fact |
|-------|------|
| Query keys | Top-level array; object property order is irrelevant, array order matters |
| Defaults | Data is stale immediately; `gcTime` 5 min; 3 retries with exponential backoff |
| Refetch triggers | New observer mounts, window refocus, network reconnect (while stale) |
| `staleTime` | Number (ms), `Infinity`, or `'static'` (never refetch, even on invalidate) |
| `invalidateQueries` | Marks stale (overrides `staleTime`) and refetches active; prefix match, `exact: true` to narrow |
| Mutation states | `idle`, `pending` (`isPending`), `error`, `success`; callbacks `onMutate/onSuccess/onError/onSettled` |
| `mutateAsync` | Promise-returning variant of `mutate` |
| `queryOptions()` | Returns its input unchanged at runtime; adds type inference, reusable in `useQuery`, `prefetchQuery`, `setQueryData(opts.queryKey, ...)` |

## Common Mistakes

### Wrong

```tsx
useQuery({ queryKey: ['cases'], queryFn: () => api.listCases({ page }) })  // page missing from key
const [rows, setRows] = useState(data)                                      // duplicated server state
```

### Correct

```tsx
useQuery({ queryKey: ['cases', { page }], queryFn: () => api.listCases({ page }) })
```

Tests: build a fresh `QueryClient` per test with `retry: false`, otherwise error cases time out
because of default retries.

## Related

- [OpenAPI client](../patterns/openapi-client-consumption.md) , [Testing](../patterns/testing-vitest-playwright.md)
- [Client routing](client-routing.md) (loaders can prefetch with the same `queryOptions`)

## Sources

- https://tanstack.com/query/latest/docs/framework/react/{installation,guides/query-keys,guides/important-defaults,guides/mutations,guides/query-invalidation,guides/query-options,guides/testing}
