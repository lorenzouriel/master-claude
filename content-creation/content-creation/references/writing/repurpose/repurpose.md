---
name: repurpose
description: >-
  Turn one finished piece (usually the Wednesday Medium article, sometimes a
  long LinkedIn post) into a set of platform-native pieces for LinkedIn, X,
  and Instagram: recap posts, an X thread, single tweets, a carousel, a Reel
  script, comment and reply hooks, and a thumbnail prompt. Use for "repurpose
  this", "turn this article into posts", "spin this off", "the Wednesday set",
  "what else can I get out of this".
---

# Repurpose

One article feeds the Wednesday set and about two weeks of follow-ups across
LinkedIn, X, and Instagram. This module plans the set and dispatches each
piece to its writing module. It writes no final copy itself.

How each idea type maps to each platform: `references/repurposing-map.md`.

## Steps

1. **Read the source** in full. If it's in the pipeline, note its `id`.
2. **Extract.** One core idea (the thesis), then 3-6 standalone insights. An
   insight qualifies only if it has its own number, failure, or tradeoff. A
   paragraph that needs the rest of the article to make sense doesn't count.
   Classify each by idea type (data, contrarian, mistake, how-to, concept,
   opinion) to pick formats from the map.
3. **Plan the set.** Propose, in one table. The first block is the Wednesday
   set from the map; the second is follow-ups.

   | # | Piece | Platform | Module | Insight | Formula/shape | Pillar | Day offset |
   |---|---|---|---|---|---|---|---|
   | 1 | Recap post | LinkedIn | linkedin-post | core idea | F4 or F10 | Px | +0 |
   | 2 | Thread | X | x-thread | core + 3-5 insights | T9 / T10 / T4 | Px | +0 |
   | 3 | Carousel recap | Instagram (+ LinkedIn PDF) | ig-carousel | the steps/framework | text-only | Px | +0 |
   | 4 | Meme CTA | LinkedIn + Instagram | linkedin-post / ig-carousel | the punchline | single post | Px | +1 |
   | 5 | Sharpest insight | X | x-post | insight 2 | T2 or T8 | Px | +1 |
   | 6 | Deep-cut post | LinkedIn | linkedin-post | insight 3 | F7 or F8 | Px | +5 |
   | 7 | Reel | Instagram | ig-reel-script | the demo moment | Tutorial / Opinion | Px | +7 |
   | 8 | Contrarian post | LinkedIn + X | linkedin-post, x-post | the tradeoff | F10 / T1 | Px | +11 |
   | 9 | Comment and reply hooks | n/a | (this module) | leftover insights | 1-2 lines each | | n/a |
   | 10 | Thumbnail | Medium | thumbnail-prompt | core idea | | | if missing |

   Different formulas per piece, so the set doesn't read like one post said
   eight times. Drop rows that don't fit the article; not every article has a
   Reel in it.
4. **Approval.** User picks which pieces to make.
5. **Dispatch** each chosen piece to its module, in the map's order (LinkedIn,
   X, Instagram), passing the insight and the source excerpt. Each module runs
   its own approval checkpoint.
6. **Hooks.** For insights not used in pieces, write 2-4 one-to-two line takes
   Lorenzo can adapt when commenting on LinkedIn or replying on X about the
   same topic. Same voice rules as `linkedin-comment-drafter` and
   `x-reply-drafter`. Save them in the pipeline row notes of the source piece.
7. **Log** each derived piece in `data/pipeline.csv` with `parent_id` set to
   the source's id, the right `platform`, and status `idea` (or `drafted` once
   written).

## Rules

- Never copy sentences verbatim between the article and the derived pieces.
  Rewrite for each platform.
- Each derived piece must stand alone for a reader who never saw the article.
- Links: LinkedIn first comment, X last tweet or first reply, Instagram "link
  in bio". Never in a LinkedIn or X body.
- Follow-ups at least 3 days apart, interleaved with other pillars.
- Respect the weekly slot map in `references/shared/pillars.md`; don't
  schedule a follow-up into a slot that already has a theme (e.g. Friday's
  curated list).
