# Accessibility Basics

> **Purpose**: Practical accessibility rules for React forms, dashboards, and data-heavy UIs
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

WCAG 2.2 (W3C Recommendation, 2024-12-12) is organized by four principles: Perceivable, Operable,
Understandable, Robust, with conformance levels A, AA, AAA. AA is the commonly targeted level. The
ARIA Authoring Practices Guide's first rule: native HTML before ARIA; "No ARIA is better than bad
ARIA", because a role is a promise to implement the matching keyboard behavior.

## The Concept

```tsx
function Field({ id, label, error, ...props }: FieldProps) {
  const errId = `${id}-error`
  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <input id={id} aria-invalid={!!error} aria-describedby={error ? errId : undefined} {...props} />
      {error && <p id={errId} role="alert">{error}</p>}
    </div>
  )
}
// Use <button> for actions, <a>/<Link> for navigation; never <div onClick>.
```

## Quick Reference

| Criterion | Level | Requirement |
|-----------|-------|-------------|
| 1.4.3 Contrast (Minimum) | AA | Text contrast >= 4.5:1; large text (18pt, or 14pt bold) >= 3:1 |
| 2.4.7 Focus Visible | AA | Keyboard focus indicator must be visible |
| 3.3.1 Error Identification | A | Errors are identified and described in text |

| Practice | Why |
|----------|-----|
| Every input has a `<label>` | Accessible name; Testing Library `getByLabelText` and Playwright `getByLabel` rely on it |
| Do not remove `outline` without a replacement | Keeps focus visible |
| Do not use color alone to convey status | Pair with text/icon |
| Modals/menus: use native `<dialog>` or a vetted headless library | Focus trapping/restore is easy to get wrong |
| Charts | Recharts 3.x `accessibilityLayer` is on by default (arrow-key navigation, ARIA roles); provide a text/table alternative for key data (practitioner note: wiki gives no text-alternative guidance) |

New in WCAG 2.2 (selection): Focus Not Obscured, Target Size (Minimum), Dragging Movements,
Accessible Authentication, Redundant Entry, Consistent Help.

## Common Mistakes

### Wrong

```tsx
<div role="button" onClick={save}>Save</div>   // no keyboard behavior, promise broken
```

### Correct

```tsx
<button type="button" onClick={save}>Save</button>
```

Role-based test queries (`getByRole`) double as an accessibility check: if an element cannot be
found by role and name, assistive tech likely cannot find it either.

## Related

- [Forms](../patterns/forms-rhf-zod.md) , [Testing](../patterns/testing-vitest-playwright.md) , [Charts](charts-recharts.md)

## Sources

- https://www.w3.org/TR/WCAG22/ ; https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/
- https://github.com/recharts/recharts/wiki/Recharts-and-accessibility
