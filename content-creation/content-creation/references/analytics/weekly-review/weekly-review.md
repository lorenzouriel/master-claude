---
name: weekly-review
description: >-
  Friday review of Lorenzo's content week: what shipped vs. planned, the week's
  numbers, pillar balance, lessons, and next week's plan. Use for "weekly
  review", "how was my week", "review and plan next week", or a scheduled
  Friday run.
---

# Weekly review

Close the week in 10 minutes and leave next week planned.

## Steps

1. **Fresh numbers.** Ask for this week's LinkedIn and X exports, Instagram
   insights, and Medium stats for the week's article. If the user skips, use whatever is in
   `data/metrics/posts.csv` and say the data may be stale.
2. **Ingest** via `references/analytics/content-analytics/content-analytics.md`
   (ingest section only).
3. **Shipped vs. planned.** From `data/pipeline.csv`: pieces published this
   ISO week vs. the slot map in `references/shared/pillars.md` (16 slots:
   1 Medium, 5 LinkedIn, 5 Instagram, 5 X), per platform. List misses
   without judgment, one line each with the reason if known.
4. **Numbers.** From content-analytics: headline metrics for the week vs. the
   4-week median, and the best and worst post with a one-line hypothesis.
5. **Pillar balance.** Last 14 days vs. target mix. Name the most underweight
   pillar.
6. **Lessons.** At most 3, each tied to a number. Examples: "F7 posts got 2.1x
   median comments, 3 of 3", "Thursday posts underperformed, n=2, too few".
7. **Next week.** Run the weekly-plan operation in
   `references/ops/content-pipeline/content-pipeline.md`, biased toward the
   underweight pillar and the lessons.
8. **Save** to `data/reviews/YYYY-Www.md`.

## Template

```
# Week <YYYY-Www> review

Shipped <n>/16 · Medium <n>/1 · LinkedIn <n>/5 · Instagram <n>/5 · X <n>/5
Per platform: impressions <n> (<+/-x%> vs 4-wk median) · eng rate <x%> · followers +<n>

## Shipped
- <date> · <title> · <eng rate>
## Missed
- <planned item> · <reason>

## Best / worst
Best: <title>, <rate>. Why (hypothesis): <line>
Worst: <title>, <rate>. Why (hypothesis): <line>

## Balance
P1 <x%> · P2 <x%> · P3 <x%> · P4 <x%> · P5 <x%> · underweight: <Pn>

## Lessons
1. ...

## Next week
Theme: <weekly theme> (month: <dominant theme>)
Medium (Wed): <title>
| Day | LinkedIn | Instagram | X |
|---|---|---|---|
| Mon | <title · P · F> | ... | <... · T> |
| Tue | ... | ... | ... |
| Wed | recap | carousel recap | thread |
| Thu | meme CTA | meme CTA | sharpest insight |
| Fri | curated list | curated list | best item |
```

## Scheduled runs

On request, use the `schedule` skill for a Friday afternoon routine. Same
storage caveat as daily-dossier: cloud runs use Google Drive and a Gmail draft.
