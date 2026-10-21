---
name: archive
description: >-
  The owner's content archive. Imports their past Medium articles, LinkedIn posts,
  and X posts into one dated folder tree, and moves new pieces (posts,
  articles, carousels, Reels) into it once they are approved and scheduled. Feeds
  repurpose, content-analytics, seo clusters, and a future ebook. Use for
  "archive my Medium posts", "import my LinkedIn history", "import my tweets",
  "save my old content", "archive this carousel", "file what I published this
  week".
---

# Archive

One place where every published piece lives as plain text, by date and
platform. The archive is what lets `repurpose` find old material and lets
`content-analytics` read what a post actually said.

## Layout

Root: `data/archive/` (resolve local vs Drive per `context/storage.md`).

```
data/archive/
  YYYY/
    MM/                    zero-padded
      WEEK 01/             days 1-7
        medium/<slug>.md
        linkedin/<YYYY-MM-DD>-<preview>.md
        x/<YYYY-MM-DD>-<preview>.md
        instagram/<slug>/  slide images, carousel.pdf, copy.md, caption.md
      WEEK 02/             days 8-14
      WEEK 03/             days 15-21
      WEEK 04/             days 22-31 (clamped, never WEEK 05)
```

Week label: `f"WEEK {min((day - 1) // 7 + 1, 4):02d}"`.

A new install starts empty; `/system install` (module 6) offers the history
import. Folders of channels the owner retired stay as source material; never
file new pieces there. The archive is local only (gitignored).

Every text file starts with:

```yaml
---
title: "..."
date: YYYY-MM-DD
platform: medium | linkedin | x | instagram
url: https://...
pipeline_id: <id or blank>
---
```

## Operations

### Import Medium history

Handle and Medium user ID come from `context/accounts.md`. Missing user ID:
WebFetch `https://medium.com/@<handle>?format=json` and read `userId`; save it
to `accounts.md`.

1. Collect slugs: `python scripts/collect_medium_slugs.py <user_id> [cutoff YYYY-MM-DD] [out.json]`
   (default cutoff 2024-01-01). Pages the public profile API; dedupes the
   featured post that repeats on every page.
2. Skip slugs whose file already exists (filename = slug without the trailing
   12-char hex id; `-2`, `-3` on collisions).
3. Fetch each article with WebFetch on `https://medium.com/@<handle>/<slug>`
   using this prompt verbatim:
   > "Return the raw article text EXACTLY as it appears on the page. Do NOT
   > rewrite, restructure, bullet-point, or summarize anything. Copy the text
   > verbatim, sentence by sentence, paragraph by paragraph, in the exact same
   > order it appears. Include every word the author wrote. If there are code
   > blocks, copy them exactly. If there are headers, copy them exactly. Do not
   > add your own words or structure. Just copy what you see."
4. Date = `firstPublishedAt` from the slug file, not the page.
5. **Batch at most 10 articles per session.** Medium has a session limit
   (resets daily; about 3 AM UTC-3). On "You've hit your session limit", stop
   and report.
6. Member-only articles come back truncated: save what's there, append
   `[PAYWALL CUTOFF]`, and list them for the owner to paste.

### Import LinkedIn history

LinkedIn's data export no longer includes posts, so this uses the Apify actor
`harvestapi/linkedin-profile-posts`.

1. Needs `APIFY_TOKEN` in the environment (or the Apify MCP connector). Never
   paste the token into a file or a command line that gets saved.
2. Run the actor for the LinkedIn public id in `context/accounts.md` with `maxPosts: 0` and
   `postedLimitDate` = cutoff (via the Apify MCP tools, or the Apify console).
3. Import the dataset:
   `python scripts/linkedin_from_apify.py <dataset_id> data/archive <public_id> [cutoff]`.
   It keeps only the owner's own posts (drops reshares), skips files that already
   exist, and never deletes anything.

### Import X history

1. The owner requests their archive at x.com → Settings → Your account →
   Download an archive of your data (arrives by email, can take a day).
2. Unzip it, then:
   `python scripts/x_from_archive.py <archive-folder>/data/tweets.js data/archive [cutoff] [handle]`.
   Keeps original posts and threads (first tweet + their own replies chained
   under it), drops replies to other people and reposts.

### Import Instagram history

Instagram → Settings → Accounts Center → Your information and permissions →
Download your information (JSON). Ask the owner for the `posts_1.json` path and
the media folder; file each post as `instagram/<date>-<preview>/` with its
images and a `caption.md`. Show the mapping for the first 3 posts before doing
the rest.

### File a scheduled piece

A piece moves into the archive once it is approved **and** scheduled, not
before. Triggers:

- `metricool` Step 7 sets a pipeline row to `scheduled` (or `published` for
  post now). Metricool drafts don't count.
- Medium (no Metricool): the owner confirms they scheduled or published the approved
  article by hand.
- "archive this" / "file this week's posts": file only rows already
  `scheduled` or `published`; list the rest and skip them.

Never file a piece that is still `idea` or `drafted`, even if approved.

The archive folder date is the **scheduled date** (`scheduled_at`, or the
publish date for Medium), not today.

| Piece | Source | Goes to |
|---|---|---|
| Medium article | `output/articles/<date>-<slug>.md` | `medium/<slug>.md`, moved |
| LinkedIn / X post or thread | the approved text (pipeline `draft_path` or Metricool post text) | `linkedin/` or `x/` |
| Carousel | finalized folder in `output/carousels/` (see ig-carousel Step 7) | `instagram/<slug>/`, moved |
| Reel / TikTok / YouTube video | `output/reels/<date>-<slug>/` | `instagram/<slug>/` (script + final video file) |

Approval and scheduling already happened, so move without asking again. Move
only after Metricool has confirmed the post (its media is hosted by then). Update
the pipeline row's `draft_path` to the archive location and report the moves
in one line each.

Frontmatter: `url` stays blank and `pipeline_id` is set. When content-pipeline
later marks the row `published`, fill in `url` (the `post_url`). That is the
only edit allowed on an existing archive file.

## Report

```
Medium: 12 saved (2024-03 to 2024-06) · 3 paywalled (paste needed) · 45 already archived
LinkedIn: 48 saved · 6 reshares skipped
X: 120 saved · 340 replies skipped
Pre-cutoff skipped: 14
```

## Rules

- Never overwrite an existing archive file (except filling `url` on publish).
  Never delete archive files.
- Verbatim text only. The archive is a record, not a rewrite.
- Never store API tokens in the archive, the scripts, or the pipeline.
