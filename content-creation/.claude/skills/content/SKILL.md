---
name: content
description: >
  Content quality and operations hub for the owner's content. Routes to sub-skills for
  conversion copy, humanizing, SEO/GEO, repurposing, the idea pipeline and weekly plan,
  Metricool scheduling and analytics, and the content archive. Trigger on: "write copy", "headline
  options", "CTA", "rewrite my bio", "landing page copy", "humanize this", "does this
  sound like AI", "SEO", "keywords for", "Medium tags", "GEO", "AEO", "repurpose this",
  "the anchor set", "add an idea", "plan my week", "what's drafted", "pillar
  balance", "schedule this", "send to Metricool", "queue", "archive my posts", "import my
  tweets", "file what I published".
---

# Content Ops & Quality

Router for the `content` sub-skills. Pick the sub-skill, read its `SKILL.md`, and follow it. Paths inside sub-skills are relative to the project root (`context/...`, `data/...`), except each sub-skill's own `references/` and `scripts/`.

## Command Router

| Command | Sub-Skill | Use for |
|---|---|---|
| `/content copy` | `copywriting/SKILL.md` | Headlines, titles, CTAs, first comments, profile bios (X, LinkedIn, Instagram, Medium), portfolio / consulting / SaaS page copy. |
| `/content humanize` | `humanizer/SKILL.md` | Remove AI tells from any text. Modes: `audit` ("does this sound like AI?"), `quick` (short-form), `full` (long-form). |
| `/content seo` | `seo/SKILL.md` | Keyword research, SERP check, on-page package for a Medium draft, topic clusters, GEO/AEO score and restructure. |
| `/content repurpose` | `repurpose/SKILL.md` | Turn one finished piece (usually the anchor article) into the platform set: LinkedIn, X thread, tweets, carousel, Reel, hooks. |
| `/content plan` | `content-pipeline/SKILL.md` | Idea backlog, status tracking, weekly or theme-week plan, pillar balance. Other sub-skills call it to log drafts. |
| `/content metricool` | `metricool/SKILL.md` | Schedule, draft, publish, or edit posts, and pull profile metrics, past posts, and best times through the Metricool connector. |
| `/content archive` | `archive/SKILL.md` | Import past Medium / LinkedIn / X content, or file approved and scheduled pieces into `data/archive/`. |

If a request spans several sub-skills, run them in order and pass the output forward. Tie-breaks and chained workflows live in the project `CLAUDE.md`.
