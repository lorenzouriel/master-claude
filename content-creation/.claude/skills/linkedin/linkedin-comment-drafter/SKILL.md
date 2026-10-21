---
name: linkedin-comment-drafter
description: Draft a LinkedIn comment on someone else's post from its URL. Use whenever the user pastes a LinkedIn post URL and asks to comment, engage, reply to the author's question, or be among the first commenters, even if they don't say the word "comment". Produces 1-3 conversation-provoking variants in the user's voice, assigns a reaction type, and hands back the final text to post manually. Not for replying to existing comments on a post.
---

# LinkedIn Comment Drafter

Produce conversation-provoking comments on any LinkedIn post from a URL. The skill
targets the patterns that actually earned author replies in 2026 testing and
avoids the thesis-restatement patterns that die with zero engagement.

## When to use

- The user pastes a LinkedIn post URL and says "comment on this", "draft me a
  comment", or "engage with this post".
- The user wants to be among the first 3 commenters on a viral post.
- The user wants to answer a closing question the author asked.

Do **not** use this skill to reply to an existing comment on a post; the owner
answers those directly. For replies on X, use `x-reply-drafter`.

## Input

A LinkedIn post URL in any standard shape (e.g. `.../posts/<handle>_activity-<id>`,
a `/feed/update/urn:li:activity:<id>` link, or a shortened share link).

## Output

1-3 draft comment variants, each with:

- A 200-350 char body, 1-2 short paragraphs, no em dashes, no hashtags.
- An assigned reaction type: `LIKE`, `PRAISE`, `EMPATHY`, `INTEREST`,
  `APPRECIATION`, or `ENTERTAINMENT`.
- A pattern label (which of the 7 templates was used).
- A one-line note on why that template fits this post.

Then wait for user approval. On approval, hand back the final text + reaction
for the owner to post by hand (react first, then comment).

## Steps

1. **Parse the URL.** Extract the post's activity ID and `post_urn` from the URL.
   All standard LinkedIn URL shapes embed the numeric activity ID; pull it out and
   normalize to `urn:li:activity:<id>`. If the URL is malformed or doesn't contain
   an activity ID, ask the user to re-paste it.

2. **Get the post body.** Try WebFetch on the URL first (public posts sometimes
   render). If an Apify integration is configured (`APIFY_TOKEN` set), fetch the
   post body and its top ~10 existing comments so your draft doesn't duplicate a
   take that's already there. **If neither works, ask the user to paste the post
   text and, optionally, the top existing comments.** Don't guess at the post
   content.

3. **Detect the author's closing question.** If the post ends on a line with a
   "?", the Answer-the-Closing-Question template (T2) usually wins — authors
   reward people who answer the actual question.

4. **Draft 2-3 variants.** Pick the templates from `references/comment-templates.md`
   that fit the post's topic and shape. Fill each with the user's voice phrasing.
   Don't ship near-duplicates: each variant should take a genuinely different angle.

5. **Run the voice/humanizer pass.** Apply every rule in
   `references/voice-rules.md`: strip em dashes (use `..`), kill AI vocab and
   uniform rhythm, lowercase sentence openings, capitalize the author's name, and
   make sure each variant has at least one specific number or named entity.

6. **Present drafts for approval.** Show: the target URL, each variant with its
   pattern label and suggested reaction, and a one-line "why this template fits".
   Ask which to post (or whether to revise).

7. **On approval, hand off.** Give the final comment text in a copyable block
   and the reaction to apply. The owner posts it by hand: react first, wait a few
   seconds, then comment. Metricool can't comment on other people's posts, so there
   is no automated path. Don't log comments in the pipeline.

## Templates (full list in `references/comment-templates.md`)

- **T1 Missing-Piece** (highest hit rate, ~15% author-reply): agree on the premise,
  then name the one piece the author left out.
- **T2 Answer-the-Closing-Question**: direct answer + one concrete example + why it
  matters for their framing.
- **T3 Data-First**: open with a number, anchor it to a dated event, state the new rule.
- **T4 Practitioner Observation**: "when X the system does Y, when X' it does Y'" —
  shows you've operated the thing they're theorizing about.
- **T5 Counter-with-Concession**: concede point 1, push on point 2 with one rooted reason.
- **T6 Quotable-Reframe**: one standalone line under 12 words, then a one-cause expansion.
- **T7 Ask-a-Sharper-Question**: reframe their question one level deeper, then ask
  if they've seen a specific case.

There are also two sales-oriented templates (account warmup, expertise-building)
and a 4-part high-weight comment structure in the reference file. Use the reaction
heuristics table there to pick the reaction type per template.

## Hard rules

Full voice rules are in `references/voice-rules.md`. The non-negotiables:

- **200-350 chars.** Don't exceed 500 under any circumstance.
- **Always capitalize the author's name** when addressing them by first name.
- **No hashtags, no emoji** unless the post itself uses them.
- **Never name the user's own product** on a third-party post. Describe what they
  do instead.
- **Never ship generic praise** ("Great post!", "This.", "100%"). Refuse and pick
  a real template instead.
- **No em dashes, no rule-of-three, no "it's not X, it's Y".**
- **Skip the post entirely** if it's sponsored, a generic listicle, or already deleted.

## Example invocation

See `references/examples.md` for the full walk-through. In short:

> User: "Comment on this: https://www.linkedin.com/posts/<handle>_activity-<id>"
>
> Skill: parses the URL, gets the post body, detects a closing question, drafts 3
> variants, and returns a T2 Answer-the-Closing-Question pick (backup: T1
> Missing-Piece), reaction `APPRECIATION`, a one-line rationale, and an approval prompt.

## Files in this skill

- `linkedin-comment-drafter.md` — this file
- `references/comment-templates.md` — the 7 templates plus sales templates, with
  fill-in slots, real examples, and the reaction heuristics table
- `references/voice-rules.md` — the voice rules every draft must pass
- `references/examples.md` — example invocation

## Related modules

- `daily-dossier` — suggests engagement targets each morning; feed its URLs here
- `.claude/skills/content/humanizer/SKILL.md` — full AI-tell guide if a variant still reads generated
