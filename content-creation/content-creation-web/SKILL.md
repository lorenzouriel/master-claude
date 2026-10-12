---
name: content-creation
description: >-
  Lorenzo's content OS (claude.ai web build, state in Google Drive) for
  Data/AI Engineering content on Medium, LinkedIn, Instagram, and X. Use whenever the user asks to
  write or edit a Medium article or lab, LinkedIn post or comment, tweet, X
  thread or reply, Instagram carousel or Reel script, long-form essay (EN/PT),
  thumbnail prompt, headline, CTA, bio, or page copy; to check if text sounds
  AI-written; for SEO, Medium tags, or GEO/AEO; to research a topic or get
  news in his area; for a daily dossier; to schedule via Buffer; to manage the
  pipeline or plan the week; to analyze post performance or run a weekly
  review; to repurpose a piece; or to archive content. Also triggers on "turn
  this into an article", "make this sound human", "give me a hook", "reply to
  this tweet", "what should I post today", "plan my week", "how did my posts
  do", "send to Buffer", "rewrite my bio", "will this rank".
---

# Content Creation OS (router, web build)

This is the claude.ai web build. All state (pipeline, metrics, drafts,
archive, saved corrections) lives in Google Drive under `content-os/`; see
`references/shared/storage.md`. The Claude Code build (`content-creation`)
is the source of truth for module text.

This file dispatches. It writes nothing itself. It picks the module, reads that
module's file in full, and follows it as if it had triggered directly.

## Always load first

Before any module:

0. Check that the Google Drive connector is enabled. If not, say that nothing
   can be saved this session and continue only for tasks that don't need
   state (writing, humanizing, research without saving).

Then read:

1. `references/shared/memory/company.md`, who Lorenzo is and what he sells
2. `references/shared/memory/preferences.md`, voice and banned patterns
3. `references/shared/memory/strategy.md`, current focus, channels, weekly shape
4. `references/shared/pillars.md`, content pillars, audience, cadence, slot map
5. `references/shared/storage.md`, Drive folder IDs and the read/rewrite protocol
6. `memory-overrides.md` in the Drive `content-os/` root (lookup per storage.md).
   Each row overrides the named skill file. A row beats the skill's own
   memory when they disagree.

Load on demand (not every time):

- `references/shared/platform-rules.md`: algorithm and format rules for the
  four channels. Writing, planning, and Buffer modules read it.
- `references/shared/identity/design-guide.md`: before any visual. Logos and
  covers in `identity/assets/`, shareable brand book in `identity/brand-book/`.
- `references/shared/channel-strategy/linkedin.md` and `x.md`: only for
  strategy reviews, profile optimization, or diagnosing stalled reach.

Module-specific rules override these only where the module says so.

## Lifecycle

```
research → plan → write → humanize + SEO → visual → publish → measure → archive → repurpose
topic-research   content-pipeline   writing modules   humanizer, seo   ig-carousel, diagrams
news-radar       daily-dossier                                          buffer   content-analytics
                                                                                 weekly-review   archive
```

## Modules

### Intel

| Module | Path | Use for |
|---|---|---|
| `news-radar` | `references/intel/news-radar/news-radar.md` | Scan and rank news/releases in Lorenzo's area, with post angles. |
| `topic-research` | `references/intel/topic-research/topic-research.md` | Deep 30-day research on one topic across Reddit, HN, web, and X, ending in content angles. |
| `daily-dossier` | `references/intel/daily-dossier/daily-dossier.md` | Morning brief: news, calendar, queue per channel, pipeline, today's ideas, LinkedIn and X engagement targets. |

### Writing

