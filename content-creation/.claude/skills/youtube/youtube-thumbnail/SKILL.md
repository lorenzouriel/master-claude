---
name: youtube-thumbnail
description: Generate a brand-consistent thumbnail for a YouTube video. For Claude Code only. Activate when the user asks for a YouTube thumbnail or video cover image. Reads the video title and topic, designs a thumbnail optimized for YouTube CTR (face + text + bold focal color), then runs generate.js to call Google's Gemini image API. Distinct from the youtube/sub-skills/thumbnail.md design brief skill — this skill generates the actual image.
---

# YouTube Thumbnail Skill (Claude Code)

Generate brand-consistent click-optimized thumbnails for YouTube videos.

> **This skill is designed for Claude Code only.** It uses Bash to invoke `generate.js`. Claude Desktop cannot drive this skill.
>
> **Relationship to `sub-skills/thumbnail.md`:** The existing thumbnail sub-skill produces a design brief (scene plan, A/B variants, CTR benchmarks). This skill generates the actual image via Gemini. They work in sequence: run the sub-skill first to nail the brief, then use this skill to generate. Or use this skill standalone for quick-turnaround thumbnails.

## When to use this skill

Activate when the user:

- Provides a video title/topic and asks for a thumbnail image
- Says "generate my YouTube thumbnail", "make a YouTube thumbnail", "create the thumbnail for this video"
- Has a thumbnail brief (from `sub-skills/thumbnail.md`) and is ready to generate

Don't use for channel art, banner images, or end screens.

## Canvas Specifications

| Format | Size | Ratio | Use |
|--------|------|-------|-----|
| Standard thumbnail | **1280×720 px** | 16:9 | YouTube's required format |
| Maximum file size | **2 MB** | — | Platform upload limit |
| Search result display | ~**210×118 px** | 16:9 | Desktop search; primary legibility target |
| Mobile display | ~**168×94 px** | 16:9 | **The critical legibility floor** |
| Home feed / suggested | ~**246×138 px** | 16:9 | Right rail and homepage |
| Profile grid (small) | ~**120×68 px** | 16:9 | Channel page video list |

**Always generate at 1280×720 px.** YouTube scales down; design at full resolution.

**168×94 px is the non-negotiable legibility floor.** This is how thumbnails appear on mobile — the highest-traffic YouTube surface. Every text element, face expression, and key prop must still communicate at that size. If it doesn't read at 168×94 px, it doesn't belong in the thumbnail.

## Prerequisites

1. **Gemini API key** with billing enabled — stored in `.env` (`GOOGLE_AI_API_KEY=...`) in the cwd, OR exported in shell rc.
2. **`generate.js` in the cwd** — the zero-dependency Node script that ships with this skill.
3. **Node.js 18+** installed.
4. **BRAND BLOCK filled in below** — every `[FILL IN ...]` marker replaced.

If the BRAND BLOCK still has `[FILL IN]` markers, stop and tell the user to edit this SKILL.md first.

---

## BRAND BLOCK

> Filled from `brand/design-guide.md` and the locked thumbnail series in `.claude/skills/medium/thumbnail-prompt/SKILL.md`. Thumbnails are the one place the brand allows a color accent. Change this block only when the brand changes there.

### Characters

**Primary character description:**
The presenter description from the Thumbnails section of `brand/design-guide.md`, rendered in the thumbnail style, never photoreal. Expression default: focused or mildly surprised, not cartoonish. Include the presenter only when a reference photo is available (see below); otherwise the thumbnail is object- or hands-driven. If the design guide says "never draw the owner", never include a face.

**Secondary character (optional):**
None.

**Reference image paths:**
- Primary character ref: optional. Ask the user for a photo path the first time a face is needed; if none, skip the face.
- Secondary character ref: none
- Style anchor: the cover or thumbnail asset named in `brand/design-guide.md` (Other assets), if any

### Output

**Aspect ratio:** `16:9`
**Pixel size:** `1280×720`
**Output directory:** `output/thumbnails/youtube/` (relative to the project root)

### Composition policies

**Illustration / visual style:**
The thumbnail style in `brand/design-guide.md`. With the duotone engraving preset: pure black background, all line work in engraved greys and white, plus one luminous spot color in the brand accent (pushed brighter so it reads on black). The accent marks the idea or payoff, never the background. No other hues.

**Background policy:**
Per the design guide (preset: pure black `#000000`). No gradients, no environment scenes.

**Element count:**
3 elements max: primary subject (face, hands, or one object) + one accent focal element + 1-3 word text overlay.

