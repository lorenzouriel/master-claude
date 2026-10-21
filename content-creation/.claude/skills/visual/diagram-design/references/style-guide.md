# Style Guide

**The single source of truth for colors, typography, and tokens.** Every diagram draws from this — not from hex values inlined in other reference files. If you want to change the visual skin of Diagram Design, change this file.

Skin: **The owner's brand** (from `brand/design-guide.md`). Monochromatic: soft-grey paper, near-black ink, grey strokes. No hue anywhere. The focal role is carried by pure black (white in dark mode) and a stronger stroke, not by color.

To generate your own from a website URL, see [`onboarding.md`](onboarding.md).

---

## Tokens

### Semantic roles

Every token is referred to by **semantic role**, not by its hex value. Type references (`type-*.md`) and SKILL.md say `accent`, not `#f7591f`.

| Role | Purpose | Light | Dark |
|---|---|---|---|
| `paper` | Page background, default node fill | `#F5F5F5` (soft background) | `#000000` (background) |
| `paper-2` | Diagram container bg, secondary fill | `#EFEFEF` (slightly darker) | `#1A1A1A` (near-black softened) |
| `ink` | Primary text, primary stroke | `#1A1A1A` | `#CFCFCF` (highlight variation) |
| `muted` | Secondary text, default arrow stroke | `#5F5F5F` (primary) | `#BFBFBF` (light stroke) |
| `soft` | Sublabels, boundary labels | `#8A8A8A` | `#8A8A8A` |
| `rule` | Hairline borders | `#EFEFEF` | `rgba(191,191,191,0.18)` |
| `rule-solid` | Stronger borders, baselines | `#BFBFBF` | `rgba(191,191,191,0.35)` |
| `accent` | Focal / 1-2 max per diagram (use with `stroke-strong`) | `#000000` | `#FFFFFF` |
| `accent-tint` | Fill for accent-bordered boxes | `rgba(0,0,0,0.06)` | `rgba(255,255,255,0.08)` |
| `link` | HTTP/API calls, external arrows (draw dashed `4,3` to separate from `muted`) | `#606060` | `#CFCFCF` |

> **Brand palette source:** `brand/design-guide.md`. Primary `#5F5F5F` / `#606060` / `#626262`, light backgrounds `#FFFFFF` / `#F5F5F5` / `#EFEFEF`, dark `#000000` / `#1A1A1A` / `#BFBFBF` / `#CFCFCF`. `ink #1A1A1A` (light), `soft #8A8A8A`, and the pure black/white accent are derived to give hierarchy and a focal signal without adding a hue. If the design guide changes, update this table to match.

> **Note:** The pre-baked example HTML files in `assets/` were built under an earlier skin. Use them for layout only, never for colors.

### Inversion rule (light → dark)

Any `rgba(0,0,0, X)` in light becomes `rgba(255,255,255, X)` in dark. Same opacities, RGB flipped.

### Series palette (multi-series chart types only)

A small set of desaturated, editorial-tone colors for chart types that genuinely need to distinguish multiple overlapping entities (currently: **radar**). The "1-focal" rule still holds — `accent` is reserved for the focal series; the palette below covers the rest.

| Token | Light | Dark | Notes |
|---|---|---|---|
| `series-1` | `#5F5F5F` | `#BFBFBF` | Non-focal series, solid stroke |
| `series-2` | `#8A8A8A` | `#8A8A8A` | Non-focal series, dashed `4,3` |
| `series-3` | `#BFBFBF` | `#5F5F5F` | Non-focal series, dotted `1,3` |
| `series-4` | `#626262` | `#CFCFCF` | Non-focal series, dash-dot `6,2,1,2` |
| `series-5` | `#A6A6A6` | `#737373` | Non-focal series, long dash `8,4` |

Grey values alone don't separate five series, so each series also gets its own dash pattern. Fills sit at `0.18` opacity light, `0.22` dark; strokes use the full color. **Don't backfill these tokens to non-chart types** — architecture, swimlane, etc. continue to use muted-ink variants. The series palette is opt-in for diagrams where overlapping shapes demand distinguishable color, not a license to add color elsewhere.

### Terminal skin (opt-in alternate)

A self-contained palette for the terminal-window primitive (see [primitive-terminal.md](primitive-terminal.md)) — a CLI-chrome register for dev-tool posts and technical social cards. It does not replace the default skin above and isn't affected by onboarding; it's a second, fixed skin you opt into per-diagram.