| Module | Path | Use for |
|---|---|---|
| `medium-tech-article` | `references/writing/medium-tech-article/medium-tech-article.md` | Medium technical articles: labs, tutorials, guides, playbooks; turning notes/docs/command dumps into an article. |
| `linkedin-post` | `references/writing/linkedin-post/linkedin-post.md` | New LinkedIn post from scratch, F1-F10 hook formulas. |
| `linkedin-comment-drafter` | `references/writing/linkedin-comment-drafter/linkedin-comment-drafter.md` | Comment on someone else's LinkedIn post from a URL. |
| `x-post` | `references/writing/x-post/x-post.md` | Single tweet or thread opener, T1-T10 hook formulas. |
| `x-thread` | `references/writing/x-thread/x-thread.md` | Full X thread, usually the Wednesday Medium recap. |
| `x-reply-drafter` | `references/writing/x-reply-drafter/x-reply-drafter.md` | Reply to or quote someone else's X post from a link or pasted text. |
| `ig-carousel` | `references/writing/ig-carousel/ig-carousel.md` | Carousels and single visual posts (Instagram, LinkedIn PDF document posts), rendered to PNG, then finalized to PDF. |
| `ig-reel-script` | `references/writing/ig-reel-script/ig-reel-script.md` | Instagram Reel script with timing, on-screen text, spoken lines. |
| `newsletter-humana` | `references/writing/newsletter-humana/newsletter-humana.md` | Long-form posts, newsletter-style essays (EN or PT), "make this sound more human" on long text. |
| `copywriting` | `references/writing/copywriting/copywriting.md` | Headlines and titles, CTAs, the four bios, portfolio/consulting/SaaS page copy. |
| `seo` | `references/writing/seo/seo.md` | Keyword research, on-page package for Medium (title, meta, tags, slug), topic clusters, GEO/AEO scoring. |
| `thumbnail-prompt` | `references/writing/thumbnail-prompt/thumbnail-prompt.md` | Image-gen prompt for an article thumbnail in the locked duotone-violet style. |
| `repurpose` | `references/writing/repurpose/repurpose.md` | One finished piece into the Wednesday set and follow-ups across LinkedIn, X, and Instagram. |

### Ops

| Module | Path | Use for |
|---|---|---|
| `content-pipeline` | `references/ops/content-pipeline/content-pipeline.md` | Idea backlog, status tracking (idea → published), weekly plan, theme week, pillar balance. |
| `buffer` | `references/ops/buffer/buffer.md` | Schedule, queue, publish, edit, delete posts on LinkedIn, Instagram, X; list channels/queue; Buffer ideas. The only publishing path. Medium is published by hand. |
| `archive` | `references/ops/archive/archive.md` | Import past Medium/LinkedIn/X/Instagram content; file newly published pieces into `data/archive/`. |

### Analytics

| Module | Path | Use for |
|---|---|---|
| `content-analytics` | `references/analytics/content-analytics/content-analytics.md` | Ingest LinkedIn/X/Instagram/Medium/Buffer stats, report what works per platform (formulas, pillars, timing). |
| `weekly-review` | `references/analytics/weekly-review/weekly-review.md` | Friday review: shipped vs. the 16-slot plan, metrics, next week's plan. |

### Shared services (not routed to directly, used by modules)

| Service | Path | Use for |
|---|---|---|
| Humanizer | `references/shared/humanizer/humanizer.md` (+ `platform-scrub-rules.md`, `voice-fingerprint.md`) | AI-tell removal for every published text. Routed directly only for "does this sound like AI?" (`audit` mode) or "humanize this" on a pasted text with no other task. |
| Diagrams | external skills (see below) | Tuesday concept-explainer diagrams. |

## Routing logic

Check in order, first match wins:

