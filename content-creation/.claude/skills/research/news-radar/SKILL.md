---
name: news-radar
description: >-
  Scan, rank, and summarize news, releases, and discussions in the owner's area
  (the topic radar in context/pillars.md), each with a post angle. Use for
  "what's new in X", "any news on <brand or topic>", "trends this week", or when daily-dossier needs its news block.
---

# News radar

Find what happened in the area, keep only what the owner can say something
useful about, and turn each item into a post angle.

## Inputs

- `.claude/skills/research/news-radar/sources.md`: sources, feeds, people to watch.
- `context/pillars.md`: topic radar for scoring.
- `data/news/seen.csv` (via `context/storage.md`): already surfaced items.
- Optional: a topic the user named, and a window (default: last 72 hours,
  7 days when the user says "this week").

## Steps

1. **Collect.** Load WebSearch and WebFetch with ToolSearch if they aren't
   loaded. Then, in parallel where possible:
   - Fetch the Tier 1 sources in `sources.md` (release notes, official blogs).
   - Run WebSearch for each high-relevance topic with the date window,
     e.g. `<high-relevance topic> announcement <month year>`.
   - Check Tier 2 (community) for discussion volume around the same items.
   If the user named a topic, search only that topic, deeper.
2. **Normalize.** For each item: title, source, URL, published date, one-line
   summary in plain words. Drop items with no date or older than the window.
   Merge items about the same event (keep the primary source URL, note the rest).
3. **Dedup.** Drop URLs already in `seen.csv` unless there is a material
   update (new version, reversal, incident follow-up).
4. **Score** each item 0-10:
   - Relevance (0-4): high-relevance topic 4, medium 2, else 0.
   - Freshness (0-2): under 24 h 2, under 72 h 1.
   - Angle (0-3): the owner has a first-hand take from experience (a result,
     a cost, a mistake) (3), can add a tradeoff or "when not to" (2), can only
     summarize (0). Summaries alone are not content.
   - Signal (0-1): real discussion volume in Tier 2 sources.
   Keep items scoring 6+. If fewer than 3 pass, show the best 3 and say the
   day was quiet.
5. **Angle.** For each kept item write:
   - The angle in one sentence, from the owner's seat (a result, a cost,
     a mistake, what the announcement doesn't say).
   - Pillar code and best format (post, carousel, article).
   - Suggested hook formula code from linkedin-post (F1-F10).
6. **Log.** Append kept items to `seen.csv`:
   `date_seen,url,title,source,score,used` (`used` = blank until a piece
   is made from it; content-pipeline sets it to the pipeline id).

## Output

```
## News radar, <date>, window <72h|7d>

1. <Title> (<source>, <published date>) score 8
   What happened: <one line>
   Angle: <one line>
   P2 · post · F10 · <url>
...
Quiet signals: <items that scored 4-5, one line each, optional>
```

Then offer: "Turn #N into a post?" (chains to linkedin-post) or "Add to
backlog?" (content-pipeline, status `idea`, `source_url` set).

## Rules

- Never summarize a page you didn't fetch. If a fetch fails, use the search
  snippet and mark it `(snippet only)`.
- Never invent version numbers, dates, prices, or quotes.
- Vendor blog posts are announcements, not proof. Say "announced", not "works".
- Skip paywalled items unless the search snippet has enough to state the fact.
