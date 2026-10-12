# Toolchain: Vite + Tailwind CSS v4

> **Purpose**: Current Vite and Tailwind v4 setup, env vars, and theming for a React SPA
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

As of 2026-10-02 Vite is on major 8 (npm 8.3.x), which bundles with Rolldown instead of the earlier
esbuild (dev) + Rollup (build) pair. Tailwind CSS is on 4.x and integrates through the first-party
`@tailwindcss/vite` plugin, configured in CSS (`@import`, `@theme`) rather than a JS config.

## The Concept

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  --color-brand-500: oklch(0.72 0.11 178);   /* generates bg-brand-500, text-brand-500 ... */
  --font-display: "Inter", sans-serif;
}
```

```bash
npm create vite@latest          # scaffold
npm install tailwindcss @tailwindcss/vite
```

## Quick Reference

| Item | Fact | Notes |
|------|------|-------|
| Node requirement (Vite 8) | 20.19+ or 22.12+ | Vitest 5 needs 22.12+ |
| `@vitejs/plugin-react` 6.x | peer `vite ^8` | v6 uses Oxc for Fast Refresh (not Babel) |
| `@tailwindcss/vite` 4.x | peer `vite ^5.2 \|\| ^6 \|\| ^7 \|\| ^8` | npm peerDependencies |
| `@theme` | Defines design tokens that create utilities | Use `:root` for plain CSS vars with no utility |
| `--color-*: initial;` | Clears the default palette namespace | Then define only your colors |
| `VITE_` prefix | Exposed to client via `import.meta.env` | Values are bundled: never put secrets |
| `.env` order | `.env`, `.env.local`, `.env.[mode]`, `.env.[mode].local` | Mode files win |
| Typing env vars | Augment `ImportMetaEnv` in `vite-env.d.ts` | |

## Common Mistakes

### Wrong

```tsx
// Tailwind scans source as plain text; interpolated names are never generated
<button className={`bg-${color}-600`} />
```

### Correct

```tsx
const variants = { blue: 'bg-blue-600 hover:bg-blue-500', red: 'bg-red-600 hover:bg-red-500' }
<button className={variants[color]} />
```

Other pitfalls: putting API keys in `VITE_*` variables; leaving `@source` unset for a UI library in
`node_modules` (default scan skips `node_modules`, `.gitignore`d files and CSS files; add
`@source "../node_modules/<lib>"`).

## Related

- [TypeScript and React 19](react19-typescript.md)
- [Testing](../patterns/testing-vitest-playwright.md)
- [Accessibility](accessibility-basics.md)

## Sources

- https://vite.dev/guide/ , https://vite.dev/blog/announcing-vite8 , https://vite.dev/guide/env-and-mode
- https://tailwindcss.com/docs/installation/using-vite , /docs/theme , /docs/detecting-classes-in-source-files
- npm registry peerDependencies for `@vitejs/plugin-react`, `@tailwindcss/vite` (checked 2026-10-02)
