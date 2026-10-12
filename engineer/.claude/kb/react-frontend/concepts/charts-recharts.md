# Charts with Recharts

> **Purpose**: Basic Recharts 3.x usage for dashboard charts
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

Recharts (npm 3.10.x) builds charts from composable React components over SVG. Data is an array of
objects; each series component references a key via `dataKey`. Wrap charts in `ResponsiveContainer`
for fluid sizing.

## The Concept

```tsx
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from 'recharts'

const data = [{ month: 'Jan', total: 120 }, { month: 'Feb', total: 98 }]

export function MonthlyChart() {
  return (
    <div className="h-72 w-full">{/* parent must have a defined size */}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis width="auto" />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="total" stroke="#2563eb" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
```

## Quick Reference

| Item | Fact |
|------|------|
| `ResponsiveContainer` | Uses ResizeObserver on the parent; parent needs defined width and height; `width`/`height` default `"100%"`; optional `aspect`, `maxHeight`, `minHeight` |
| Typical composition | Chart (`LineChart`/`BarChart`/`AreaChart`) + `XAxis`/`YAxis`/`CartesianGrid`/`Tooltip`/`Legend` + series |
| `accessibilityLayer` | Default `true` in 3.x (was `false` in 2.x); adds ARIA roles/labels and arrow-key navigation |
| Migration | A 3.0 migration guide exists on the Recharts wiki; check it when upgrading from 2.x |
| Dev tooling | Optional `RechartsDevtools` component for inspecting chart state |

## Common Mistakes

### Wrong

```tsx
<ResponsiveContainer><LineChart .../></ResponsiveContainer>   // parent has no height: renders empty
```

### Correct

```tsx
<div className="h-72"><ResponsiveContainer width="100%" height="100%">...</ResponsiveContainer></div>
```

Also: memoize or derive chart data outside render when large; feed it from TanStack Query `select`.

## Related

- [Accessibility](accessibility-basics.md) , [Server state](server-state-tanstack-query.md)

## Sources

- https://recharts.github.io/en-US/guide/getting-started/ , https://recharts.github.io/en-US/api/ResponsiveContainer/
- https://github.com/recharts/recharts/wiki/Recharts-and-accessibility ; npm registry version 3.10.1 (2026-10-02)
