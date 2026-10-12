---
name: daily-dossier
description: >-
  Lorenzo's morning content brief: top news in his area with angles, today's
  calendar, Buffer queue and gaps, pipeline status, three ready-to-write post
  ideas, engagement targets, and a metrics pulse. Use for "daily dossier",
  "morning brief", "brief me", "what should I post today", or a scheduled
  weekday run.
---

# Daily dossier

One page Lorenzo reads in 3 minutes, ending with what to write and who to
engage with today.

## Steps

Run the independent sources in parallel. If a source fails, keep going and
mark that section `unavailable (<reason>)`. Never fill a section from memory.

1. **Date and timezone.** Get today's date from the system. Timezone: the
   primary Google Calendar's timezone if the connector works, else the Buffer
   channel timezone, else ask once.
2. **News.** Run `references/intel/news-radar/news-radar.md` with a 24 h window
   (72 h on Mondays). Keep the top 5.
3. **Calendar.** Google Calendar `list_events` for today. Show meetings and
   free blocks of 60+ minutes; label the best one as the writing block.
4. **Queue.** Buffer `list_posts` for each channel (LinkedIn, Instagram, X),
   next 7 days. Compare with the slot map in `references/shared/pillars.md`
   (and whether this week's Medium article is drafted) and list empty slots
   per platform.
5. **Pipeline.** Read `data/pipeline.csv`: drafts waiting for review,
   anything scheduled today, stale drafts (14+ days).
6. **Metrics pulse.** If `data/metrics/posts.csv` has rows, show the last
   published post's numbers vs. Lorenzo's median. One line. Skip otherwise.
7. **Today's ideas.** Three ideas, each ready to hand to a writing module:
   - Fill today's slot-map theme first (e.g. Tuesday = concept explainer).
   - At least one from today's news, at least one from the backlog.
   - Prefer the pillar that is most underweight in the last 14 days.
   - Each: working title, pillar, platforms (LinkedIn + Instagram + X for a
     slot), format, formula code, one-sentence angle, source link.
8. **Engagement targets.** From "People to watch" in `sources.md`, list 3-5
   LinkedIn profiles (activity pages) and 3-5 X handles to check for fresh
   posts. If the list is empty, say so and suggest adding names. Daily
   targets (`references/shared/platform-rules.md`): 10-15 LinkedIn comments
   and 10-15 X replies.
9. **Save** to `data/dossiers/YYYY-MM-DD.md` (see `references/shared/storage.md`).

## Template

```
# Dossier, <Weekday DD Mon YYYY>

## Today
<meetings, one line each> · Writing block: <time range>
Today's slot: <theme> · Medium this week: <title, status>
Queue: LinkedIn <n> · Instagram <n> · X <n> scheduled this week · Open: <platform/day list>
Pipeline: <n> drafts waiting · <scheduled today, if any>
Last post: <title>, <impressions> impr, <eng rate>% (median <x>%)

## News
1. <title> (<source>) · <what happened, one line>
   Angle: <one line> · P2 · post · F10 · <url>
...

## Write today
1. <working title> · P1 · LinkedIn post F7 + IG carousel + X T2
   <angle> · <source>
2. ...
3. ...

## Engage
LinkedIn:
- <name>, <activity URL>
X:
- @<handle>, <profile URL>
...
Target: 10-15 LinkedIn comments, 10-15 X replies. Paste any post URL to
draft a comment (LinkedIn) or reply (X).
```

Then stop and offer: "Write #1?" (linkedin-post, x-post, ig-carousel as the
idea needs), "Add all to backlog?" (content-pipeline).

## Delivery options

- Default: show in chat + save the file.
- "As a page": render the same content as an HTML Artifact (load the
  artifact-design skill first). Monochrome per `references/shared/identity/design-guide.md`.
- "Email it": Gmail `create_draft` to Lorenzo's own address. Draft only,
  never send.

## Scheduled runs

To run every weekday morning, use the `schedule` skill to create a cloud
routine with the prompt "Run my daily dossier from the content-creation
skill", e.g. weekdays 07:00 in his timezone. Storage is Google Drive (see
`storage.md`) and delivery a Gmail draft. If scheduling isn't available in
this claude.ai plan, say so; the Claude Code build can schedule it instead.
Set this up only when the user asks.
