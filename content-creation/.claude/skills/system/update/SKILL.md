---
name: update
description: Re-run one CreatorOS install module (company, voice, strategy, brand, tools, import) without touching the rest. Use for "/system update brand", "new logo", "change my pillars", "update my voice", "connect Metricool", "add a channel".
---

# /system update <module>

Runs one module of `../install/SKILL.md` against files that are already
filled. Same questions, but each one shows the current value first and
accepts "keep".

| Module | Install module | Files it rewrites |
|---|---|---|
| `company` | 1 | `context/company.md`, `context/accounts.md` (handles) |
| `voice` | 2 | `context/voice-samples.md` (append, never delete samples), `context/preferences.md`, humanizer voice references |
| `strategy` | 3 | `context/strategy.md`, `context/pillars.md`, news-radar `sources.md`, `CLAUDE.md` Workspace block |
| `brand` | 4 | `brand/design-guide.md`, `brand/video-theme.json`, diagram palettes, brand book HTML + PDF |
| `tools` | 5 | `context/accounts.md` (Metricool, keys) |
| `import` | 6 | `data/archive/`, `data/metrics/` |

No module named: ask which, or suggest the one `/system doctor` flags first.

## Rules

- Show a diff of every file before writing it; write after a yes.
- A brand change regenerates everything downstream in the same run (video
  theme, diagram palettes, brand book), so they never disagree.
- A channel added in `strategy` triggers the Metricool check from `tools`.
- Never delete archive, metrics, or pipeline rows.
