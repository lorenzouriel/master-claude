# CreatorOS

A content operating system for one brand: research, plan, write, design,
edit video, schedule, measure, and archive across Instagram, LinkedIn, X,
TikTok, YouTube, and Medium. Open Claude Code in this folder to use it.

## First run

If `context/company.md` still starts with `<!-- creatoros:template -->`, the
workspace has not been set up. Before any other task, offer `/system install`
(about 20-30 minutes, resumable). A writing or design task on an unset
workspace stops and points there; never invent the brand, voice, or audience.

## Workspace

<!-- Filled by /system install (module 3). -->
- Brand: <name> · Owner: <first name>
- Active channels: <list>
- Content language: <language(s)> · Anchor piece: <format> on <day>

## Context (always loaded)

@context/company.md
@context/preferences.md
@context/strategy.md
@context/pillars.md
@context/accounts.md
@context/storage.md

Load on demand, not every time:

- `context/voice-samples.md`: real writing by the owner. Writing skills and
  the humanizer calibrate against it.
- `context/platform-rules.md`: algorithm and format rules per channel. Writing,
  planning, and Metricool skills read it.
- `brand/design-guide.md`: before any visual. Logos and fonts in
  `brand/assets/` and `brand/fonts/`, video colors in `brand/video-theme.json`,
  shareable brand book in `brand/brand-book/`, reference posts and videos in
  `brand/inspirations/`.
- `context/channel-strategy/linkedin.md` and `x.md`: only for strategy reviews,
  profile optimization, or diagnosing stalled reach.

Skill-specific rules override these only where the skill says so.

## Layout

| Path | What |
|---|---|
| `.claude/skills/` | 11 hubs (`system`, `content`, `research`, `analytics`, `linkedin`, `x`, `instagram`, `medium`, `visual`, `tiktok`, `youtube`). Each hub's `SKILL.md` routes to its sub-skill folders. Invoke as `/<hub> <command>` (`/linkedin post`, `/content humanize`) or in plain language. |
| `.claude/agents/` | Subagents for isolated, heavy work (research, analytics, editing, bulk archive). |
| `context/` | Who the owner is, voice, strategy, pillars, accounts, platform rules, storage. |
| `brand/` | Design guide, logos, fonts, video theme, brand book, inspirations. |
| `data/` | State: pipeline, metrics, news log, dossiers, reviews, SEO, research, archive. |
| `output/` | Drafts before they are published (articles, carousels, reels). |

## Lifecycle

```
setup → research → plan → write → humanize + SEO → visual → publish → measure → archive → repurpose
```

| Stage | Hub → sub-skills | Agent |
|---|---|---|
| Setup | `system` → `install`, `doctor`, `update` | (main thread) |
| Intel | `research` → `news-radar`, `topic-research`, `daily-dossier` | `researcher` |
| Writing | `medium` → `medium-tech-article`, `newsletter-humana`, `thumbnail-prompt`; `linkedin` → `linkedin-post`, `linkedin-comment-drafter`; `x` → `x-post`, `x-thread`, `x-reply-drafter`; `instagram` → `ig-carousel`, `ig-reel-script`; `tiktok`; `youtube`; `content` → `copywriting`, `seo`, `repurpose` | (main thread) |
| Visual | `visual` → `diagram-design`, `excalidraw-diagram`, `video-edit` (local engine, Claude Code only) | (main thread) |
| Quality | `content` → `humanizer` | `editor` |
| Ops | `content` → `content-pipeline`, `metricool`, `archive` | `archivist` (bulk imports) |
| Analytics | `analytics` → `content-analytics`, `weekly-review` | `analyst` |

Below, skills are named by sub-skill (`humanizer`, `metricool`); the table above
gives each one's hub.

Writing always runs in the main conversation: drafts go through approval
rounds, and a subagent can't hold that dialogue. Agents take the work that is
heavy, parallel, or benefits from a fresh read, and hand back one result.

## Routing tie-breaks

Hubs route themselves from their descriptions; the hub's router table picks
the sub-skill. When more than one fits:

1. "Install", "set up", "onboarding", "my logo changed", "change my pillars"
   → `system`. "Is everything set up?" → `doctor`.
2. Pasted LinkedIn post URL + comment/engage → `linkedin-comment-drafter`.
   Pasted x.com/twitter.com link + reply/quote → `x-reply-drafter`.
3. "What should I post today", "brief me" → `daily-dossier`, not `news-radar`.
   News without asking for a full brief → `news-radar`.
4. "Does this sound like AI?" → `humanizer` in `audit` mode. "Humanize this" on
   pasted text with no other task → `humanizer` (`full` for long, `quick` for
   short). "Make this more human" on long text to rewrite in the owner's voice
   → `newsletter-humana`.
5. Headline, CTA, bio, page copy → `copywriting`, even inside another task.
6. "Write a post about X" with no platform: ask one short question (which of
   the active channels, or the full set). Voice, length, and structure differ
   too much to guess.
7. "Reel script", "short video", "vertical video" with no platform →
   `ig-reel-script`. Only "TikTok" → `tiktok`; only "YouTube" or "Shorts" →
   `youtube`.
