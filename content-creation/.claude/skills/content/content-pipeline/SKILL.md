---
name: content-pipeline
description: >-
  Idea backlog, status tracking, and weekly plan for the owner's content. Use when
  the user wants to add or list ideas, see what's drafted or scheduled, plan the
  week (or a theme week across the active channels), check pillar balance, or move a piece between statuses. Other modules
  call it to log drafts and scheduled posts.
---

# Content pipeline

One CSV tracks every piece from idea to published. Location per
`context/storage.md` (`data/pipeline.csv`).

## Schema

```
id,created,title,pillar,format,platform,status,formula,parent_id,source_url,draft_path,scheduled_at,published_at,metricool_id,post_url,notes
```

| Column | Values |
|---|---|
| `id` | `YYYYMMDD-NN` (creation date + counter that day) |
| `pillar` | `P1`-`P5` from `context/pillars.md` |
| `format` | `post`, `carousel`, `reel`, `article`, `long-form`, `tweet`, `thread` |
| `platform` | `medium`, `linkedin`, `instagram`, `x` (one row per platform; a carousel posted on LinkedIn and Instagram is two rows sharing `parent_id`) |
| `status` | `idea` → `drafted` → `scheduled` → `published`, or `dropped` |
| `formula` | `F1`-`F10` for LinkedIn posts (linkedin-post), `T1`-`T10` for X tweets and thread openers (x-post), `lab`/`guide`/`playbook` for articles, Reel format (`tutorial`/`story`/`listicle`/`opinion`/`bts`) for Reels, blank otherwise |
| `parent_id` | id of the piece this was repurposed from, blank if original |
| `source_url` | news item or reference that inspired it |
| `draft_path` | file path of the draft, if saved |
| `metricool_id` | from Metricool after scheduling |
| `post_url` | live URL once published |

Quote any field that contains a comma. Keep `notes` short.

## Operations

**Add idea.** Append a row with status `idea`. Ask for the pillar only if it
isn't obvious from the title. Confirm with one line.

**Log from another module.** Writing modules log `drafted`; Metricool logs
`scheduled`. Find an existing row by title or `parent_id` before appending, so
an idea that gets drafted updates its row instead of duplicating.

**Mark published.** When a scheduled time is in the past, the status is still
`scheduled` in the file. On any pipeline read, check those rows against Metricool if the connector is available: a row
still in `get_scheduled_posts` stays `scheduled`; otherwise find it in that
network's `get_<network>_posts` (match `metricool_id`, else same network, text
start, and publish time within 2 hours) and update to `published` with
`published_at` and `post_url`. The Metricool sync in
`.claude/skills/analytics/content-analytics/SKILL.md` runs this step with the
posts it already pulled. Match only on a clear hit; ambiguous rows go to the
user. Otherwise ask the user. The
piece was already archived when it was scheduled; fill `url` in its archive
file's frontmatter (at `draft_path`). If a `published` row has no archive file
yet (scheduled outside Metricool), run "File a scheduled piece" in
`.claude/skills/content/archive/SKILL.md`.

**Show board.** Group by status, newest first, one line per row:
`id · pillar · format · title · (scheduled_at)`. Cap ideas at 15 and say how
many more there are.

**Weekly plan.** Read cadence, the weekly slot map, and pillar mix from
`pillars.md`, and the month's dominant theme from
`context/strategy.md`. Look at the next 7 days:
1. Slots already filled (scheduled rows), per active platform.
2. Open slots (the slot map minus filled). Count them from the
   slot map in `pillars.md` (one per channel per posting day).
3. Pillar gap: last 14 days of published + scheduled vs. target mix.
4. Propose ideas from the backlog for each open slot, preferring the
   underweight pillars, then fresh dossier ideas. One line each with the
   suggested formula.
Show the plan, ask for approval, then update chosen rows' notes with the
target day. Don't schedule anything here; scheduling is Metricool's job after
the post is written.

**Theme week.** For "plan my week around X" or when the month's theme
should drive the week. One theme, every slot native to its platform:
1. Confirm the theme (default: the month's dominant theme in `strategy.md`)
   and the anchor piece (article, video, or long post) (backlog row or new idea).
2. Fill the slot map day by day, using `.claude/skills/content/repurpose/references/repurposing-map.md`
   to pick each platform's format and formula from the idea type:
   following the day themes in the slot map.
3. Output one table: day × platform, each cell = format · formula · one-line
   angle · pillar. Mark which piece to write first (the anchor piece, then
   any diagram that feeds several channels).
4. Add the daily engagement line: LinkedIn 10-15 comments, X 10-15 replies.
5. Readiness check before approval:
   - [ ] Every platform has at least one P-code from the month's theme and one
     from another pillar.
   - [ ] No formula repeated on the same platform in the same week.
   - [ ] No piece copy-pasted across platforms.
   - [ ] Links only where each platform allows (`platform-rules.md`).
   - [ ] Every diagram slot has a diagram source (see Diagrams in `CLAUDE.md`).
6. On approval, append one `idea` row per piece (with `parent_id` pointing at
   the anchor piece's row) and put the target day in `notes`.

**Stale check.** Ideas older than 45 days: list them in the weekly plan once
and offer to drop them. Drafts older than 14 days: flag them.

## Rules

- Never delete rows. Use `dropped`.
- Never invent `post_url` or `metricool_id`.
- If the file doesn't exist, create it with the header line above.
