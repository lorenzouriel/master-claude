---
name: thumbnail-prompt
description: Generate an image-generation prompt for a Medium article thumbnail (or a LinkedIn article cover) in the owner's locked thumbnail style from brand/design-guide.md (Thumbnails section). Ships with a duotone halftone-engraving preset recolored with the brand accent. Use whenever the user pastes or links an article (or its draft/notes) and asks for a thumbnail, cover, header, or "thumb" prompt, even if they don't name the style, since the style is fixed. Outputs a ready-to-paste prompt plus one alternative and the thumbnail-survival tradeoff. Not for generating the image itself, and not for arbitrary unrelated illustration styles.
---

# Thumbnail Prompt

Turn an article into a single image-generation prompt that matches the owner's established
header style across Medium and LinkedIn. The output is a *prompt*, not an image: paste-ready
for Midjourney / DALL·E / SD.

The whole job is: read the piece → find the one idea → translate it into one gesture →
dress it in the locked style. Consistency across the series matters more than novelty; the
visual signature is what makes the feed recognizable as the owner's.

## The locked style (never deviate)

Read the **Thumbnails** section of `brand/design-guide.md`. It names the style and the accent
color. If it is still a template, run `/system update brand` first.

When the design guide picks the **duotone engraving preset**, append this style block verbatim,
with `<accent>` replaced by the accent's name (e.g. "electric violet", "burnt orange", "teal"):

```
duotone, single luminous <accent> spot color on black, vintage halftone engraving texture,
etched cross-hatching, no smooth gradients, pure black background, conceptual editorial
header, wide banner crop
```

Any other style in the design guide: write its style block there once (8-15 tokens, same
shape as above) and append that verbatim every time.

Why each token of the preset earns its place:
- **single luminous <accent> spot color on black**: the recurring accent = the *idea / knowledge / creation*. It's the only color. Keep it to one accent element, never two competing tones.
- **no smooth gradients**: stops DALL·E from flattening the engraving into clean vector, which would break series consistency. Keep it even when it feels redundant.
- **vintage halftone engraving texture, etched cross-hatching**: the antique-illustration look. Midjourney renders this natively; DALL·E needs it stated explicitly or it drifts to flat color.
- **pure black background**: the subject and the accent float in black.
- **wide banner crop**: the thumbnail has to read in a feed at small size.

### Color anchor & the contrast rule
The brand accent hex is in the design guide. Use it as the reference for the *base* tone of
engraved elements. For the **glowing idea element** (the starburst / emitted light), push the hue
brighter and more saturated so it punches out of pure black. A muted dark accent on black has low
luminance contrast and goes muddy at thumbnail size. One accent only: don't let the base tone and
the glow read as two separate colors.

## Process

### 1. Find the one idea
Don't summarize the article. Extract the *single* argument it's making — the thesis the reader
should leave with. If the piece has a central tension or reversal (consume vs. create, input vs.
output, fear vs. action, old self vs. new self), that contrast is usually the strongest thumbnail
because it's inherently visual.

### 2. Pick one gesture
Translate the idea into a *single visual gesture* a viewer grasps in under a second. One subject,
one action. The test: could you describe what's happening in the image in one short sentence? If it
needs two, it's too busy and won't survive shrinking to a feed thumbnail.

Recurring vocabulary that fits the style (mix, don't checklist):
- the **accent starburst** = an idea, insight, knowledge, the "aha"
- a **figure in profile** (human or animal) in a contemplative pose
- **hands** doing something — shaping, building, reaching, holding
- **books / open pages** as the source
- **growth metaphors** — a sprout through stone, a crack, something emerging
- a **human head/brain** in cross-section for input/output or transformation themes

Lean on *active* gestures (building, shaping, reaching, emerging) over passive ones (just reading,
just sitting) when the article is about doing something with knowledge — it distinguishes the
thumbnail from earlier passive ones in the series and matches a "do something" thesis.

### 3. Compose the prompt
Order the prompt the way image models parse best:

```
[subject + the single action], [secondary detail if any], [STYLE BLOCK], [mood/theme].
```

Keep the subject description concrete and physical. State the action explicitly. Put the glowing
the accent on the element that represents the idea, not the background.

### 4. Deliver
Give the user:
1. **Primary prompt** — the strongest single gesture, ready to paste.
2. **One alternative** — a different metaphor for the same thesis.
3. **The tradeoff** — one or two sentences on which to pick and why, *always* judged by whether
   it survives shrinking to feed-thumbnail size. Busy / multi-element / fine-detail-dependent
   concepts lose at small scale; name that when it applies.

Keep the framing tight and in the owner's register. No preamble, no restating the article back.

## Example

**Article thesis:** Real learning isn't consuming more content — it's *creating* and *teaching*
with what you already have (input vs. output).

**Primary prompt:**
> A pair of hands reaching into an open book, sculpting a glowing <accent> starburst of light
> into a tangible object rising off the pages, duotone, single luminous <accent> spot color on
> black, vintage halftone engraving texture, etched cross-hatching, no smooth gradients, pure black
> background, conceptual editorial header, wide banner crop, theme of turning knowledge into creation.

**Alternative:**
> A human head in profile split into two halves — left side receiving streams of small symbols
> (books, screens, sound waves), right side emitting a single bright <accent> starburst,
> [style block], theme of transforming input into output.

**Tradeoff:** Go with the primary. The hands-shaping gesture carries the whole "build with what you
read" thesis in one read and holds up at thumbnail size. The split-head alternative is more literal
to the input/output section but the incoming-symbol streams turn to mush when shrunk to a feed
thumbnail.

## Model note (mention only if the user asks how to run it)
- **Midjourney** holds the engraving + duotone natively.
- **DALL·E / SD** drift toward clean flat vector — the `no smooth gradients` + `etched cross-hatching`
  tokens are what hold the vintage look; don't drop them.
- If the model renders the accent too dark, state "bright glowing <accent>, high luminance".
