# Color Palette & Brand Style

**This is the single source of truth for all colors and brand-specific styles.** It follows `brand/design-guide.md` (the owner's brand): monochromatic, no hue anywhere. If the design guide changes, update this file to match.

Because there is no hue, meaning is carried by **grey value, stroke weight, and stroke style** (solid, dashed, dotted). Always pair the fill with the stroke style listed.

---

## Shape Colors (Semantic)

| Semantic Purpose | Fill | Stroke | Stroke style |
|------------------|------|--------|--------------|
| Primary/Neutral | `#EFEFEF` | `#1A1A1A` | solid, width 2 |
| Secondary | `#F5F5F5` | `#5F5F5F` | solid, width 2 |
| Tertiary | `#FFFFFF` | `#BFBFBF` | solid, width 1 |
| Start/Trigger | `#FFFFFF` | `#1A1A1A` | solid, width 4 |
| End/Success | `#1A1A1A` | `#000000` | solid, width 2 (white text) |
| Warning/Reset | `#F5F5F5` | `#5F5F5F` | dashed, width 2 |
| Decision | `#EFEFEF` | `#5F5F5F` | solid, width 2 (diamond shape) |
| AI/LLM | `#5F5F5F` | `#1A1A1A` | solid, width 2 (white text) |
| Inactive/Disabled | `#FFFFFF` | `#BFBFBF` | dashed, width 1 |
| Error | `#FFFFFF` | `#000000` | dotted, width 3 |

**Rule**: always pair a darker stroke with a lighter fill, except End/Success and AI/LLM, which are dark fills with white text. Never introduce a hue.

---

## Text Colors (Hierarchy)

| Level | Color | Use For |
|-------|-------|---------|
| Title | `#000000` | Section headings, major labels |
| Subtitle | `#1A1A1A` | Subheadings, secondary labels |
| Body/Detail | `#5F5F5F` | Descriptions, annotations, metadata |
| On light fills | `#1A1A1A` | Text inside light shapes |
| On dark fills | `#FFFFFF` | Text inside dark shapes |

Fonts: Excalidraw uses its own hand-drawn font. When exporting to HTML/SVG with a font choice, use Fraunces for titles, Inter for labels, JetBrains Mono for code and metadata.

---

## Evidence Artifact Colors

| Artifact | Background | Text Color |
|----------|-----------|------------|
| Code snippet | `#1A1A1A` | `#CFCFCF` (keywords `#FFFFFF`, comments `#8A8A8A`) |
| JSON/data example | `#1A1A1A` | `#CFCFCF` |

---

## Default Stroke & Line Colors

| Element | Color |
|---------|-------|
| Arrows | Stroke color of the source element's semantic purpose |
| Structural lines (dividers, trees, timelines) | `#5F5F5F` or `#BFBFBF` |
| Marker dots (fill + stroke) | `#1A1A1A` |

---

## Background

| Property | Value |
|----------|-------|
| Canvas background | `#F5F5F5` (light) or `#000000` (dark mode, then swap: strokes `#BFBFBF`, text `#CFCFCF`, fills `#1A1A1A`) |
