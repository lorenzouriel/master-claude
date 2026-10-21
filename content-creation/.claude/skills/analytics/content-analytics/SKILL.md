---
name: content-analytics
description: >-
  Ingest and analyze the owner's content performance from LinkedIn analytics
  exports, X analytics exports, Instagram insights, Medium stats, and Metricool, then report what works: hook formulas,
  pillars, formats, posting times, follower growth. Use for "how did my posts
  do", "analyze my LinkedIn stats", "what's working", an uploaded LinkedIn or
  Medium export, or when weekly-review needs numbers.
---

# Content analytics

Turn exports into one clean table, then answer "what should I do more of".

## Data sources

| Source | How it arrives | Notes |
|---|---|---|
| LinkedIn | Creator analytics export (.xlsx) from linkedin.com/analytics, "Export" | No API for personal profiles. Ask for a fresh export weekly. |
| X | Analytics export (.csv) from analytics.x.com, "Export data" (by post, chosen date range) | Columns include impressions, engagements, replies, reposts, likes, bookmarks, profile visits, URL clicks. Requires X Premium for the full analytics page; if unavailable, ask for screenshots. |
| Instagram | Insights from the app (professional account): per-post screenshot or Meta Business Suite export (.csv) | Reach, saves, shares, comments, likes; Reels add plays and average watch time. |
| Medium | Paste from the stats page, or a screenshot | No export. Per story: views, reads, read ratio, earnings if Partner Program. Referrers show Google and AI assistants (feeds `seo` monitor). |
| Metricool (preferred) | Metricool MCP: `get_<network>_posts` (LinkedIn, X, Instagram, TikTok, YouTube) for per-post metrics, `get_analytics` for followers and account totals. See `.claude/skills/content/metricool/SKILL.md`. | Covers LinkedIn personal profiles, TikTok, and YouTube. History depth depends on the plan (Free: 30 days). Exports above fill gaps and older history. |

## Sync from Metricool

The default way to refresh the CSVs. Run on "sync metrics", "update my
numbers", at the start of `weekly-review`, and (last 7 days only) in
`daily-dossier`. Tool calls follow `.claude/skills/content/metricool/SKILL.md`.
If the Metricool connector isn't available, say so and fall back to the
exports in Ingest below.

1. **Window.** Default: from the latest `collected_at` in `posts.csv` minus 7
   days (metrics keep moving for a week) to today. First run or "full sync":
   the last 90 days. If the plan returns nothing older (Free keeps 30 days),
   say the plan limit was reached, not that there were no posts.
2. **Brand.** `get_brands` → `blogId` and the connected networks. Sync only
   the networks the owner uses: LinkedIn, X, Instagram, TikTok, YouTube.
3. **Pull posts.** Per network, for the window: `get_linkedin_posts`,
   `get_x_posts`, `get_instagram_posts` + `get_instagram_reels`,
   `get_tiktok_videos`, `get_youtube_videos`. Page through results until
   empty; don't stop at the first page.
4. **Pull followers.** `get_analytics` per network for the window, daily
   granularity if the tool offers it (check `get_metrics` for the follower
   metric name).
