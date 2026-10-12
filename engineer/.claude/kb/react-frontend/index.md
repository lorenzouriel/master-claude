# React Frontend Knowledge Base

> **Purpose**: React 19 + Vite 8 + Tailwind v4 SPA: TanStack Query, routing, forms, charts, a11y, testing, role-based structure
> **MCP Validated**: 2026-10-02

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/toolchain-vite-tailwind.md](concepts/toolchain-vite-tailwind.md) | Vite 8, `@tailwindcss/vite`, `@theme`, env vars |
| [concepts/react19-typescript.md](concepts/react19-typescript.md) | React 19 features, strict tsconfig, typing |
| [concepts/server-state-tanstack-query.md](concepts/server-state-tanstack-query.md) | Query keys, defaults, mutations, `queryOptions` |
| [concepts/client-routing.md](concepts/client-routing.md) | React Router vs TanStack Router (neutral) |
| [concepts/charts-recharts.md](concepts/charts-recharts.md) | Recharts 3 basics, `ResponsiveContainer` |
| [concepts/accessibility-basics.md](concepts/accessibility-basics.md) | WCAG 2.2, ARIA rules, accessible fields |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/feature-folders-role-areas.md](patterns/feature-folders-role-areas.md) | Feature folders for admin/company/doctor areas |
| [patterns/role-guarded-routes.md](patterns/role-guarded-routes.md) | Auth/role guards in both routers |
| [patterns/openapi-client-consumption.md](patterns/openapi-client-consumption.md) | Generated OpenAPI client + TanStack Query |
| [patterns/forms-rhf-zod.md](patterns/forms-rhf-zod.md) | React Hook Form + Zod, React 19 actions |
| [patterns/testing-vitest-playwright.md](patterns/testing-vitest-playwright.md) | Vitest, Testing Library, Playwright auth reuse |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Versions, commands, decision matrix

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Server state vs UI state** | Query cache owns server data; React state owns UI-only data |
| **Config in CSS (Tailwind v4)** | `@import "tailwindcss"` + `@theme` instead of a JS config |
| **Client guards are UX only** | Authorization is enforced by the API |
| **Generated client** | Types come from the OpenAPI spec; never hand-edit |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/toolchain-vite-tailwind.md, concepts/react19-typescript.md |
| **Intermediate** | concepts/server-state-tanstack-query.md, patterns/forms-rhf-zod.md |
| **Advanced** | patterns/role-guarded-routes.md, patterns/openapi-client-consumption.md, patterns/testing-vitest-playwright.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| react-frontend-specialist | all concepts and patterns | Build screens, routing, forms, charts, tests |
| fastapi-backend-specialist | patterns/openapi-client-consumption.md | Keep API schema consumable by the generated client |
| aws-app-platform-specialist | concepts/toolchain-vite-tailwind.md (env vars, build) | Static build output and build-time env handling |

## Related Domains

[javascript](../javascript/index.md) , [testing](../testing/index.md) , [pydantic](../pydantic/index.md)

## Scope Notes

Version facts reflect npm and official docs on 2026-10-02 and move quickly; re-check before pinning.
Claims labeled "practitioner note" are not from official docs. Research log kept by the KB builder.
