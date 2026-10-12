---
name: x-post
description: Draft a single X (Twitter) post or a thread opener using one of ten hook formulas (contrarian, number-shock, confession, hot-take, pattern-interrupt, comparison, question, reveal, thread-bait, how-I). Runs the humanizer pass and hands off to Buffer on approval. Use when the user asks for a tweet, an X post, a hook for X, or a short take. For full threads use x-thread; for replies to other people's tweets use x-reply-drafter.
---

# X post

One sharp tweet in Lorenzo's voice. X rewards conviction, specifics, and
replies, so every draft is built to provoke a real response.

## When to use

- "Write a tweet about X", "post this on X", "give me a hook for X".
- A daily X slot from the weekly plan (Mon, Tue, Thu, Fri in `pillars.md`).
- A thread opener only, when the user will write the rest themselves.

## Formulas

| Code | Formula | Best for |
|---|---|---|
| T1 | Contrarian Opener | Hot takes, counter-intuitions |
| T2 | Number Shock | Data, costs, benchmarks |
| T3 | Confession / Mistake | Monday reflection, credibility |
| T4 | Hot Take + Thread | Opinion-first threads |
| T5 | Pattern Interrupt | "Stop doing X, do Y" |
| T6 | Comparison | Tool vs tool, approach vs approach |
| T7 | Question | Genuine open questions |
| T8 | The Reveal | Non-obvious root causes |
| T9 | Thread Bait | Research or build-log threads |
| T10 | How-I | Results with a timeframe |

Skeletons, rules, and examples: `references/hook-formulas.md`.

## Steps

1. **Gather inputs.** Topic, angle, pillar (P1-P5 from
   `references/shared/pillars.md`), and the source if it came from a dossier,
   news-radar item, or a Medium article (the link goes in the first reply,
   never the tweet).
2. **Pick the formula.** If the user didn't name one, suggest 2-3 that fit and
   let them pick. If `data/metrics/posts.csv` has 10+ X rows, show Lorenzo's
   median engagement per T-code (content-analytics) and prefer his data.
3. **Draft.** Fill the skeleton in Lorenzo's voice:
   - First 5-8 words carry the hook.
   - 280 chars hard limit; aim for 71-200.
   - One idea. Three points means three tweets or a thread.
   - 0 hashtags by default, never more than 1.
   - No link in the body.
4. **Humanizer pass** (`references/shared/humanizer/humanizer.md`, `quick`
   mode, X block of `platform-scrub-rules.md`). At least one concrete specific
   (number, tool, date). No em dashes, no emojis, no hedging.
5. **Approval card.** Formula (T-code), pillar (P-code), the tweet, char count,
   suggested posting window (one of 8-10 AM / 12-1 PM / 7-9 PM local, keeping
   the same window Lorenzo has been using), and the first-reply text if there
   is a link. Offer 1 alternative opening line.
6. **On approval.** Log in the pipeline as `drafted` (`platform: x`,
   `format: tweet`, `formula: Tn`). If the user wants it scheduled, hand the
   exact text to `references/ops/buffer/buffer.md`, with the first reply as a
   note for Lorenzo to post right after (Buffer schedules the tweet only).

## Hard rules

- Never beg: "follow me", "RT if you agree", "thoughts?".
- No all-caps words, no emojis, no em dashes.
- No hedging ("might", "perhaps", "sort of"). Commit or don't post.
- Don't frame another platform as superior in the tweet.
- Never invent a number. If the hook needs one and Lorenzo hasn't given it, ask.

## Resources

- `references/hook-formulas.md`: T1-T10 skeletons and the picking table.
- `references/algorithm-heuristics.md`: X ranking signals, timing, length.
- `references/shared/platform-rules.md`: X section.
- `references/shared/channel-strategy/x.md`: long-form X strategy, only when
  the user asks for strategy.

## Related modules

- `x-thread`: when the idea needs 3+ points.
- `x-reply-drafter`: daily replies, the main X growth lever.
- `buffer`: scheduling.
- `repurpose`: when the tweet comes from an article.
