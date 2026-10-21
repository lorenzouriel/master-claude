# Visual Identity

> Visual reference for all generated content. Skills read this before creating visuals.

---

## Colors

### Primary (strokes and text)
- Primary: #5F5F5F
- Variation: #606060
- Smooth curves: #626262

### Light mode backgrounds
- Pure white: #FFFFFF
- Soft background: #F5F5F5
- Slightly darker: #EFEFEF

### Dark mode
- Background: #000000
- Near-black softened: #1A1A1A
- Light stroke: #BFBFBF
- Highlight variation: #CFCFCF

The palette is monochromatic. No primary colors, no accent colors. Clean, minimal, technical.

---

## Typography

| Font | Role | Where |
|------|------|-------|
| Fraunces (serif) | Display and titles | Name on homepage, page headings, article titles, lede paragraph |
| Inter (sans-serif) | Body text | All paragraphs, descriptions, nav links, definition lists |
| JetBrains Mono (monospace) | Metadata and labels | Section labels ("STACK", "EM RESUMO"), detail keys, reading times, footer, external links |

---

## General style

Direct. Confident. Technical but human. Monochromatic. Minimal.
Short sentences, specific numbers, → arrows for lists, problem → solution structure, no emojis.

---

## Key elements

- Borders: thin, subtle (#EFEFEF or #BFBFBF on dark)
- Card border radius: small (4-8px)
- Buttons: flat, no shadows, uppercase or sentence case
- Shadows: none or very subtle

---

## What to NEVER do

- No emojis in any content
- No corporate jargon or AI-sounding phrases
- No em dashes: use commas, periods, or colons
- No bold headers with colons in lists
- No soft vague conclusions
- No primary accent colors; the palette is monochromatic only

---

## Exception: article thumbnails

Article thumbnails (Medium headers) use the locked duotone electric-violet
series defined in `skills/thumbnail-prompt/thumbnail-prompt.md`.
That is the only place a color accent is allowed. Carousels, documents, and
every other visual stay monochromatic.

---

## Logo

Paths relative to the project root.

- Light version: `brand/assets/uriel-logo.png`
- No background: `brand/assets/uriel-logo-nobg.png`
- Left cover: `brand/assets/uriel-left-cover.png`
- Right cover: `brand/assets/uriel-right-cover.png`

If a listed file is missing, use `uriel-logo.png` and tell the user.
- Where to use: carousel CTA slide, proposal header, presentation slides
- Suggested size: width between 120-200px in HTML files

## Other assets

- `brand/assets/monkey.png`: black-and-white "thinking chimp" stock photo.
  Not a brand mark; use only as a meme-format image, never as a logo.

---

## Brand book

The full brand guidelines for sharing with designers or clients:

- `brand/brand-book/brand-book.pdf`: the shareable PDF
- `brand/brand-book/brand-book.html`: the source; it loads the logos from
  `../assets/`, so keep it inside `brand/brand-book/`

When colors, fonts, or logos change, update this guide first, then regenerate
the brand book so the two never disagree.
