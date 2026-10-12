---
name: ig-carousel
description: >
  Creates carousels and visual posts for Instagram, TikTok, LinkedIn with the brand's visual identity.
  Generates styled HTML + renders to 1080x1350 PNG via Playwright, with a ready caption at the end.
  Supports text-only carousel, carousel with AI photo (generated via OpenAI), and single post.
  Use when the user asks for "carousel", "post", "instagram content", "create image",
  "generate photo", "educational post", or /carousel.
---

# /ig-carousel — Carousels and visual posts

Central visual content creation skill. Takes a theme → delivers styled HTMLs + PNGs ready to post + brand-style caption.

## Dependencies

- **Visual identity:** `references/shared/identity/design-guide.md` — READ BEFORE creating any visual
- **Business context:** `references/shared/memory/company.md`
- **Voice and tone:** `references/shared/memory/preferences.md`
- **Playwright:** to render HTML to PNG (`npx playwright screenshot` or via `render.js`)
- **OpenAI API (optional):** to generate realistic photos — only if the client has an API key configured
- **Outputs go in:** `output/carousels/<type>-<theme>-<YYYY-MM-DD>/`

---

## Content types

When receiving a request, identify which type fits:

### 1. TEXT-ONLY CAROUSEL
- **When to use:** educational posts, tips, lists, explanations
- **Format:** 1080x1350 (4:5) — always
- **Style:** clean typography, alternating brand colors, no photos

### 2. CAROUSEL WITH PHOTO
- **When to use:** visual presentation, aspirational content, cover with character
- **Format:** 1080x1350 (4:5)
- **Style:** photo as cover with gradient overlay + inner slides in alternating pattern
- **Photo:** can be AI-generated (via OpenAI) or real (provided by the user)

### 3. SINGLE POST
- **When to use:** impact phrase, data/statistic, testimonial, behind-the-scenes
- **Format:** 1080x1350
- **Style:** varies by content (quote, large number, photo with overlay)

If the type is not clear, ask:
> "What type of content? (1) text carousel, (2) carousel with photo, (3) single post"

---

## Base visual style

The OS has its own style — editorial, calm, premium. No clip-art, no decorative emoji, no rainbow gradient, no generic AI template. `references/shared/identity/design-guide.md` overrides these patterns; when the design guide is vague or blank, use what's here (don't stop to run `/install` — `/carousel` works fine with good defaults).

### Default typography

- **Font:** Inter (Google Fonts), weights 400/500/600/700/800/900
- **Cover title:** 90-100px, weight 900, line-height 0.98, letter-spacing **-0.04em**
- **H2 (inner slides):** 60-72px, weight 800, line-height 1.04, letter-spacing **-0.035em**
- **Body:** 20-24px, weight 500, line-height 1.5
- **Eyebrow/kicker:** 13-16px, weight 700-800, **UPPERCASE**, letter-spacing **0.22-0.32em**, accent color
- **Page counter (top right):** 14-16px, weight 500-600, letter-spacing 0.18em, muted color
- **Meta/handle (@):** 15-18px, weight 600

Typography rule: large titles with **tight** kerning (-0.035em), small eyebrows with **open** kerning (0.22em+). That contrast is the heart of the style.

### Default colors (when design-guide is vague)

Sober palette: dark background + off-white + **ONE** accent color. Never four competing colors.

- Dark background: `#0E1116` or `#1A1A1A`
- Light alternative background: `#F5ECD7` (cream) or `#FAFAF7`
- Text on dark: `#FAFAF7`
- Text on light: `#1A1A1A` (h2) and `#444` (body)
- Accent: brand color (one only)

### Recurring visual elements

- **Thin rule** (3-4px height, 60-80px width, accent color) between kicker and h2 or as divider
- **Logo top-left + page counter top-right** on every slide
- **Border-top 1px** `rgba(255,255,255,0.12)` separating footer from content (on dark slides)
- **Circular stamps** (200x200, border 3px translucent, rotate -10deg) for seals/dates/data
- **Tags/pills** uppercase, generous padding, kerning 0.2em, to label slide category
- Base padding: 70-100px on sides

### Named layouts

Layout vocabulary — each slide has a name. Alternate between them to create rhythm:

- **COVER** — eyebrow + large title + subtitle + @handle. Background: photo with gradient overlay (`rgba(12,10,9,0.55)` → `rgba(12,10,9,0.85)`) OR solid (dark/light/accent)
- **SOLO** — horizontal split: photo left 50% + text right 50% (kicker + h2 + rule + paragraph)
- **DUO** — text on top (kicker + h2 + rule + p) + 2 photos side by side below (or 1 wide photo)
- **NUMBER** — giant numeral (200-320px, weight 800, accent color) as graphic element + h2 + supporting paragraph
- **QUOTE** — large watermark quotes + phrase in h2 + attribution
- **FINAL CTA** — accent color background, centered logo, short headline, button/CTA, phone/@handle

**Slide-to-slide rhythm:** alternate dark ↔ light ↔ accent backgrounds. Never two slides in a row with the same background.

---

## Carousel pattern

**Base structure (5 to 10 slides):**
- **Slide 1:** `COVER` layout
- **Inner slides:** use 2-3 different layouts from `SOLO` / `DUO` / `NUMBER` / `QUOTE`
- **Final slide:** `FINAL CTA` layout

Before creating HTML: read `references/shared/identity/design-guide.md`. If blank, use the "Base visual style" above as default.

### Cover sequence in the feed (grid planning)

Before defining the cover, consider the **last published cover** to alternate:
- light → next is photo/dark
- photo/dark → next is brand color
- brand color → next is light
- never two identical covers in sequence

If the user doesn't know what the last one was, ask.

### Language (critical rule)

Follow `references/shared/memory/preferences.md`. In general: natural sentences, no marketing jargon, no corporate speak. The real audience rarely says "average ticket", "performance", "B2B". Speak the way they speak.

### Caption — always generate alongside

When done rendering the PNGs, **automatically** generate the post caption and save to `caption.md` in the same folder. **Do not wait for the user to ask.** Standard structure:

1. Hook (question or statement)
2. Context (1-2 sentences about the content)
3. CTA to swipe ("Swipe through and check it out")
4. Offer block (company differentiators, contact)
5. Hashtags: Instagram 3-5 targeted (see `references/shared/platform-rules.md`). LinkedIn 0-2 at the end, and the caption follows `references/writing/linkedin-post/references/algorithm-heuristics.md` (hook in first 210 chars, no links in body).

LinkedIn is the primary platform now. For a LinkedIn carousel, also export the slides as one PDF (`carousel.pdf`, LinkedIn document post) and write `caption-linkedin.md` by default.

LinkedIn and Instagram post the same carousel on the same day (see `references/shared/pillars.md`), so write both captions by default: `caption.md` (Instagram) and `caption-linkedin.md`. For X, the strongest single slide (usually the cover or a NUMBER slide) can be attached as an image to that day's tweet; note which one in `copy.md`.

---

## Workflow

### Step 1 — Understand and plan

1. Read `references/shared/memory/preferences.md` and `references/shared/memory/company.md`
2. Read `references/shared/identity/design-guide.md` for colors, fonts, and logo
3. Identify the content type (1, 2, or 3)
4. Define the theme and angle

### Step 2 — Copy

Write the content following the tone rules:

**For carousel (5-10 slides):**
- Slide 1 (Cover): impactful title, max 8 words. Offer 3 options
- Inner slides: one insight per slide, natural sentences, no bullet points
- Final slide: CTA + logo

**For single post:**
- Main phrase highlighted
- Supporting context (if needed)
- Subtle CTA

**CHECKPOINT:** Show the full copy. Wait for approval before moving to visuals.

### Step 3 — Generate photos (if type 2)

Only if the user asked for a carousel with AI photo.

1. Build the prompt in English (the API works better in English)
2. Generic prompt pattern:

```
Professional [TYPE] photography of [SUBJECT],
[DETAILS], [ENVIRONMENT/CONTEXT],
[LIGHT STYLE] lighting, shallow depth of field,
shot from [ANGLE], [STYLE/AESTHETIC],
editorial quality
```

3. Generate via script (if `scripts/generate-image.js` exists):
```bash
node --env-file=.env scripts/generate-image.js "PROMPT" "output/carousels/<folder>/photo-<name>.png"
```

If the script doesn't exist yet, instruct the user to configure `OPENAI_API_KEY` in `.env` and create the script (or use another image generation tool).

4. Show the photo to the user before continuing.

**CHECKPOINT:** Photo approved → continue. If not, adjust prompt and regenerate.

### Step 4 — Create visuals (HTML + PNG)