**Face policy:**
Face optional (see Characters). When used, left or center third, engraved style, expression legible at 168×94 px. Never a neutral, bored stare.

**Environment policy:**
None. The subject floats on black.

**Text in image:**
1-3 words that complement the title, never repeat it. The display font from the design guide, bold (or a heavy sans fallback), white `#FFFFFF`, uppercase allowed; one word may be violet for emphasis. No emojis, no em dashes. Must pass the 168×94 px test.

**Prop selection style:**
One data or AI-native object that shows the payoff: a pipeline diagram fragment, a query plan, a terminal window, a server rack, a cost chart dropping. Engraved, identifiable at 168 px wide.

**Banned visual elements:**
Emojis, red arrows and circles, stock-photo collages, competitor thumbnails, logos of other products as the main subject, more than one accent color, text longer than 3 words, neutral or exaggerated meme faces.

**YouTube-specific rules (always apply):**
- Text overlay: **maximum 3 words**, bold weight, white fill (black stroke only if it sits over engraving), legible at 168×94 px
- Face expression: if featured, must be a **high-energy emotion** legible as a thumbnail-sized silhouette
- Information split: thumbnail text must NOT duplicate the video title — it must add complementary info that creates curiosity when read with the title
- 16:9 is mandatory — portrait or square crops are invalid
- All elements must be distinguishable at **168×94 px** — the mobile display floor

---

## Workflow

### Step 1 — Read the video brief

Identify:
- **Video title** (exact — this is what the thumbnail MUST complement, not duplicate)
- **Core payoff**: what does the viewer gain or feel after watching? Show that in the thumbnail.
- **Information split**: title handles X (what the video is about) → thumbnail must handle Y (the emotion, the outcome, the stakes, the surprise). Never the same information twice.
- **Emotional hook**: shock, aspiration, curiosity, humor, urgency — which one drives clicks for this video?
- **Niche-native props**: one object that belongs to this video's world and can be recognized at 168 px wide.

### Step 2 — Design the scene per BRAND BLOCK policies

Use this structure. The information split check is non-negotiable for YouTube:

```
SCENE PLAN
- Video title: ...
- Title communicates: <what information the title already provides>
- Thumbnail must add: <the complementary emotion/outcome/stakes that title does NOT say>
- Information split: VALID — <title handles X, thumbnail handles Y, no overlap>
- Format: 16:9, 1280×720 px
- Composition: <rule-of-thirds layout — face position, text position, prop position>
- Face expression: <specific high-energy emotion + physical description — not just "surprised" but "wide eyes, open mouth, hand raised to cheek">
- Text overlay: <exact 1-3 words, font style, color, position — must not overlap face>
- Key prop: <one object that shows the payoff — what is it doing that conveys the outcome?>
- 168×94 px check: <what must still read at mobile thumbnail size — face emotion? text? prop?>
```

### Step 3 — Confirm with user

Show the SCENE PLAN and information split analysis. Offer 2-3 variants if the video has multiple angles to test. For YouTube, A/B testing thumbnails is common — offer to plan multiple concepts for the user to test by swapping thumbnails in YouTube Studio after publishing.

### Step 4 — Generate via Bash

```bash
node generate.js \
  --prompt="<full prompt with scene + YouTube constraints>" \
  --refs="<primary ref>,<secondary ref>,<style anchor>" \
  --output="<output_directory>/<video-slug>-YYYY-MM-DD.png"
```

For A/B variants, run sequentially with `<slug>-v1.png`, `<slug>-v2.png`, etc.

On success, the script prints `OK: <output_path>`.

### Step 5 — Review the output

Check these gates — fail any one and iterate:

- ✓/✗ Canvas is 1280×720 px?
- ✓/✗ **168×94 px test**: face emotion, text, and key prop all legible at mobile size?
- ✓/✗ Text overlay: max 3 words, bold with black stroke, does not overlap the face?
- ✓/✗ Information split: thumbnail adds what the title doesn't?
- ✓/✗ Face expression: high-energy emotion, not neutral?
- ✓/✗ High contrast between all elements?
- ✓/✗ Brand style honored?
- ✓/✗ No banned elements?

### Step 6 — Iterate via edit

```bash
node generate.js \
  --input="<previous output>" \
  --prompt="<what to change AND what to preserve>" \
  --output="<new output path>"
```

For YouTube specifically: if the face expression is wrong, regenerate from scratch (editing rarely fixes identity/expression accurately). For everything else (text, color, prop, background), editing is preferred.

---