1. Thumbnail/cover/header image prompt → `thumbnail-prompt`.
2. Pasted LinkedIn post URL + comment/engage/reply → `linkedin-comment-drafter`.
3. Pasted X/Twitter link (x.com, twitter.com) + reply/respond/quote/engage → `x-reply-drafter`.
4. "Daily dossier", "morning brief", "what should I post today", "brief me" → `daily-dossier`.
5. "Research <topic>", "what are people saying about", "last 30 days on", "is <topic> worth writing about" → `topic-research`.
6. News, releases, "what's new in X", trends in his area, without asking for a full brief → `news-radar`.
7. Stats, metrics, performance, "how did my posts do", uploaded LinkedIn/X/Instagram/Medium export → `content-analytics`.
8. "Weekly review", "how was my week" → `weekly-review`.
9. Backlog, ideas list, "add this idea", status of drafts, content calendar, "plan my week", "theme week" → `content-pipeline`.
10. "Archive", "import my Medium/LinkedIn/tweets", "save my old content", "file what I published" → `archive`.
11. "Repurpose", "turn this article into posts", "spin this off", "the Wednesday set" → `repurpose`.
12. SEO, keywords, "will this rank", meta description, Medium tags, slug, topic cluster, GEO, AEO, "optimize for AI" → `seo`.
13. Headline or title options, CTA, bio (X, LinkedIn headline/About, Instagram, Medium), landing/portfolio/about/services page copy → `copywriting`.
14. "Does this sound like AI?", "check this for AI tells" → humanizer in `audit` mode. "Humanize this" on pasted text with no other task → humanizer (`full` for long text, `quick` for short).
15. Reel, short vertical video script → `ig-reel-script`.
16. Carousel, slides for LinkedIn/Instagram, visual single post, "finalize carousel", "carousel to PDF" → `ig-carousel`.
17. Thread, "turn this into a thread" → `x-thread`.
18. Tweet, X post, hook for X → `x-post`.
19. New LinkedIn post, hook for LinkedIn → `linkedin-post`.
20. Newsletter-style essay, long-form personal post, PT long-form, "make this more human" on long text the user wants rewritten in his voice → `newsletter-humana`.
21. Medium article, lab, tutorial, guide, "turn these notes into an article" → `medium-tech-article`.
22. Schedule / queue / publish / "send to Buffer" finished copy, or manage the queue → `buffer`.
23. Diagram for a concept explainer, architecture diagram, "draw this" → build it as an HTML/SVG Artifact styled with `references/shared/identity/design-guide.md` (monochrome, Inter / JetBrains Mono), sized 1080x1350 for Instagram/LinkedIn and 1600x900 for X, with print CSS so it saves as a PDF; convert to PNG with the code tool if available. For the fuller diagram library, use the `diagram-design` skill in the Claude Code build.

If "write a post about X" names no platform, ask one short question: LinkedIn
post, X post or thread, Instagram carousel, Medium article, or the full set
for all four. Voice, length, and structure differ too much to guess.

## Chained workflows

Some requests span modules. Run them in this order, passing the output forward,
and stop at every approval checkpoint the modules define.

| Request | Chain |
|---|---|
| "Write and schedule a LinkedIn post about X" | `linkedin-post` → `buffer` |
| "Tweet this" / "write and schedule a tweet" | `x-post` → `buffer` |
| "Write the article" (Wednesday anchor) | `medium-tech-article` → `seo` (on-page, optional geo) → `thumbnail-prompt` |
| "Do the Wednesday set" / "repurpose this article" | `repurpose` → `linkedin-post` + `x-thread` + `ig-carousel` → `buffer` |
| "Post about today's news" / pick from dossier | `news-radar` (or the dossier item) → `linkedin-post` and/or `x-post` → `buffer` |
| "Plan my week" | `content-pipeline` (weekly plan or theme week), reading `strategy.md` and the slot map |
| "Tuesday explainer" | diagram (route 23) → `linkedin-post` + `ig-carousel` + `x-post` with the diagram attached → `buffer` |
| "Research X and write about it" | `topic-research` → `seo` (research) → `medium-tech-article` |
| Carousel approved | `ig-carousel` Step 7 (finalize to PDF) → `buffer` |
| Anything written that the user approves | log it in `content-pipeline` (status `drafted`, or `scheduled` after Buffer confirms) |
| Anything marked `published` | `archive` files it into `data/archive/` |

Pipeline logging is automatic: when a writing module produces approved copy, or
Buffer confirms a scheduled post, update the pipeline file per
`content-pipeline` without asking.

## Execution

