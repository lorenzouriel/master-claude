# Voice rules

These are the global voice rules every drafted comment must pass before it's
shown for approval. They're reconstructed from the constraints specified across
this skill (the Hard rules in `linkedin-comment-drafter.md`, the Anti-patterns table and
Length & Weight rules in `comment-templates.md`). If you have an original
`voice-rules.md` from your feedback memories, replace this file with it.

## The tells to strip (AI-detector pass)

These are the patterns that make a comment read as machine-written. Remove every
one of them:

- **No em dashes (`—`).** When you need that beat, use a double dot (`..`) the way
  the templates do: `the moat moved.. taste won`. Never substitute with a single
  hyphen pretending to be an em dash either.
- **No rule-of-three lists.** "faster, cheaper, better" style triads are a tell.
  Make one point well.
- **No "it's not X, it's Y" construction.** Overused, instantly recognizable.
- **No AI vocabulary**: delve, leverage, tapestry, testament, landscape, realm,
  navigate (figurative), unlock, elevate, robust, seamless, game-changer.
- **No uniform sentence rhythm.** Vary length. A short punch after a longer line
  reads human; three medium sentences in a row reads generated.
- **No hashtags.**
- **No emoji** unless the post you're replying to uses them first.

## Casing and address

- **Lowercase sentence openings** are the house style. Every real example in the
  template library opens lowercase (`the tools-as-equalizer argument..`,
  `half the sales calls..`, `when tools are exposed directly..`). Keep it.
- **Always capitalize the author's name** when you address them by first name.
  Lowercasing a person's name reads careless, not casual.
- Proper nouns, product names, and acronyms keep their normal casing.

## Substance requirements

- **Always include one specific anchor**: a number, a date, a named entity, or a
  concrete case. A comment with no specific is just an opinion and gets ignored.
  If the draft has none after the template fill, add one before showing it.
- **No generic praise.** "Great post!", "This.", "100%", "Couldn't agree more",
  "So true" are dead on arrival. The skill refuses to ship them.
- **Don't restate the author's thesis back to them.** Extend it, sharpen it,
  answer it, or push on it. Restatement gets zero replies.
- **Never name your own product.** Describe what you do in plain terms instead.
- **Don't tag a third party** to farm reach.

## Length

- Target **200-350 characters** (~25-50 words), **1-2 short paragraphs**.
- Hard floor: comments under ~10 words get near-zero algorithmic weight. Aim for
  12+ words minimum.
- Hard ceiling: over 500 characters reads as a thread hijack. Don't exceed it
  unless you're answering a direct question with real depth, and even then stay
  tight.

## Final self-check before approval

Run this list against every variant:

1. Any em dash, hashtag, or unprompted emoji? → strip.
2. A rule-of-three or "not X, it's Y"? → rewrite.
3. At least one specific number / name / date? → if not, add one.
4. Author's first name capitalized? → fix.
5. Is this restating the post or adding to it? → if restating, pick a different template.
6. Between 200-350 chars? → trim or expand.