| Token | Hex | Purpose |
|---|---|---|
| `terminal-page` | `#0a0a0a` | Page background behind the window |
| `terminal-paper` | `#141414` | Window body, node fill |
| `terminal-bar` | `#1b1b1b` | Titlebar strip |
| `terminal-border` | `#2b2b2b` | Window border, hairlines |
| `terminal-ink` | `#f5f5f5` | Primary text, primary stroke (same white-smoke as default `ink`) |
| `terminal-muted` | `#9a9a9a` | Secondary text, sublabels, ring stroke |
| `terminal-soft` | `#5c5c5c` | Tertiary — inactive dots, spokes |
| `terminal-accent` | `#ff5a36` | The one accent — focal station, prompt sign, active dot |
| `terminal-accent-tint` | `rgba(255,90,54,0.12)` | Fill for accent-bordered boxes |

**1-accent rule still holds.** Everything that isn't `terminal-ink` or `terminal-muted`/`terminal-soft` should be `terminal-accent` — never introduce a second hue.

---

## Typography

| Role | Family | Size | Weight | Usage |
|---|---|---|---|---|
| `title` | Fraunces | 1.75rem | 400 | Page H1 |
| `node-name` | Inter (sans) | 12px | 600 | Human-readable labels |
| `sublabel` | JetBrains Mono | 9px | 400 | Port, protocol, URL, field type |
| `eyebrow` | JetBrains Mono | 7-8px | 500, tracked 0.18em, uppercase | Type tags, axis labels |
| `arrow-label` | JetBrains Mono | 8px | 400, tracked 0.06em | Arrow annotations |
| `callout` | Fraunces *italic* | 14px | 400 | Editorial asides only |

### Font stack

```html
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

**Load-bearing rule:** Mono is for *technical* content and labels (ports, commands, URLs, field types, eyebrows), matching the brand's metadata role for JetBrains Mono. Names go in Inter. Page title is Fraunces. Italic Fraunces is reserved for annotation callouts (see [primitive-annotation.md](primitive-annotation.md)).

---

## Stroke, radius, spacing

| Token | Value | Use |
|---|---|---|
| `stroke-thin` | `0.8` | Tag-box outlines, leaf nodes |
| `stroke-default` | `1` | Most strokes |
| `stroke-strong` | `1.2` | Emphasis strokes |
| `radius-sm` | `4` | Small tags |
| `radius-md` | `6` | Node boxes |
| `radius-lg` | `8` | Containers, rings |
| `grid` | `4` | Every coord, size, and gap is divisible by 4 (hard rule) |

---

## Node type → treatment

Semantic role combinations — reference these by name in type specs.

| Type | Fill | Stroke |
|---|---|---|
| `focal` (1–2 max) | `accent-tint` | `accent` |
| `backend` | `#FFFFFF` (pure white; `#1A1A1A` in dark) | `ink` |
| `store` | `ink @ 0.05` | `muted` |
| `external` | `ink @ 0.03` | `ink @ 0.30` |
| `input` | `muted @ 0.10` | `soft` |
| `optional` | `ink @ 0.02` | `ink @ 0.20` dashed `4,3` |
| `security` | `accent @ 0.05` | `accent @ 0.50` dashed `4,4` |

---

## Customizing the skin

Four options:

1. **Run onboarding** — see [`onboarding.md`](onboarding.md). Drop a URL; the skill extracts the palette + fonts and rewrites this file.
2. **Edit by hand** — change the hex values in the tables above. Run the pre-output taste gate afterward to verify the accent still reads as "focal" against the new paper color.
3. **Brand handoff** — paste your existing design-token JSON into a new section here and map its tokens to the semantic roles above.
4. **Client profiles** — save and switch named skins, or bind one to a project, using [`profiles.md`](profiles.md).

### Constraints (don't break these)

- **Contrast**: `ink` must hit WCAG AA on `paper`. `muted` must hit AA on `paper` for 11px+ text.
- **One accent**: this brand's accent is pure black / white plus `stroke-strong`. Never introduce a hue.
- **No rainbow palette**: if your brand ships 8 colors, pick 3 (paper, ink, accent). The rest become `muted` variants.
- **Serif + sans + mono**: three families, not more. If brand typography is all sans, keep a serif (here Fraunces) for `title` and `callout` anyway — the contrast is load-bearing.
- **Paper is soft grey, not pure white**: `#F5F5F5` per the brand. Pure white is reserved for `backend` node fills.
- **Dot pattern is optional, not default**: the 22×22 dot pattern is an opt-in "dotted paper" variant (good for long-form editorial hero diagrams). The default background is a clean `paper` fill, no pattern. When the pattern is enabled, it should sit at ~10% opacity of `ink` on `paper` — visible but quiet.
- **Container is clean by default**: the diagram sits directly on the page paper, no secondary container background or border. A framed variant (`paper-2` bg + `rule` border + 8px radius + padding) is available as an opt-in for card-heavy layouts, but don't reach for it by default — the extra chrome fights the figure.
