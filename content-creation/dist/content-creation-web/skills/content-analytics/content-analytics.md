---
name: content-analytics
description: >-
  Ingest and analyze Lorenzo's content performance from LinkedIn analytics
  exports, X analytics exports, Instagram insights, Medium stats, and Buffer, then report what works: hook formulas,
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
| Buffer | Buffer MCP (`get_post`, or `execute_query` after `introspect_schema`) | Use only if the schema exposes post statistics. Don't guess fields. |

## Ingest

1. Save the original file untouched to Drive `data/metrics/raw/<source>-<YYYY-MM-DD>.<ext>`
   (`create_file` with `base64Content`, the real MIME type, and
   `disableConversionToGoogleType: true`; see `context/storage.md`).
2. Inspect before parsing. For xlsx, list sheet names and the header row of
   each (Python with pandas/openpyxl in the code tool; if the code tool is
   off, ask Lorenzo to paste the relevant sheet as CSV text). LinkedIn exports usually have sheets like
   DISCOVERY, ENGAGEMENT, TOP POSTS, FOLLOWERS, DEMOGRAPHICS, but names and
   columns change: map what you actually see and show the mapping to the user
   before writing anything.
3. Upsert into `data/metrics/posts.csv`, keyed by `post_url` (read, merge,
   write once, per the storage rewrite protocol). Newer exports
   overwrite numbers for the same post.
4. Upsert daily totals into `data/metrics/followers.csv`.
5. Join with `data/pipeline.csv` on `post_url` (or `buffer_id`) to pull
   `pillar`, `format`, `formula`. Posts with no pipeline row: ask for pillar and
   formula in one batch question, or leave blank.

### posts.csv schema

```
post_url,platform,published_at,title,pillar,format,formula,impressions,reactions,comments,reposts,clicks,saves,profile_visits,reads,read_ratio,earnings,collected_at
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
6b. **Cross-platform:** for pieces that share a `parent_id` (the Wednesday
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
