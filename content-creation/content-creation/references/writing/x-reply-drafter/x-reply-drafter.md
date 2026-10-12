---
name: x-reply-drafter
description: Draft replies and quote posts on other people's X (Twitter) posts from a URL or pasted text, in Lorenzo's voice. Produces 1-3 variants that add a number, a missing piece, or a sharper question, sized for X. Use when the user pastes an X/Twitter link and says reply, respond, engage, or quote; or asks for "my X replies for today". Not for replies on Lorenzo's own threads when he can just answer directly.
---

# X reply drafter

Replies are the main growth lever on X: a sharp reply under a bigger account's
post shows up for that account's audience. This module is the X sibling of
`linkedin-comment-drafter` and reuses its templates, resized for X.

## When to use

- The user pastes one or more `x.com/.../status/<id>` or `twitter.com` links
  and asks for a reply or quote.
- Daily reply session: the dossier lists X reply targets; run this on each.
- "Quote this with my take".

## Input

A post URL or the pasted post text. X blocks most anonymous fetches, so:

1. Try WebFetch on the URL once.
2. If it fails or returns a login wall, **ask the user to paste the post text**
   (and the top replies, optionally). Never guess the content.

## Templates

Use the 7 templates in
`references/writing/linkedin-comment-drafter/references/comment-templates.md`
with these X adjustments. They are labeled CT1-CT7 here so they don't
clash with the T1-T10 hook codes of `x-post`; CTn = template Tn in that file.


| Template | On X |
|---|---|
| CT1 Missing-Piece | Best default. Agree in 3-5 words, then the piece they left out. |
| CT2 Answer-the-Question | When the post ends with "?". Direct answer + one specific. |
| CT3 Data-First | Lead with the number. Works best under data/AI posts. |
| CT4 Practitioner Observation | "when X, the system does Y". Shows you've run the thing. |
| CT5 Counter-with-Concession | Concede, then push on one point with one reason. |
| CT6 Quotable-Reframe | One line under 12 words. Best for quote posts. |
| CT7 Sharper-Question | Reframe their question one level deeper. |

The LinkedIn sales templates (account warmup, expertise-building) don't apply
on X.

## Reply vs quote

- **Reply** (default): adds to their conversation, shows to their audience.
- **Quote**: only when Lorenzo has a real counter-take or a more specific
  example, and the take stands alone without the original. 2-4 per week max.

## Steps

1. Get the post text (see Input).
2. Pick the target type: peer (similar size), bigger account, prospect (his
   audience: data engineers moving into AI/senior scope), or a viral post in
   his niche. Bigger accounts get a sharp observation, never agreement.
3. Draft 2-3 variants, each a different template.
4. Voice pass (`references/writing/linkedin-comment-drafter/references/voice-rules.md`
   with the X lengths below, then the X block of
   `references/shared/humanizer/platform-scrub-rules.md`).
5. Show: post URL, each variant with template label, char count, and a
   one-line "why this fits". Mark one as the pick.
6. On approval, give the final text in a copyable block. Lorenzo posts it by
   hand (Buffer can't reply to other people's posts). Don't log replies in the
   pipeline.

## X lengths

- Reply: 80-250 chars. One or two short lines. Hard max 280.
- Quote: under 200 chars so the embedded post keeps the attention.

## Hard rules

- Lowercase sentence openings and `..` soft pauses, as in LinkedIn comments.
  Capitalize people's names, products, and acronyms.
- At least one specific: a number, a tool, a date, or a concrete case.
- Never "great point", "this", "100%", "so true".
- Never restate the post. Extend it, answer it, or push on it.
- Never plug Lorenzo's own article or product in someone else's thread unless
  the author asked for resources. Then one link, plainly.
- No hashtags, no emojis, no em dashes.
- Skip the post if it's rage bait, a giveaway, or off his topics; say why.

## Related modules

- `daily-dossier`: lists X reply targets each morning.
- `linkedin-comment-drafter`: same templates, LinkedIn sizing.
- `x-post`: when the reply idea is strong enough to be its own tweet.
