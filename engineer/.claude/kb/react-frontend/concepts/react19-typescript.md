# React 19 and Strict TypeScript

> **Purpose**: What React 19 adds and a strict TypeScript baseline for components
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

React 19.0 shipped 2024-12-05; the latest on react.dev is 19.3.0 (2026-09-09). TypeScript on npm
`latest` is 7.0.2 (native compiler, same `tsc` command); a project may still pin 5.x or 6.x. Enable
`strict` and keep `@types/react` / `@types/react-dom` aligned with the React major.

## The Concept

```jsonc
// tsconfig.json (app)
{
  "compilerOptions": {
    "target": "ES2022", "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext", "moduleResolution": "bundler",
    "jsx": "react-jsx", "strict": true,
    "noUncheckedIndexedAccess": true, "verbatimModuleSyntax": true,
    "isolatedModules": true, "noEmit": true, "skipLibCheck": true
  },
  "include": ["src"]
}
```

```tsx
interface BadgeProps { label: string; tone?: 'ok' | 'warn'; ref?: React.Ref<HTMLSpanElement> }

// React 19: ref is a regular prop on function components (no forwardRef)
function Badge({ label, tone = 'ok', ref }: BadgeProps) {
  return <span ref={ref}>{label}</span>
}
```

## Quick Reference

| React 19 feature | Use |
|------------------|-----|
| `useActionState(fn, init)` | Returns `[state, action, isPending]`; pass `action` to `<form action>` |
| `useOptimistic(value)` | Optimistic UI while an async request runs |
| `use(promise \| context)` | Read a promise/context in render (suspends) |
| `ref` as prop | Replaces `forwardRef` for function components |
| `<Context value>` | Replaces `<Context.Provider>` |
| `useFormStatus` | Pending state of the parent form without prop drilling |
| Document metadata | `<title>`, `<meta>`, `<link>` renderable in components |

| tsconfig flag | Effect |
|---------------|--------|
| `strict` | Enables noImplicitAny, strictNullChecks, strictFunctionTypes, useUnknownInCatchVariables, etc. |
| `noUncheckedIndexedAccess` | Index signatures yield `T \| undefined` (not part of `strict`) |
| `verbatimModuleSyntax` | Imports/exports preserved as written: use `import type` for types |
| `moduleResolution: bundler` | Bundler semantics (package `exports`/`imports`) |

## Common Mistakes

```tsx
// Wrong: any / unchecked catch
catch (e: any) { toast(e.message) }
// Correct: catch variables are unknown under strict
catch (e) { toast(e instanceof Error ? e.message : 'Unexpected error') }
```

Practitioner note (not from docs): React Router 8 requires React >= 19.2.7 (npm peer deps), so pin
React accordingly when choosing it. TS 7 removed some options (e.g. `baseUrl`); verify TS-version-specific options against the
installed compiler's tsconfig reference before copying older configs.

## Related

- [Toolchain](toolchain-vite-tailwind.md) , [Forms](../patterns/forms-rhf-zod.md)
- [javascript KB](../../javascript/index.md)

## Sources

- https://react.dev/versions , https://react.dev/blog/2024/12/05/react-19 , https://react.dev/learn/typescript
- https://www.typescriptlang.org/tsconfig/ ; npm dist-tags `typescript` (7.0.2 latest, checked 2026-10-02)
- TypeScript 7.0 (GA 2026-07-08; `tsc` kept; `baseUrl`, `target: es5`, `moduleResolution: node10` removed): https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ (fetched 2026-10-02)
