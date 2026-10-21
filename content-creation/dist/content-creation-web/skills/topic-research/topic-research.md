---
name: topic-research
description: >-
  Deep research on one topic over the last 30 days across Reddit, Hacker News,
  the web, and X, synthesized into a briefing with real citations and ending
  in content angles mapped to Lorenzo's pillars and formats. Use for
  "research <topic>", "what are people saying about <topic>", "last 30 days
  on <topic>", "is <topic> worth writing about", or before a Medium article
  or a contrarian post that needs evidence. Not for the daily scan of news
  (that is news-radar).
---

# Topic research

news-radar scans many sources for what's new. This module goes deep on one
topic: what practitioners actually say, where they disagree, and what nobody
has answered well. The gaps are where Lorenzo's articles come from.

## Input

A topic ("Iceberg vs Delta in Fabric", "LLM evals for data pipelines"). If
none was given, ask. Optional: a window other than 30 days.

## Phases

Run phases 1-3 in parallel. Then phase 4. Then synthesize. If a source fails,
note it in that section and keep going. Never fill a section from memory.

### 1. Reddit

WebFetch the public JSON search (no key):

```
https://www.reddit.com/search.json?q=<TOPIC>&sort=top&t=month&limit=25
https://www.reddit.com/search.json?q=<TOPIC>&sort=new&t=month&limit=15
https://www.reddit.com/r/dataengineering/search.json?q=<TOPIC>&restrict_sr=1&sort=top&t=month
```

Record title, subreddit, score, comment count, date, URL. For the top 3-5
posts, fetch the thread (`/r/<sub>/comments/<id>.json?sort=top&limit=10`) and
note recurring complaints, praise, and questions. If blocked, retry once with
`&raw_json=1`.

### 2. Hacker News

Algolia API, with `<TS>` = Unix time 30 days ago (compute from the system date):

```
https://hn.algolia.com/api/v1/search?query=<TOPIC>&tags=story&numericFilters=created_at_i><TS>&hitsPerPage=20
https://hn.algolia.com/api/v1/search?query=<TOPIC>&tags=comment&numericFilters=created_at_i><TS>&hitsPerPage=15
```

Record title, URL, points, comments, notable comment excerpts.

### 3. Web

2-3 WebSearch queries: vendor announcements and docs, practitioner blog
posts, and `<TOPIC> problems OR "in production" OR postmortem`. Fetch the 3-4
most relevant pages and pull the actual claims, numbers, and conclusions.
Prefer sources from `skills/news-radar/sources.md`.

### 4. X

X needs a login, so in order of preference:

1. If a browser tool with a logged-in session is available (Claude in Chrome),
   search X directly for the topic, filtered to the last 30 days, and read the
   top posts and replies.
2. Otherwise, ask Grok at grok.com through the browser: "What are people
   saying about <TOPIC> on X in the last 30 days? Main discussions, opinions,
   complaints, notable posts and accounts, with specific examples."
3. If neither works, mark the section `unavailable (no logged-in browser)` and
   move on. Don't retry endlessly.

Note accounts worth adding to the X reply targets in `sources.md`.

### 5. Synthesize

Look for consensus, real disagreement, recurring pain, genuine excitement,
what's emerging vs settled, and unanswered questions. A point that shows up
on Reddit **and** HN **and** X is the strongest signal.

## Output

Save to `data/research/<topic-slug>-<YYYY-MM-DD>.md` (storage rules in
`context/storage.md`) and also show the full briefing in chat.

```markdown
# <Topic>: last 30 days
*Generated: <date> · window: <start> to <end>*

## TL;DR
2-3 sentences.

## Reddit
- **<title>** (r/<sub>, <score> pts, <n> comments) · <one line> · <url>
What Reddit is saying: <paragraph>

## Hacker News
- **<title>** (<points> pts, <n> comments) · <one line> · <url>
What HN is saying: <paragraph; HN skews builder/skeptic>

## Web
- **<title>** (<publication>) · <key claim> · <url>

## X
<findings, with handles and post links where available, or "unavailable (reason)">

## Cross-platform patterns
## Open questions nobody answers well

## Content angles
| # | Angle | Pillar | Format | Module | Formula | Evidence |
|---|---|---|---|---|---|---|
| 1 | ... | P1 | article | medium-tech-article | lab | <links> |
| 2 | ... | P2 | thread | x-thread | T4 | ... |
| 3 | ... | P1 | post | linkedin-post | F10 | ... |
```

Then offer: "Add these angles to the backlog?" (content-pipeline) or "Run
seo research on angle 1?".

## Rules

- Every claim in the briefing links to its source. No source, no claim.
- Engagement numbers are copied, never estimated.
- Label opinions as opinions ("r/dataengineering commenters argue...").
- Don't quote private individuals' posts at length in content; the briefing is
  for Lorenzo, and posts built from it paraphrase and credit.