5. **Keep raw.** Save every response untouched as JSON to
   `data/metrics/raw/metricool-<network>-<YYYY-MM-DD>.json` (one file per
   network per sync day; overwrite the same day's file) before parsing.
6. **Map.** Convert each post to the `posts.csv` schema with the Metricool
   mapping table below. On the first sync, or when a response has fields the
   table doesn't cover, show the proposed mapping and wait for a yes before
   writing.
7. **Upsert.** `posts.csv` keyed by `post_url` (newer numbers overwrite the
   same post; never delete rows). `followers.csv` keyed by `date` +
   `platform`. Set `collected_at` to today.
8. **Tag.** Join with `data/pipeline.csv` on `post_url`, then `metricool_id`,
   to fill `pillar`, `format`, `formula`. Untagged posts: ask in one batch, or
   leave blank.
9. **Reconcile the pipeline.** Hand the pulled posts to the "Mark published"
   operation in `.claude/skills/content/content-pipeline/SKILL.md`, so
   scheduled rows that went live get `published`, `published_at`, `post_url`.
10. **Report.** One line per network: posts added, posts updated, follower
    rows added, the oldest date returned. Then the default Analysis below only
    if the user asked "how did my posts do", not after a plain sync.

Medium is not in Metricool: keep pasting its stats (Data sources above).

### Metricool mapping

Fill from the first real sync (field names differ per network and change with
the server). Until then, map by meaning and confirm with the owner.

| Column | LinkedIn | X | Instagram (post / Reel) | TikTok | YouTube |
|---|---|---|---|---|---|
| `post_url` | (first sync) | (first sync) | (first sync) | (first sync) | (first sync) |
| `published_at` | | | | | |
| `impressions` | | | reach (Reels: plays) | views | views |
| `reactions` | | likes | likes | likes | likes |
| `comments` | | replies | comments | comments | comments |
| `reposts` | | reposts + quotes | shares | shares | n/a |
| `clicks` | | link clicks | n/a | n/a | n/a |
| `saves` | | bookmarks | saves | saves (if given) | n/a |
| `video_views` | video only | video only | Reels plays | views | views |
| `avg_watch_time` | n/a | n/a | Reels avg watch time | avg watch time | avg view duration |

## Ingest (manual exports)

For sources Metricool doesn't cover (Medium) or history older than the
Metricool plan keeps.

1. Save the original file untouched to `data/metrics/raw/<source>-<YYYY-MM-DD>.<ext>`
   (see `context/storage.md`).
2. Inspect before parsing. For xlsx, list sheet names and the header row of
   each (Python with pandas/openpyxl). LinkedIn exports usually have sheets like
   DISCOVERY, ENGAGEMENT, TOP POSTS, FOLLOWERS, DEMOGRAPHICS, but names and
   columns change: map what you actually see and show the mapping to the user
   before writing anything.
3. Upsert into `data/metrics/posts.csv`, keyed by `post_url`. Newer exports
   overwrite numbers for the same post.
4. Upsert daily totals into `data/metrics/followers.csv`.
5. Join with `data/pipeline.csv` on `post_url` (or `metricool_id`) to pull
   `pillar`, `format`, `formula`. Posts with no pipeline row: ask for pillar and
   formula in one batch question, or leave blank.

### posts.csv schema

```
post_url,platform,published_at,title,pillar,format,formula,impressions,reactions,comments,reposts,clicks,saves,profile_visits,video_views,avg_watch_time,reads,read_ratio,earnings,collected_at
```

Column mapping per platform:

| Column | LinkedIn | X | Instagram | Medium |
|---|---|---|---|---|
| `impressions` | impressions | impressions | reach (or plays for Reels) | views |
| `reactions` | reactions | likes | likes | claps |
| `comments` | comments | replies | comments | responses |
| `reposts` | reposts | reposts + quotes | shares | n/a |
| `clicks` | clicks | URL clicks | link-in-bio taps if known | n/a |
| `saves` | saves if exported | bookmarks | saves | highlights if shown |
| `profile_visits` | n/a | profile visits | profile visits | n/a |
| `video_views` / `avg_watch_time` | video only | video only | Reels plays / avg watch time | n/a |
| `reads` / `read_ratio` / `earnings` | n/a | n/a | n/a | from stats |

`engagement_rate = (reactions + comments + reposts + saves) / impressions`,
computed at analysis time, not stored. For Medium, use `reads / views` as the
rate. Compare rates within a platform only; an X rate and a LinkedIn rate are
not comparable. On X, also report `comments / impressions` (reply rate), the
signal X weighs most.

### followers.csv schema

```
date,platform,followers,new_followers
```

## Analysis

Default report (last 30 days, plus all-time where noted), per platform:

1. **Headline.** Impressions, median engagement rate, followers gained, posts
   published. Each vs. the previous 30 days.
2. **Top 3 and bottom 3 posts** by engagement rate (min 500 impressions to
   qualify). For each, one line on the likely reason: hook, topic, format,
   timing. Label reasons as hypotheses.
3. **By formula** (all-time, per platform): F-codes for LinkedIn, T-codes for
   X, count and median rate. Feeds the formula pick in linkedin-post and x-post. Mark any group with fewer than 5 posts as "too few to trust".
4. **By pillar and format:** count, median rate, share of output vs. target mix
   in `pillars.md`.
5. **Timing:** median rate by weekday and by hour band. Only if 20+ posts.
6. **Comments ratio:** comments / reactions. High ratio = conversation posts;
   note which formulas produce them.
6b. **Cross-platform:** for pieces that share a `parent_id` (the anchor
   set), which platform carried the idea best, and whether the X thread or
   LinkedIn recap drove Medium reads (Medium referrers).
7. **Do more / do less:** at most 3 bullets each, each tied to a number above.

Charts: load the `dataviz` skill before drawing any chart. Use medians, not
means (one viral post wrecks a mean). Small samples get a caveat, not a
conclusion.

## Output

Chat summary always. On request, an HTML Artifact report (load artifact-design
and dataviz first) or a markdown file in `data/reviews/`.

## Rules

- Never invent or estimate a missing metric. Blank stays blank.
- Show the raw-to-schema column mapping before the first import of a new
  export shape.
- Correlation language only: "posts with X got higher engagement", never
  "X causes".
