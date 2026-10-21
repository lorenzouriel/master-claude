# Voice fingerprint

How to keep the owner's voice while scrubbing AI tells. The goal is not a
generic clean text. It is their clean text.

The baseline below is derived at `/system install` (module 2) from
`context/voice-samples.md` and `context/preferences.md`. When the owner gives a
fresh sample, calibrate against the sample first and this file second.

---

## Owner baseline

<!-- creatoros:template: /system install fills this table from the samples -->

| Dimension | Default |
|---|---|
| Sentence length | <short / mixed / long; typical length> |
| Word level | <plain / technical terms as-is / ...> |
| Person | <I / we / you; when each> |
| Openings | <how posts start> |
| Punctuation | <dashes, arrows, ellipses, casing habits> |
| Casing | <normal / lowercase in replies / ...> |
| Confidence | <hedging or conviction; how limits are admitted> |
| Evidence | <numbers, stories, examples> |
| Signature moves | <recurring moves seen in the samples> |
| Never | <the avoid-list from preferences.md> |

## Extracting a fresh sample

If the owner pastes something they wrote, note before rewriting:

| Dimension | Look for | Apply |
|---|---|---|
| Sentence length pattern | Ratio of short to long | Match the ratio |
| Word choice level | Casual vs technical | Don't upgrade or downgrade |
| Paragraph starts | Straight in vs context first | Match |
| Punctuation habits | Parentheses, colons, `..` | Preserve; they are voice |
| Recurring phrases | Verbal tics | Keep 1-2 per piece, don't overuse |
| Transitions | Explicit connectors vs none | Match |
| First-person density | How often "I" | Keep the ratio |

---

## Per platform

### LinkedIn
- Posts: short paragraphs, double line breaks, a real moment of stakes or
  vulnerability, one specific number at least.
- Comments: lowercase openings, `..` pauses, the author's first name
  capitalized, 200-350 chars.

### X
- Ultra-short lines as punches are voice, not grammar errors.
- Single-word reactions ("Exactly." "No.") are fine in replies.
- Replies: lowercase openings and `..` like LinkedIn comments.
- Abbreviations only if the owner uses them in the sample. Don't add "tbh",
  "ngl" on their behalf.

### Instagram
- Slide copy: one idea per slide, shorter than LinkedIn, same voice.
- Captions: first two lines carry the hook; the rest can be the LinkedIn
  argument compressed.
- Reels (spoken): direct "you", short punches, natural markers they would
  actually say ("here's the thing:"); read aloud before approving.

### Medium
- The article skeleton phrases are fixed (see `platform-scrub-rules.md`,
  "Do NOT scrub on Medium").
- Question headers in quotes, the price line, screenshot placeholders.

---

## Never flatten

- Intentional repetition for emphasis.
- Self-corrections mid-text ("(I was wrong about this at first)").
- One acknowledged uncertainty ("I could be wrong, but...").
- Specific numbers and named entities: add more, never remove.
- A weird detail only the owner would know. That is usually the best line.

## When no sample is given

Use the baseline above. Replace every vague quantity with a specific one; if
you don't have the number, ask. Don't invent it.

## The read-aloud test

Read the result aloud. If it sounds like an engineer talking to another
engineer, it's done. If it sounds like a press release, or like someone
reading a script, keep going. Any sentence that makes you stumble gets
rewritten.