1. Create **a single `carousel.html`** with ALL slides as `<div class="slide">` inside the same file. Inline CSS, Google Fonts as the only external dependency. Apply:
   - Colors and typography from `references/shared/identity/design-guide.md`
   - Minimum 2 different layouts (don't repeat the same on every slide)
   - Logo top-left + slide-counter top-right on every slide
   - Final slide: logo + CTA, main color background

   **To include AI photo in HTML:**
   ```html
   <div class="slide" style="
     background-image: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.7)), url('photo-xxx.png');
     background-size: cover;
     background-position: center;
   ">
     <div class="content">
       <h2>Text over the photo</h2>
     </div>
   </div>
   ```

2. Create `render.js` in the same folder — a Node script with Playwright that opens the HTML and screenshots each `.slide` at 1080x1350. Can reuse `node_modules` from a previous folder (no need to run `npm install` every time):
```bash
NODE_PATH="<folder-with-node_modules>/node_modules" node render.js
```

3. Show slide 1, slide 2, and the final CTA rendered. If approved, show the intermediate ones.

### Step 5 — Save and organize

```
output/carousels/<type>-<theme>-<YYYY-MM-DD>/
  copy.md               ← approved copy + caption
  photo-<name>.png      ← AI-generated photos (if any)
  carousel.html
  render.js
  instagram/
    slide-01.png → slide-NN.png
  tiktok/ (if requested — 9:16 format)
    slide-01.png → ...
  caption.md            ← Insta+FB caption
  caption-linkedin.md   ← (if requested, more formal)
```

### Step 6 — Log and hand off

Log the carousel in the pipeline (`references/ops/content-pipeline/content-pipeline.md`, format `carousel`). If the user wants it scheduled, hand the caption and the publicly reachable media to `references/ops/buffer/buffer.md`.

Optionally ask whether the theme deserves a full Medium article; if yes, run `references/writing/medium-tech-article/medium-tech-article.md` with the same theme.

### Step 7 — Finalize (after the carousel is approved)

Turns the working folder into a clean deliverable: slide images, `carousel.pdf`
(the LinkedIn document post), and the text files Buffer needs. Destructive, so:
**build the PDF first, show the keep/delete list, and wait for an explicit yes
before deleting anything.**

1. **Locate.** The folder the user named, or the most recent folder under
   `output/carousels/`. Confirm it.
2. **Build the PDF.** From inside the carousel folder:
   ```bash
   NODE_PATH="<folder-with-node_modules>/node_modules" node "<skill-root>/references/writing/ig-carousel/scripts/carousel-pdf.js" instagram carousel.pdf
   ```
   The script auto-detects the slide size from the first PNG (works for 9:16
   slides too). Fallbacks if Playwright isn't reachable:
   `magick instagram/slide-*.png carousel.pdf` (ImageMagick), or Python + Pillow.
   Check the page count matches the slide count before going on.
3. **Show the plan.**

   | Keep | Delete |
   |---|---|
   | All images (`.png .jpg .jpeg .webp`), any subfolder | `carousel.html`, `render.js`, any other `.js` |
   | `carousel.pdf` | `node_modules/`, `package*.json`, `.env` |
   | `copy.md`, `caption.md`, `caption-linkedin.md` | any other file |

4. **Clean** (after the yes). PowerShell, from inside the folder:
   ```powershell
   Remove-Item -Recurse -Force .\node_modules -ErrorAction SilentlyContinue
   Get-ChildItem -Recurse -File | Where-Object { $_.Extension -notmatch '(?i)\.(png|jpg|jpeg|webp|pdf)$' -and $_.Name -notmatch '^(copy|caption.*)\.md$' } | Remove-Item -Force
   ```
   Bash:
   ```bash
   rm -rf node_modules
   find . -type f ! -iregex '.*\.\(png\|jpg\|jpeg\|webp\|pdf\)' ! -name 'copy.md' ! -name 'caption*.md' -delete
   find . -type d -empty -delete
   ```
5. **Report** the final tree. Never touch sibling carousel folders.

After the carousel is published, `references/ops/archive/archive.md` files the
folder into the content archive.

---

## Rules

- Always read `references/shared/identity/design-guide.md` before creating any visual
- Carousel: 1080x1350 (4:5 portrait) — always. TikTok/Reels: 1080x1920 (9:16) — only when explicitly requested
- Language strictly follows `references/shared/memory/preferences.md`
- Always consider the cover sequence in the feed before defining a new cover
- Always generate caption automatically at the end, saving to `caption.md`
- AI photos: always ask for approval before using in the carousel
- AI photos: prompts in English
- AI photos: never generate photos of identifiable people/faces
- HTMLs: a single `carousel.html` file with all slides + `render.js` in the same folder. Inline CSS
- Render: reuse `node_modules` when possible (don't run `npm install` in each folder)
- Don't repeat layout between slides — use visual variation
