---
name: x-thread
description: Write a full X (Twitter) thread of 3-10 tweets in Lorenzo's voice, most often the Wednesday thread that recaps his Medium article. Uses the T4, T9, or T10 hook formulas, one idea per tweet, link only in the last tweet. Use when the user asks for a thread, "turn this into a thread", "X thread about the article", or a breakdown too big for one tweet.
---

# X thread

The long format on X. Tweet 1 is the only one most people see, so it must
work alone; every other tweet must also make sense if someone screenshots it.

## When to use

- The Wednesday slot: thread recapping that day's Medium article.
- Any idea with 3+ insights, steps, or receipts.
- "Turn this into a thread", "thread this", "X version of the article".

For a single tweet use `x-post`.

## Inputs

- Source: a Medium article (most common), a LinkedIn post, notes, or a topic.
- Pillar (P1-P5). If the source is in the pipeline, reuse its pillar and
  set `parent_id` to the source's id.
- Shape: breakdown, steps, story, or opinion (below).

## Shapes

| Shape | Opener formula | Body | Length |
|---|---|---|---|
| Breakdown (article recap) | T9 Thread Bait or T2 Number Shock | One insight per tweet, each with its own number or tradeoff | 5-8 tweets |
| Steps (how-to, lab) | T10 How-I | One step per tweet: action + result | 5-7 tweets |
| Story (mistake, incident) | T3 Confession | Tension, what broke, what it cost, the lesson | 4-6 tweets |
| Opinion | T4 Hot Take | Claim, steelman, 2-3 evidence tweets, reframe | 5-7 tweets |

Skeletons for T-codes: `skills/x-post/references/hook-formulas.md`.

## Structure

```
Tweet 1  HOOK      Stands alone. Promises what the thread delivers.
                   Ends with "Here's what I found:" / a colon / "Thread:"
                   only when the line above is already strong.
Tweet 2  STAKES    Why it matters. The symptom, the cost, the context.
Tweets 3..N-1      One idea per tweet, 140-200 chars, each with a specific.
                   No filler tweets. If a tweet adds nothing, delete it.
Tweet N  CLOSE     The takeaway in one line, then the link:
                   "Full lab with the queries: <link>" (Medium recap)
                   or a specific question that invites replies.
```

## Steps

1. **Read the source in full.** For a Medium recap, extract the thesis and
   3-6 standalone insights, the same way `repurpose` does. An insight
   qualifies only if it has its own number, failure, or tradeoff.
2. **Pick the shape and opener.** Show 2 opener options with their T-codes.
3. **Draft every tweet.** Rules:
   - No numbering (`1/`, `2/`). Each tweet stands alone.
   - 140-200 chars per tweet, 280 hard limit. Show the count per tweet.
   - Vary tweet length and rhythm; don't make every tweet a list item.
   - Never copy sentences from the article. Rewrite for X.
   - Code: at most one short inline snippet in the whole thread, or an image
     of the code/diagram attached to the tweet that needs it.
   - 0 hashtags. No emojis, including the thread emoji.
   - The link appears only in the last tweet.
4. **Humanizer pass** (`quick` mode + X block of
   `skills/humanizer/references/platform-scrub-rules.md`). Check the thread
   tells: numbered tweets, filler tweets, uniform length.
5. **Approval card.** Opener T-code, pillar, every tweet with its char count,
   total tweets, suggested media per tweet (e.g. Tuesday's diagram), and the
   posting window. For the Wednesday recap, schedule it after the Medium
   article is live.
6. **On approval.** Log in the pipeline as `drafted` (`platform: x`,
   `format: thread`, `formula: Tn`, `parent_id` = source id). Hand it to
   `skills/buffer/buffer.md` if the user wants it scheduled; Buffer
   handles threads on X as one post with multiple tweets only if the channel
   supports it, so check `list_channels` and otherwise give Lorenzo the
   thread to post manually.

## After posting (tell Lorenzo)

- Reply to every reply in the first 2 hours.
- Quote-repost tweet 1 a few hours later or the next morning, with one new line.
- If the thread performs, consider pinning it (pin refresh every 60-90 days).

## Hard rules

- Tweet 1 must make sense with nothing else around it.
- No link before the last tweet.
- No invented numbers. Every number comes from the source or from Lorenzo.
- No emojis, no em dashes, no hedging.

## Related modules

- `x-post`: single tweets and thread openers only.
- `repurpose`: plans the thread as part of an article's spin-offs.
- `medium-tech-article`: the usual source.