1. Load the "always load first" files.
2. Pick the module (or chain) above.
3. Read the module file in full, plus any files under its own `references/`
   folder exactly as it instructs.
4. Follow it. Don't mix structural rules across writing modules: each has its
   own non-negotiables (e.g. medium-tech-article's lab skeleton,
   thumbnail-prompt's locked visual style).
5. Every text that will be published passes
   `references/shared/humanizer/humanizer.md` with its platform layer (`full`
   for long-form, `quick` or the module's own checklist for short-form).

## Global non-negotiables

- No em dashes, no emojis, no guru or corporate vocabulary (see preferences).
- English by default. Portuguese or Spanish only when the user asks.
- Never publish without an explicit yes. Only Buffer publishes (Medium is
  published by Lorenzo by hand).
- No links in the body of LinkedIn posts or tweets (first comment / first reply).
- Never invent numbers, quotes, metrics, or news. If a source can't be fetched,
  say so.

## Keeping memory current

Lorenzo's context lives in `references/shared/memory/` and must not go stale.

- **Learn from corrections.** When Lorenzo corrects something in a way that
  sounds permanent ("don't do this anymore", "I prefer...", "always...",
  "next time..."), ask: "Do you want me to save this so you don't have to
  repeat it?" On yes, add one row to `memory-overrides.md` in Drive (the skill
  files are read-only on web), using the storage rewrite protocol, and show
  the row. The `Overrides` column names the file the rule belongs to:
  voice and style → `preferences.md`; business, clients, offer →
  `company.md`; focus, channels, cadence, deadlines → `strategy.md` /
  `pillars.md`; colors, fonts, logos → `identity/design-guide.md`.
- **Fold overrides back.** When `memory-overrides.md` has 10+ rows, or when
  Lorenzo says he's updating the skill, remind him to apply the rows to the
  skill files in the Claude Code build, re-upload the web zip, and clear the
  table.
- **After a context change** (new channel, new client, changed cadence, new
  module), ask: "This changed your context. Update memory?" Show the row
  before saving it to `memory-overrides.md`. Don't reformat whole files.
- **Don't ask** for one-off tasks, simple questions, or corrections that only
  matter in the current conversation.
- **Repeated tasks.** If Lorenzo does the same unrouted task twice, offer to
  turn it into a module (see below).

## What runs where

| Task | Web (this build) | Needs the Claude Code build |
|---|---|---|
| Writing, humanizing, SEO, copywriting, research, dossier, planning | Yes | |
| Pipeline, metrics, reviews, archive of new pieces | Yes, in Drive | |
| Buffer scheduling | Yes, with the Buffer connector | |
| Carousels | Artifact → print to PDF → PNG via code tool | AI photos, automatic Playwright rendering |
| Archive imports | Up to 10 Medium articles or 30 posts per chat | Full back-catalog (Medium, LinkedIn via Apify, X archive) |
| Diagrams | HTML/SVG Artifacts | The `diagram-design` skill library |

Connectors this build expects: **Google Drive** (required for anything that
saves), **Buffer** (custom connector `https://mcp.buffer.com/mcp`, for
publishing), **Google Calendar** and **Gmail** (daily dossier), web search and
fetch. The code tool (code execution) is optional but unlocks PNG export,
logo embedding, and spreadsheet parsing.

## Maintaining this skill

Edit modules in the Claude Code build (`content-creation`) first, then port
the change here and re-upload the zip. Keep these web-only files different:
`SKILL.md`, `references/shared/storage.md`, `references/ops/archive/archive.md`,
`references/writing/ig-carousel/ig-carousel.md`, and the delivery steps in
`medium-tech-article`, `ig-reel-script`, `content-analytics`, `daily-dossier`.

Add a module: create `references/<area>/<name>/<name>.md` (plus its own
`references/` if needed), add a row to the right Modules table, and add a
routing rule above. Retire one: remove the row, the routing rule, and the
folder. Shared voice/identity/memory changes go in `references/shared/` only,
never copied into modules.