8. Medium or LinkedIn cover → `thumbnail-prompt`. YouTube thumbnail →
   `youtube` (`thumbnail` brief, `youtube-thumbnail` to generate). Article SEO →
   `seo`; video SEO and metadata → `youtube`.
9. A recorded video file + "edit", "cut the pauses", "add captions",
   "add motion", "reframe" → `video-edit`. Writing the script for it → rule 7.

## Diagrams

Concept explainers and "draw this": use the `diagram-design` skill (or
`excalidraw-diagram` for a hand-drawn look), styled with
`brand/design-guide.md`. Their palettes live in
`diagram-design/references/style-guide.md` and
`excalidraw-diagram/references/color-palette.md`; `/system install` rewrites
them from the design guide. Export 1080x1350 for Instagram/LinkedIn and
1600x900 for X.

## Chained workflows

Run in order, pass the output forward, stop at every approval checkpoint.
Skip rows for channels that aren't active (see Workspace).

| Request | Chain |
|---|---|
| "Write and schedule a LinkedIn post about X" | `linkedin-post` → `metricool` |
| "Tweet this" / "write and schedule a tweet" | `x-post` → `metricool` |
| "Write the article" (anchor piece) | `medium-tech-article` or `newsletter-humana` → `seo` (on-page, optional geo) → `thumbnail-prompt` |
| "Do the anchor set" / "repurpose this article" | `repurpose` → `linkedin-post` + `x-thread` + `ig-carousel` → `metricool` |
| "Post about today's news" / pick from dossier | `news-radar` (or the dossier item) → `linkedin-post` and/or `x-post` → `metricool` |
| "Plan my week" | `content-pipeline` (weekly plan or theme week) |
| Concept explainer | diagram → `linkedin-post` + `ig-reel-script` + `x-post` with the diagram attached → `metricool` |
| Reel / TikTok | `ig-reel-script` → `tiktok` script pass → the owner records → `video-edit` (`reel`) → `metricool` |
| YouTube video | anchor piece → `youtube` (`script` → `metadata` → `thumbnail`) → `youtube-thumbnail` → the owner records → `video-edit` (`youtube`, then `short`) |
| "Research X and write about it" | `researcher` agent (`topic-research`) → `seo` (research) → `medium-tech-article` |
| Carousel approved | `ig-carousel` Step 7 (finalize to PDF) → `metricool` |
| Long-form draft ready for review | `editor` agent → apply its fixes in the main thread |
| "Sync metrics" / "update my numbers" | `analyst` agent → `content-analytics` "Sync from Metricool" → `content-pipeline` "Mark published" → `archive` for newly published rows |
| Anything written that the owner approves | log it in `content-pipeline` (`drafted`, or `scheduled` after Metricool confirms) |
| Anything approved and scheduled (Metricool confirms, or the owner confirms a manual post) | `archive` moves it into `data/archive/` under the scheduled date; on `published`, only `url` is filled in |

Pipeline logging is automatic: when a writing skill produces approved copy, or
Metricool confirms a scheduled post, update the pipeline without asking.

## Global non-negotiables

- The avoid-list in `context/preferences.md` applies to everything published.
- Content language comes from `context/preferences.md`; conversation follows
  the language the owner writes in.
- Every text that will be published passes `humanizer` with its platform layer
  (`full` for long-form, `quick` or the skill's own checklist for short-form).
- Never publish without an explicit yes. Only Metricool publishes (channels
  Metricool can't post to are published by the owner by hand).
- No links in the body of LinkedIn posts or tweets (first comment / first reply).
- Never invent numbers, quotes, metrics, or news. If a source can't be fetched,
  say so.

## Keeping memory current

- **Learn from corrections.** When the owner corrects something in a way that
  sounds permanent ("don't do this anymore", "I prefer...", "always...",
  "next time..."), ask: "Do you want me to save this so you don't have to
  repeat it?" On yes, add one clear line to the right file and show it:
  voice and style → `context/preferences.md`; business, clients, offer →
  `context/company.md`; focus, channels, cadence, deadlines →
  `context/strategy.md` (and `context/pillars.md` if numbers changed);
  handles, connections → `context/accounts.md`; colors, fonts, logos →
  `/system update brand`; a rule for one skill → that skill's `SKILL.md`.
- **After a context change** (new channel, new offer, changed cadence, new
  skill), ask: "This changed your context. Update memory?" Show the line
  before saving. Don't reformat whole files.
- **Don't ask** for one-off tasks, simple questions, or corrections that only
  matter in the current conversation.
- **Repeated tasks.** If the owner does the same unrouted task twice, offer to
  turn it into a skill.

## Maintaining this workspace

- Add a sub-skill: `.claude/skills/<hub>/<name>/SKILL.md` (+ `references/`,
  `scripts/`), a row in the hub's Command Router, its trigger phrases in the
  hub's `description`, a mention in the Lifecycle table, and a tie-break above
  only if it overlaps another skill.
- Shared voice/brand/context changes go in `context/` or `brand/` only, never
  copied into skills.
- Paths in skills are relative to the project root (`context/...`,
  `data/...`), except a skill's own files (`references/...`, `scripts/...`),
  which are relative to its folder.
