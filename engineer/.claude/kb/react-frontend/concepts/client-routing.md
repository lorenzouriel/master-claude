# Client Routing: React Router vs TanStack Router

> **Purpose**: Neutral comparison of the two common SPA routers and their current state
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

Both are viable for a Vite SPA. **React Router** (npm `react-router` 8.4.x, v8 released 2026-06-17)
offers three modes: declarative, data, framework. **TanStack Router** (npm `@tanstack/react-router`
1.170.x) emphasizes inferred type safety, typed search params, and file- or code-based routes.
Pick one per app; do not mix.

## The Concept

```tsx
// React Router, data mode (package: react-router)
import { createBrowserRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'

const router = createBrowserRouter([
  { path: '/', Component: Root, children: [
      { path: 'cases/:id', loader: loadCase, Component: CasePage } ] },
])
// <RouterProvider router={router} />   (create router outside React state)
```

```tsx
// TanStack Router, code/file-based routes
export const Route = createFileRoute('/cases/$caseId')({
  loader: ({ params }) => load(params.caseId),
  component: CasePage,
})
```

## Quick Reference

| Aspect | React Router | TanStack Router |
|--------|--------------|-----------------|
| Modes | Declarative (`BrowserRouter`), Data (`createBrowserRouter`), Framework (Vite plugin over Data) | Single model; file-based and code-based can coexist |
| Data loading | `loader`/`action`, `useFetcher`, `lazy`, `shouldRevalidate` | Built-in loader cache with lifecycle APIs; works with TanStack Query/SWR |
| Type safety | Typed in Framework mode (route modules, `href`) | Fully inferred navigation, params, search |
| Search params | Standard `URLSearchParams` APIs | Parsed/serialized as JSON, validated by schema, typed |
| Guarding | `middleware` or `loader` throwing `redirect` | `beforeLoad` throwing `redirect`; router context |
| v8 baseline | Node >= 22.22, React >= 19.2.7; `react-router-dom` removed (npm engines + release post) | Not verified this session |

Decision hints (RR docs): Declarative suits simple routing with your own data layer; Data adds
loaders/actions; Framework adds SSR/code splitting. Choose TanStack Router when typed search params
and end-to-end route typing matter most; choose React Router when ecosystem familiarity matters.

## Common Mistakes

- Creating the router inside a component (RR docs: create it outside React state).
- Importing from `react-router-dom` on v8 (package removed; DOM exports come from `react-router/dom`).
- Fetching in both router loaders and `useEffect`; choose loaders (optionally priming Query) or Query alone.

## Related

- [Role-guarded routes](../patterns/role-guarded-routes.md) , [Server state](server-state-tanstack-query.md)

## Sources

- https://reactrouter.com/start/modes , /start/data/installation , /start/data/route-object
- https://tanstack.com/router/latest/docs/framework/react/overview
- npm registry (versions, engines, peerDependencies) 2026-10-02; v8 release post https://remix.run/blog/react-router-v8 (fetched 2026-10-02: Node 22.22+, React 19.2.7+, Vite 7+, `react-router-dom` removed)
