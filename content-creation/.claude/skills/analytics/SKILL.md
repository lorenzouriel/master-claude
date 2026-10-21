---
name: analytics
description: >
  Analytics hub for the owner's content: sync metrics from Metricool into the CSVs,
  ingest platform exports, and run the Friday review. Trigger on: "sync metrics",
  "update my numbers", "pull my stats", "how did my posts do", "analyze my LinkedIn stats", "what's
  working", an uploaded LinkedIn / X / Instagram / Medium / Metricool export, "weekly
  review", "how was my week", "review and plan next week".
---

# Analytics

Router for the `analytics` sub-skills. Pick the sub-skill, read its `SKILL.md`, and follow it. Paths inside sub-skills are relative to the project root (`context/...`, `data/...`), except each sub-skill's own `references/` and `scripts/`.

## Command Router

| Command | Sub-Skill | Use for |
|---|---|---|
| `/analytics sync` | `content-analytics/SKILL.md` | "Sync from Metricool": pull posts and followers for LinkedIn, X, Instagram, TikTok, YouTube into `data/metrics/`, reconcile `data/pipeline.csv`. |
| `/analytics report` | `content-analytics/SKILL.md` | Ingest exports into `data/metrics/` and report what works: hooks, pillars, formats, times, follower growth. |
| `/analytics weekly` | `weekly-review/SKILL.md` | Friday review: shipped vs. planned, numbers, pillar balance, lessons, next week's plan. |

If a request spans several sub-skills, run them in order and pass the output forward. Tie-breaks and chained workflows live in the project `CLAUDE.md`.
