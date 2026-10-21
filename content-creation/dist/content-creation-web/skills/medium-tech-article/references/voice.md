# Voice (Medium technical articles)

> Reconstructed from `medium-tech-article.md` and `context/preferences.md`
> because the original file was missing. Replace with the original if you have it.

## Sentence level

- Short declaratives. Most sentences under 20 words, with an occasional long one
  that carries a full mechanism.
- First person singular for experience ("I broke this on purpose"), second person
  for instructions ("run this, then check the plan").
- Technical terms used as-is. No definition for anything a mid-level data engineer
  already knows.
- Numbers instead of adjectives: "4.2 s to 180 ms", not "much faster".
- Every claim is followed by its evidence or its price within two sentences.

## Moves that sound like Lorenzo

- **The dare.** Invite the reader to break something: "Kill the primary. Watch what happens."
- **The price line.** "The price: ..." right after a technique.
- **The honest limit.** "This doesn't fix X. For that, see ..."
- **The question header.** Sections named after what the reader would ask, in quotes.
- **The transition.** "Let's [verb]?" into the body.
- **The receipt.** Screenshot placeholder at every measurable moment.

## Banned

- Em dashes, en dashes used as em dashes, double hyphens.
- "In this article we will explore", "Let's dive in", "deep dive", "game-changer",
  "leverage", "robust", "seamless", "unlock", "landscape", "journey".
- Rhetorical question openers that aren't a real symptom.
- Bullet lists of generic best practices without a measurement.
- Soft conclusions ("and that's it!", "hope this helps"). The closer template is fixed.
- Emojis.

## Rhythm check before delivery

1. Read the hook alone. Does it state a symptom, a mystery, or an uncomfortable truth?
2. Any paragraph over 4 lines? Split it.
3. Any claim without a number, plan property, or "why it can't be measured"? Fix it.
4. Any technique without its price? Add it.
5. Run `skills/humanizer/humanizer.md` patterns 1-30 quickly over the full draft.