## Universal best practices for YouTube thumbnails

1. **168×94 px is the design constraint, not 1280×720 px.** Design at full resolution but validate at mobile size. Every element in the thumbnail was put there for a reason — if it doesn't survive the 168×94 px squint test, remove it.

2. **Information split is the core CTR mechanic.** The title and thumbnail are a two-part system. Together they must create more curiosity than either alone. Title: "I tried X." Thumbnail: shows shocked face + outcome. The viewer doesn't know the outcome — they click to find out. If thumbnail and title say the same thing, one of them is wasted.

3. **Facial expression is the highest CTR driver in most niches.** High-energy emotions (genuine shock, disgust, joy, disbelief) outperform neutral faces by significant margins. The expression must be readable as a tiny silhouette — exaggerated is correct.

4. **Text is there to complete the information split.** 1-3 words only. The text should be the piece of the puzzle the title doesn't give. "WAIT" on a shocked face + "I tested 10 AI tools" in the title creates a question. "I TESTED" on the thumbnail + "I tested 10 AI tools" in the title creates redundancy and kills curiosity.

5. **One prop that shows the payoff.** The best YouTube thumbnails show the result, not the process. A "before" thumbnail (messy desk, broken product) creates more curiosity than an "after" thumbnail — unless the after is genuinely aspirational. The prop should be in a state that the viewer wants to understand: how did it get that way?

6. **Brand color as background.** A consistent background color across all thumbnails builds channel identity. When someone sees your thumbnails in the suggested feed, they should recognize the channel before reading the title. Establish one dominant color and protect it.

---

## PROMPT TEMPLATE

```
Generate a single illustrated frame in the EXACT style of the reference images, featuring the EXACT characters from the references.

YouTube thumbnail — 1280×720 px, 16:9 format. MANDATORY: must be legible at 168×94 px (mobile display).

Scene to render:
<your scene description from Step 2>

Style and constraints (violating any = wrong output):
- Illustration style: <BRAND illustration_style>
- Background: <BRAND background_policy>
- Aspect ratio: 16:9 horizontal — this is MANDATORY
- Primary character must look identical to the first reference image
- Face expression: <specific high-energy emotion described physically — e.g., "wide eyes, raised eyebrows, open mouth, one hand raised to cheek in disbelief">
- <Secondary character identical to second reference — only if applicable>
- Match the style anchor's line weights, palette, and shading exactly
- Text overlay: "<exact 1-3 words>" in bold sans-serif, white fill with 4 px black stroke — positioned <location> — must NOT overlap the face — must be legible at 168×94 px
- Element count: stay within <BRAND element_count>
- All elements must be distinguishable at 168×94 px — no fine details, no subtle gradients
- High contrast throughout — YouTube compresses thumbnails
- Banned elements: <BRAND banned_elements>

168×94 px legibility check: face expression, text, and key prop must all read at mobile thumbnail size.
```

---

## Common pitfalls

1. **Neutral or low-energy face expression.** The most common YouTube thumbnail failure. Edit: "Change the face expression to [specific emotion with physical description]. Keep all other elements identical." If editing doesn't fix it, regenerate from scratch — expression editing is unreliable.

2. **Text overlaps the face.** Gemini sometimes places text across the subject. Edit: "Move the text '[words]' to the [upper/lower] third of the frame. Ensure it does not overlap the face or primary character. Keep all other elements identical."

3. **Text too long.** Sentence-length text is invisible at 168×94 px. Edit: "Replace all text in the image with just the word(s) '[1-3 words]'. Make it bold, white with black stroke. Keep everything else identical."

4. **Thumbnail repeats the title.** Information split failure. The thumbnail text says the same thing as the video title. Redesign the scene plan before regenerating — the fundamental concept is wrong, not the rendering.

5. **Background blends with subject.** Subject gets lost in the background at small size. Edit: "Increase contrast between [subject] and background. Shift background to solid [brand color]. Keep the subject and text unchanged."

6. **Too many elements at full size — unreadable at 168×94 px.** Edit: "Remove [secondary prop/element]. Increase the size of [primary focal element]. Simplify to [max element count]. Keep the concept and style unchanged."

---

## Cost notes

Each `generate.js` call is one Gemini API call. YouTube A/B testing typically requires 2-3 thumbnail variants — budget accordingly. Check current per-image pricing at https://ai.google.dev/gemini-api/docs/pricing — rates vary by model.

Text iteration on the SCENE PLAN and information split analysis is free. Only image generation and edits cost API credits. The user decides how many variants to generate.
