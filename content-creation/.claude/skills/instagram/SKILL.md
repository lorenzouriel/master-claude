---
name: instagram
description: >
  Instagram hub for the owner. Routes to carousels and single visual posts (HTML rendered
  to 1080x1350 PNG, finalized to PDF) and Reel scripts. Trigger on: "carousel",
  "instagram post", "create image", "generate photo", "educational post", "/carousel",
  "Reel script", "short video", "vertical video", "script for Instagram".
---

# Instagram

Router for the `instagram` sub-skills. Pick the sub-skill, read its `SKILL.md`, and follow it. Paths inside sub-skills are relative to the project root (`context/...`, `data/...`), except each sub-skill's own `references/` and `scripts/`.

## Command Router

| Command | Sub-Skill | Use for |
|---|---|---|
| `/instagram carousel` | `ig-carousel/SKILL.md` | Carousel or single post in the brand identity, rendered via Playwright, with caption. Step 7 finalizes to PDF. |
| `/instagram reel` | `ig-reel-script/SKILL.md` | 15-60 s Reel script with timing, on-screen text, spoken lines, visual cues. The same video goes to TikTok on Tue/Thu. |

If a request spans several sub-skills, run them in order and pass the output forward. Tie-breaks and chained workflows live in the project `CLAUDE.md`.
