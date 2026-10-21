---
name: ig-carousel
description: >
  Creates carousels and visual posts for Instagram and LinkedIn with the brand's visual identity
  (claude.ai web build). Builds the slides as an HTML Artifact that prints to a 1080x1350 PDF
  (the LinkedIn document post), converts the PDF to PNG slides for Instagram when the code tool
  is available, saves everything to Google Drive, and writes the captions.
  Use when the user asks for "carousel", "post", "instagram content", "create image",
  "educational post", "carousel to PDF", "finalize carousel", or /carousel.
---

# /ig-carousel — Carousels and visual posts

Central visual content creation skill. Takes a theme → delivers a styled slide Artifact, a PDF for LinkedIn, PNGs for Instagram, and brand-style captions, all saved to Drive.

## Dependencies

- **Visual identity:** `brand/design-guide.md` — READ BEFORE creating any visual
- **Business context:** `context/company.md`
- **Voice and tone:** `context/preferences.md`
- **Artifact tool:** renders the slides as one HTML page Lorenzo can preview and print to PDF
- **Code tool (optional):** converts the PDF to PNG slides (PyMuPDF or pdf2image) and base64-encodes the logo
- **Google Drive connector:** storage, per `context/storage.md`
- **Outputs go in:** Drive `output/carousels/<YYYY-MM-DD>-<type>-<theme>/` (a folder per carousel)
- **Not on web:** Playwright rendering and AI photo generation. Those run in the Claude Code build.

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
- **Photo:** provided by the user (AI-generated photos only in the Claude Code build)

### 3. SINGLE POST
- **When to use:** impact phrase, data/statistic, testimonial, behind-the-scenes
- **Format:** 1080x1350
- **Style:** varies by content (quote, large number, photo with overlay)

If the type is not clear, ask:
> "What type of content? (1) text carousel, (2) carousel with photo, (3) single post"

---

## Base visual style

The OS has its own style — editorial, calm, premium. No clip-art, no decorative emoji, no rainbow gradient, no generic AI template. `brand/design-guide.md` overrides these patterns; when the design guide is vague or blank, use what's here (don't stop to run `/install` — `/carousel` works fine with good defaults).

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

Before creating HTML: read `brand/design-guide.md`. If blank, use the "Base visual style" above as default.

### Cover sequence in the feed (grid planning)

Before defining the cover, consider the **last published cover** to alternate:
- light → next is photo/dark
- photo/dark → next is brand color
- brand color → next is light
- never two identical covers in sequence

If the user doesn't know what the last one was, ask.

### Language (critical rule)

Follow `context/preferences.md`. In general: natural sentences, no marketing jargon, no corporate speak. The real audience rarely says "average ticket", "performance", "B2B". Speak the way they speak.

### Caption — always generate alongside

When done rendering the PNGs, **automatically** generate the post caption and save to `caption.md` in the same folder. **Do not wait for the user to ask.** Standard structure:

1. Hook (question or statement)
2. Context (1-2 sentences about the content)
3. CTA to swipe ("Swipe through and check it out")
4. Offer block (company differentiators, contact)
5. Hashtags: Instagram 3-5 targeted (see `context/platform-rules.md`). LinkedIn 0-2 at the end, and the caption follows `skills/linkedin-post/references/algorithm-heuristics.md` (hook in first 210 chars, no links in body).

LinkedIn is the primary platform now. For a LinkedIn carousel, also export the slides as one PDF (`carousel.pdf`, LinkedIn document post) and write `caption-linkedin.md` by default.

LinkedIn and Instagram post the same carousel on the same day (see `context/pillars.md`), so write both captions by default: `caption.md` (Instagram) and `caption-linkedin.md`. For X, the strongest single slide (usually the cover or a NUMBER slide) can be attached as an image to that day's tweet; note which one in `copy.md`.

---

## Workflow

### Step 1 — Understand and plan

1. Read `context/preferences.md` and `context/company.md`
2. Read `brand/design-guide.md` for colors, fonts, and logo
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

### Step 3 — Photos (if type 2)

AI photo generation needs an API key and a script, so it only runs in the
Claude Code build. On web: ask Lorenzo to upload the photo to the chat (or
point to one in Drive), or switch to a text-only carousel. Never use photos of
identifiable people without his say-so.

### Step 4 — Build the slides (HTML Artifact)

