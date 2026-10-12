# Role-Guarded Routes

> **Purpose**: Restrict route subtrees by authentication and role in the client (UX layer)
> **MCP Validated**: 2026-10-02

## When to Use

- Redirect unauthenticated users to login and send each role to its own area.
- Hide routes a role should never navigate to.

**Practitioner note (not from the router docs): client guards are a UX convenience. Bundles and
JS state are user-controlled, so every API endpoint must enforce authorization server-side.**

## Implementation

Shared idea: a layout (parent) route performs the check once; child routes inherit it.

```tsx
// React Router data mode: loader throws redirect (middleware is also supported)
import { redirect, Outlet } from 'react-router'

type Role = 'admin' | 'company' | 'doctor'

export function requireRole(role: Role) {
  return async () => {
    const session = await getSession()            // e.g. cached via queryClient.ensureQueryData
    if (!session) throw redirect('/login')
    if (session.role !== role) throw redirect(homeFor(session.role))
    return session
  }
}

const routes = [
  { path: '/admin',  loader: requireRole('admin'),  Component: AdminLayout },   // layout renders <Outlet />
  { path: '/doctor', loader: requireRole('doctor'), Component: DoctorLayout },
]
```

```tsx
// TanStack Router: beforeLoad + redirect on a pathless layout route (file: routes/_authenticated.tsx)
export const Route = createFileRoute('/_authenticated')({
  beforeLoad: ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({ to: '/login', search: { redirect: location.href } })
    }
  },
})
// Root: createRootRouteWithContext<{ auth: AuthState }>(); pass context to <RouterProvider context={{ auth }} />
```

## Configuration

| Mechanism | Router | Notes |
|-----------|--------|-------|
| `loader` + `throw redirect()` | React Router | Runs before render; revalidates on navigation/actions |
| `middleware: [fn]` | React Router | Documented example throws `redirect("/login")` before `next()` |
| `beforeLoad` + `redirect` | TanStack Router | Documented for authenticated routes; context typed via `createRootRouteWithContext` |
| Pathless layout route | TanStack Router | Protects an entire subtree |

## Example Usage

Preserve the intended destination: TanStack docs pass `search: { redirect: location.href }`; after
login, navigate there. On role mismatch, redirect to the user's own home rather than showing 403 UI.
Treat 401/403 API responses as the authoritative signal: clear the session and redirect.

## See Also

- [Client routing](../concepts/client-routing.md) , [Feature folders](feature-folders-role-areas.md)
- [Server state](../concepts/server-state-tanstack-query.md)

## Sources

- https://reactrouter.com/start/data/route-object (loader, middleware, redirect)
- https://tanstack.com/router/latest/docs/framework/react/guide/authenticated-routes
- Server-side authorization note: practitioner guidance; no source fetched
