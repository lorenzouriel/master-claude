---
name: ig-reel-script
description: Write an Instagram Reel script (15-60 s) in Lorenzo's voice, with a timing column, on-screen text, spoken lines, and visual cues, ready to record. Formats - tutorial, story, listicle, opinion, behind-the-scenes. Use for "Reel script", "short video", "vertical video", "script for Instagram", or when the weekly plan has a Reel slot.
---

# Instagram Reel script

Reels are Instagram's reach format. Shares to Stories and completion rate
decide how far a Reel travels, so the first 3 seconds and the pacing matter
more than anything else.

## When to use

- "Write a Reel script about X".
- A Reel slot in the weekly plan, usually the Tuesday concept explainer or the
  Wednesday recap of the Medium article in video form.
- Turning a carousel or a LinkedIn post into spoken video.

## Lengths

| Length | Best for |
|---|---|
| 15-30 s | One concept, a contrarian take, a quick fix |
| 30-60 s (default) | Tutorial steps, a story, an article recap |
| 60-90 s | Rare. Reach drops above 90 s |

## Formats

Tutorial, Story, Listicle, Opinion/Contrarian, Behind-the-scenes. Full
skeletons with timing in `references/script-formats.md`.

Quick pick:

| Source | Format |
|---|---|
| Medium lab or how-to | Tutorial |
| Incident, mistake, career moment (Monday reflection) | Story |
| Friday curated list | Listicle |
| Hot take, tradeoff | Opinion |
| Screen recording of a real pipeline, dashboard, or query plan | Behind-the-scenes |

## Steps

1. **Inputs.** Topic or source piece, pillar (P1-P5), length, format. If the
   source is in the pipeline, set `parent_id`.
2. **Hook (0:00-0:03).** Three layers, each must work alone:
   - On-screen text: 3-6 words, readable muted.
   - Spoken: under 8 words, works with the screen off.
   - Visual: already doing the thing (terminal running, diagram drawing,
     query plan on screen). No title card, no greeting.
3. **Setup (0:03-0:10).** One or two sentences: the stakes or the symptom.
4. **Body.** One idea per 5-10 s. Every beat has a specific: a number, a
   command, a tool name.
5. **CTA.** One action, or none:
   - "Save this for your next incident review." (educational)
   - "Full lab on Medium, link in bio." (Wednesday recap)
   - End on the strongest line (opinion).
6. **Humanizer pass** in `quick` mode with the Instagram Reel block of
   `references/shared/humanizer/platform-scrub-rules.md`. Then read it aloud at
   130-150 wpm and cut anything that runs long; don't speed up delivery.
7. **Approval card.** The script as a table (timing / on-screen / spoken /
   visual), estimated runtime (spoken words / 140 wpm), format, pillar, and a
   caption draft (first 2 lines are the hook, "link in bio" says what's there,
   0-5 hashtags).
8. **On approval.** Save to `output/reels/<YYYY-MM-DD>-<slug>/script.md` and
   log in the pipeline as `drafted` (`platform: instagram`, `format: reel`).
   Lorenzo records and edits; once the video file exists and is publicly
   reachable, `buffer` can schedule it.

## Output format

```
Reel: <title> · <format> · <length target> · P<n>

| Time | On-screen | Spoken | Visual |
|---|---|---|---|
| 0:00-0:03 | ... | ... | ... |
| ... |

Runtime estimate: <words> words ≈ <s> s
Caption:
<caption>
```

## Hard rules

- No greeting openers ("Hey guys", "Welcome back", "So today").
- No "like and subscribe" or any other platform's CTA.
- The first 3 seconds are never a title card or a logo animation.
- On-screen text and spoken line are different words (if identical, one is
  wasted).
- No emojis in on-screen text or caption. No em dashes.
- Never script a number Lorenzo can't show or back up.

## Visual identity

On-screen text follows `references/shared/identity/design-guide.md`:
monochrome, Inter for body text, JetBrains Mono for labels and code. The logo
(`identity/assets/uriel-logo-nobg.png`) only on the last frame, if at all.

## Related modules

- `ig-carousel`: the static version of the same idea.
- `repurpose`: plans Reels as article spin-offs.
- `buffer`: scheduling once the video is rendered.