1. One HTML page with ALL slides as `<div class="slide">`, each exactly
   1080x1350 px. Inline CSS, Google Fonts as the only external dependency.
   Apply:
   - Colors and typography from `brand/design-guide.md`
   - Minimum 2 different layouts (don't repeat the same on every slide)
   - Logo top-left + slide-counter top-right on every slide
   - Final slide: logo + CTA
2. **Logo.** Artifacts can't load skill files by path. If the code tool is
   available, read `brand/assets/uriel-logo-nobg.png`
   (or `uriel-logo.png` on light slides), base64-encode it, and embed it as a
   `data:image/png;base64,...` URI. Without the code tool, use a text wordmark
   ("Uriel" in Fraunces) and say so.
3. **Print CSS** so the page prints one slide per PDF page:
   ```css
   @page { size: 1080px 1350px; margin: 0; }
   @media print {
     body { margin: 0; }
     .slide { page-break-after: always; break-after: page; }
     .slide:last-child { page-break-after: auto; }
   }
   ```
   On screen, stack the slides vertically with a small gap and scale them down
   to fit the viewport (CSS `zoom` or a transform on a wrapper) so Lorenzo can
   review them; print must use the full 1080x1350 size.
4. Publish it as an Artifact and show it. Get approval on slide 1, slide 2,
   and the CTA slide first, then the rest.

### Step 5 — Export and save to Drive

1. **PDF (LinkedIn document post).** Lorenzo opens the Artifact, prints
   (Ctrl+P), chooses "Save as PDF", margins "None", background graphics on.
   He uploads `carousel.pdf` back to the chat. Check the page count equals the
   slide count.
2. **PNGs (Instagram).** If the code tool is available, render each PDF page
   to a 1080x1350 PNG (PyMuPDF: `page.get_pixmap(matrix=fitz.Matrix(z, z))`
   with `z` chosen so the width is 1080; or pdf2image at the matching DPI).
   Name them `slide-01.png` ... `slide-NN.png`. Without the code tool, tell
   Lorenzo to export the PNGs in the Claude Code build, or to post the PDF on
   LinkedIn and export images from Canva.
3. **Save** to Drive (protocol in `context/storage.md`): create the
   folder `output/carousels/<YYYY-MM-DD>-<type>-<theme>/`, then upload:
   ```
   copy.md               approved slide copy
   caption.md            Instagram caption
   caption-linkedin.md   LinkedIn caption
   carousel.html         the Artifact source
   carousel.pdf          from step 1
   slide-01.png ...      from step 2
   ```
   Images and the PDF go up as `base64Content` with their real MIME type.

### Step 6 — Log and hand off

Log the carousel in the pipeline (`skills/content-pipeline/content-pipeline.md`, format `carousel`, one row per platform). If the user wants it scheduled, hand the captions and the media to `skills/buffer/buffer.md`. Buffer needs **publicly reachable** media URLs: Drive files are private by default, so either Lorenzo attaches the media in Buffer's own composer, or he shares the specific files ("anyone with the link") and confirms. Never change sharing on his files without an explicit yes.

Optionally ask whether the theme deserves a full Medium article; if yes, run `skills/medium-tech-article/medium-tech-article.md` with the same theme.

### Step 7 — Finalize (after the carousel is approved)

The Drive folder should end with the slides, `carousel.pdf`, and the text
files Buffer needs.

1. Confirm the folder (the one named, or the newest under `output/carousels/`).
2. Check `carousel.pdf` and every `slide-NN.png` exist.
3. Show the plan: keep images, `carousel.pdf`, `copy.md`, `caption*.md`;
   trash `carousel.html` and anything else. Wait for a yes.
4. `trash_file` the listed files (recoverable for 30 days). Never touch
   sibling carousel folders.
5. Report the final file list with links.

After the carousel is published, `skills/archive/archive.md` moves the
folder into the archive.

---

## Rules

- Always read `brand/design-guide.md` before creating any visual
- Carousel: 1080x1350 (4:5 portrait) — always. TikTok/Reels: 1080x1920 (9:16) — only when explicitly requested
- Language strictly follows `context/preferences.md`
- Always consider the cover sequence in the feed before defining a new cover
- Always generate caption automatically at the end, saving to `caption.md`
- Photos: only ones Lorenzo uploads or approves; never identifiable people without his say-so
- HTML: one page with all slides, inline CSS, print CSS for 1080x1350 pages
- Don't repeat layout between slides — use visual variation
