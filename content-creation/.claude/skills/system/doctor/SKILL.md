---
name: doctor
description: Read-only health check of a CreatorOS workspace - unfilled templates, brand files, tools, Metricool connection, video engine. Use for /system doctor, "check my setup", "what's missing".
---

# /system doctor

Read-only. Installs nothing, writes nothing. One table, then the fixes.

## Checks

| Area | Check | Pass when |
|---|---|---|
| Context | `context/company.md`, `accounts.md`, `preferences.md`, `voice-samples.md`, `strategy.md`, `pillars.md` | no `<!-- creatoros:template -->` marker; count remaining `<...>` placeholders per file |
| Brand | `brand/design-guide.md` | no marker |
| Brand | logo files named in the design guide | each file exists in `brand/assets/` |
| Brand | `brand/brand-book/brand-book.pdf`, `brand/video-theme.json` | exist and are newer than `design-guide.md` |
| Brand | fonts in `video-theme.json` | each file resolves (video-edit `fonts/` or `brand/fonts/`) |
| Research | `.claude/skills/research/news-radar/sources.md` | no `<...>` placeholder rows left |
| Voice | `.claude/skills/content/humanizer/references/voice-fingerprint.md` | "Owner baseline" table has no template marker |
| Workspace | `CLAUDE.md` Workspace block | no `<...>` left |
| Metricool | tools present (ToolSearch "metricool") and `getBrandSettings` answers | brand blogId matches `accounts.md`; every active channel in `strategy.md` is a connected network |
| Carousels | `node --version` (18+), `npx playwright --version` | both answer |
| Video | `vedit.py doctor` (only if video is used per `strategy.md`) | prints `ready` |
| Keys | `.env` lists the keys `accounts.md` says are set | names present (never print values) |
| State | `data/pipeline.csv` | exists with the header from content-pipeline |

## Output

```markdown
### CreatorOS health

| Area | Status | Detail |
|---|---|---|
| Context | ok / 2 open | strategy.md: monthly themes; pillars.md: topic radar |
| ... | | |

Fix next: <the single most useful fix, with the command>
```

Then list every failing row with its fix: the `/system update <module>` that
fills it, or the exact command. Missing system tools get the official install
command for the OS; never run it from here.
