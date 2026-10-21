---
name: research
description: >
  Intel hub for the owner's content: news scans, 30-day topic deep dives, and the morning
  brief. Trigger on: "what's new in X", "any news on", "trends this week", "research
  <topic>", "what are people saying about", "last 30 days on", "is X worth writing
  about", "daily dossier", "morning brief", "brief me", "what should I post today".
---

# Intel

Router for the `research` sub-skills. Pick the sub-skill, read its `SKILL.md`, and follow it. Paths inside sub-skills are relative to the project root (`context/...`, `data/...`), except each sub-skill's own `references/` and `scripts/`.

## Command Router

| Command | Sub-Skill | Use for |
|---|---|---|
| `/research news` | `news-radar/SKILL.md` | Scan and rank news, releases, and discussions in the owner's area, each with a post angle. |
| `/research deep` | `topic-research/SKILL.md` | Deep research on one topic over the last 30 days (Reddit, HN, web, X), cited briefing ending in content angles. |
| `/research dossier` | `daily-dossier/SKILL.md` | Morning brief: news with angles, calendar, Metricool planner and gaps, pipeline, three ready-to-write ideas, metrics pulse. |

If a request spans several sub-skills, run them in order and pass the output forward. Tie-breaks and chained workflows live in the project `CLAUDE.md`.
