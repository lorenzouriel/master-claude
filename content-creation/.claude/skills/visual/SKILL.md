---
name: visual
description: >
  Diagram hub for the owner's content, styled with brand/design-guide.md. Routes to
  branded HTML/SVG/PNG diagrams (architecture, flowchart, sequence, ER, data flow,
  medallion, charts, and 30+ more types) or hand-drawn Excalidraw diagrams. Trigger on:
  "draw this", "diagram", "Tuesday explainer", "architecture diagram", "flowchart",
  "sequence diagram", "data flow", "chart", "redraw this drawio / mermaid",
  "excalidraw", "hand-drawn diagram", "sketch this".
---

# Visual & Diagrams

Router for the `visual` sub-skills. Pick the sub-skill, read its `SKILL.md`, and follow it. Paths inside sub-skills are relative to the project root (`context/...`, `data/...`), except each sub-skill's own `references/` and `scripts/`.

## Command Router

| Command | Sub-Skill | Use for |
|---|---|---|
| `/visual diagram` | `diagram-design/SKILL.md` | Branded diagrams as standalone HTML/SVG/PNG; default for explainers. Palette in `references/style-guide.md`. |
| `/visual excalidraw` | `excalidraw-diagram/SKILL.md` | Excalidraw JSON for a hand-drawn look. Palette in `references/color-palette.md`. |
| `/visual edit` | `video-edit/SKILL.md` | Edit a recorded Reel, TikTok, or YouTube video with the local vedit engine: cuts, branded captions, audio, reframe, per-platform export. Claude Code only. |

If a request spans several sub-skills, run them in order and pass the output forward. Tie-breaks and chained workflows live in the project `CLAUDE.md`.
