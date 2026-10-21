---
name: install
description: >
  First-run setup for CreatorOS. Interviews the owner in six modules and builds
  the content base from scratch: company and accounts, voice from real samples,
  strategy, channels, cadence and pillars, brand kit (logo, colors, fonts,
  inspirations, design guide, brand book, video theme, diagram palettes), tools
  and Metricool, and an optional import of past content. Resumable: a module
  whose files are already filled is offered as "keep or redo". Use for
  /system install, "set up", "onboarding", "start CreatorOS".
---

# /system install

A discovery conversation, not a form. One question at a time, in the owner's
language (detect it from their first message; content language is asked
separately). Every answer lands in a file before the next module starts, so
the install can stop and resume anywhere.

Show a one-line progress header before each module:
`Setup 2/6 · Voice` and, at the end of each module, what was written.

Ground rules:
- Never invent facts, numbers, competitors, colors or handles. Vague answer →
  record it as given or leave the field, and say which fields stay open.
- Offer to research instead of asking when the web can answer (competitors,
  trends, a public profile). Show what was found and let the owner confirm.
- Accept "skip" on any question. Skipped fields keep their `<...>` placeholder
  and are listed in the final summary.
- Remove the `<!-- creatoros:template -->` marker only from files that are
  fully filled; leave no "fill this later" notes in finished files.
- Files and skills are in English; the content language comes from the owner.

## Module 0 · Pre-check

1. **Folder name.** If the folder is `content-creation`, `creatoros`,
   `CreatorOS`, `creator-os` or another generic name, say you'll suggest a
   rename at the end.
2. **Existing setup.** List which of these still have the template marker:
   `context/company.md`, `accounts.md`, `preferences.md`, `voice-samples.md`,
   `strategy.md`, `pillars.md`, `brand/design-guide.md`. Filled files → ask
   "keep or redo?" per module. If everything is filled, suggest
   `/system update <module>` instead.
3. **Quick tool scan** (read-only, no installs): `node --version`,
   `python --version` or `python3 --version`, `uv --version`,
   `ffmpeg -version`, and whether Metricool tools are present (ToolSearch
   "metricool"). Note the gaps; Module 5 fixes them.
4. Tell the owner the plan in two lines: six modules, about 20-30 minutes,
   skippable, resumable.

## Module 1 · Company → `context/company.md`, `context/accounts.md`

Ask:
1. Brand or person name as it appears on content, and the owner's first name
   (how you'll refer to them).
2. Profile: solo creator, freelancer, agency, or company.
3. What it does, one sentence, "as you'd explain it to a neighbor".
4. The offer: what is sold, and the price or model if it's public.
5. Who pays: the real client profile.
6. Team: solo, or who does what.
7. The audience the content is for, if different from the paying client.
8. Competitors or peer creators (names or handles). Offer: "Want me to research
   your space and list competitors?" If yes, WebSearch 2-3 queries in the
   content language, return a table (name, what they do, link) and keep only
   the ones the owner confirms. Save the research brief to
   `data/research/competitors-YYYY-MM-DD.md` with sources.
9. Handles and URLs per platform (Instagram, LinkedIn, X, TikTok, YouTube,
   Medium, website/newsletter), the public contact email, and the CTA link.
10. Anything else content should know (credentials, location, story).

Write `company.md` (with the competitor table) and the accounts part of
`accounts.md`. Show both.

## Module 2 · Voice → `context/voice-samples.md`, `context/preferences.md`

1. Content language(s), and which channel gets which if more than one.
2. Ask for 2-3 real samples the owner wrote (a caption, a post, an email, an
   article). Pasted text, a file path, or a public URL (WebFetch it). Store
   each verbatim in `voice-samples.md`. If the owner has none, offer to draft
   from their spoken answers so far and mark the fingerprint "provisional".
3. What annoys them in writing: words, phrases, formats.
4. Emojis (none / sparingly / allowed), em dashes (avoid / allowed), hashtags.
5. Fixed phrases, openers or closers they always use (verbatim).

Derive the fingerprint (sentence length, opener, register, person, signature
moves, never-seen items) from the samples only. Write `preferences.md`. Show
the derived tone in 4 lines and ask "sounds like you?" before moving on.

Then sync the voice into the skill references that carry per-owner rules:
- `.claude/skills/content/humanizer/references/voice-fingerprint.md`: replace
  the "Owner baseline" section with the fingerprint.
- `.claude/skills/content/humanizer/references/platform-scrub-rules.md`: the
  global rule line (emojis, dashes) follows `preferences.md`.

## Module 3 · Strategy and pillars → `context/strategy.md`, `context/pillars.md`

1. Phase of the business and the 1-3 goals for the next 90 days (measurable
   when possible).
2. Channels to use, from: Instagram, LinkedIn, X, TikTok, YouTube, Medium (or
   blog/newsletter). For each: its role (anchor, authority, reach, conversion).
3. Cadence per channel: posts per week, which days, weekend or not. If the
   owner has no idea, propose a sustainable default from `platform-rules.md`
   for their available hours per week (ask for that number).
4. Engagement habit (comments on LinkedIn, replies on X) or none.
5. Pillars: propose 3-5 from the answers so far (positioning, audience, offer,
   competitors), each with a mix % and example topics. Iterate until approved.
6. Topic radar: propose high / medium / ignore keywords from the niche and the
   competitors. Confirm. Also fill `.claude/skills/research/news-radar/sources.md`
   with the sources and creators the owner reads (ask) plus what research found.
7. Monthly themes for the next 3 months (propose from goals; confirm).
8. Bottleneck and the weekly task to take off their plate.

Build the weekly slot map (day × active channel, format and formula per slot)
from cadence and pillars, using
`.claude/skills/content/repurpose/references/repurposing-map.md` for format
choices. Write both files. Then edit the root `CLAUDE.md` "Workspace" block:
owner name, active channels, and drop chained-workflow rows for channels the
owner doesn't use (keep the rows; mark inactive ones "(inactive)").

## Module 4 · Brand kit → `brand/`

1. **Logo.** Ask the owner to drop files into `brand/assets/` (or give paths to
   copy): main logo (`logo.png`), a version for dark backgrounds
   (`logo-dark.png`), a square mark (`logo-mark.png`). SVG is fine too. Check
   each file exists and open it (Read) to confirm it's the right image. No
   logo yet → note it; the end card and brand book fall back to the name in the
   display font.
2. **Colors.** Ask for hex codes. If they only have a logo, extract the
   dominant colors (Python + Pillow k-means on the logo, 5 colors) and propose
   them mapped to roles. Fill the design guide's color table (primary, deep,
   accent light, dark bg, light bg, soft bg, ink, muted, line). Ask for the
   palette rule.
3. **Fonts.** Display, body, optional mono, from Google Fonts. If they use a
   non-Google font, ask them to put the TTF/OTF files in `brand/fonts/`.
4. **Style.** Mood in a few words, photo vs. text-only, corner radius, visual
   don'ts.
5. **Inspirations.** Ask for 2-5 posts or carousels they love (screenshots
   into `brand/inspirations/instagram/post-N/`, `linkedin/`, `x/`) and any
   reference video (into `brand/inspirations/video/`). For each video run
   `uv run --project .claude/skills/visual/video-edit/scripts python .claude/skills/visual/video-edit/scripts/vedit.py reference <file> --out brand/inspirations/video/<name>-reference`
   and summarize what it measured (pace, zooms, caption band). Look at the
   images and write 3-5 lines of "what to borrow" into the design guide's
   Inspirations section.
6. **Thumbnails.** Article/YouTube thumbnail style (duotone, photo,
   illustration, none) and how the owner should be drawn, if at all.

Then generate, in order, showing each:
1. `brand/design-guide.md`, fully filled.
2. `brand/video-theme.json` for video renders. Map roles:
   ```json
   {"_from": "brand/design-guide.md",
    "dark": "<dark bg>", "light": "<light bg>", "soft": "<soft bg>", "line": "<line>",
    "inkDark": "<ink>", "inkLight": "<text on dark>",
    "accent": "<accent light, for dark backgrounds>", "accentOnLight": "<primary>",
    "dim": "<muted on dark>", "dimOnLight": "<muted>",
    "track": "<dark bg, 15% lighter>", "trackOnLight": "<soft bg, 8% darker>",
    "bar": "<dark bg, 8% lighter>", "barOnLight": "<light bg>",
    "capIdle": "<text on dark>", "capActive": "<accent light>",
    "fonts": {"text": "<body TTF>", "bold": "<display or body extra-bold TTF>", "display": "<display TTF>"}}
   ```
   Font files: instance the Google Fonts variable TTF to static weights with
   fonttools (as the video-edit skill's fonts were made) into
   `.claude/skills/visual/video-edit/scripts/fonts/`, or reference
   `brand/fonts/<file>` directly. Render one check with
   `vedit.py templates --theme brand/video-theme.json --preview label --params '{"kicker":"<NAME>","title":"<tagline>"}'`
   and show it.
3. Diagram palettes: rewrite the color tokens in
   `.claude/skills/visual/diagram-design/references/style-guide.md` and
   `.claude/skills/visual/excalidraw-diagram/references/color-palette.md`
   from the design guide (keep their structure).
4. Brand book: copy `templates/brand-book.html` to
   `brand/brand-book/brand-book.html`. Fill every `{{...}}` (logo files,
   name, contact), replace the fonts in the `@import` and `font-family` rules
   and the greys in the CSS with the brand palette, and rewrite every section's
   text from `context/` and the design guide (who we are, palette swatches with
   hex, type system, how the brand talks, where the mark lives, what's still
   missing). Keep the page structure and A4 landscape setup. Render the PDF
   with Playwright (`page.pdf`, `preferCSSPageSize: true`) to
   `brand/brand-book/brand-book.pdf`.
5. One sample carousel slide (cover) with `ig-carousel`'s style rules into
   `output/carousels/_brand-check/`, so the owner sees the brand applied.

## Module 5 · Tools and Metricool → `context/accounts.md`, `.env`

1. **Metricool.** `.mcp.json` already registers the server. If the tools are
   missing: tell the owner to run `/mcp`, pick `metricool`, Authenticate, then
   continue. With tools present: `getBrandSettings`. Record brand label,
   blogId, timezone and connected networks in `accounts.md`. Compare with the
   channels chosen in Module 3 and list any not connected ("connect X inside
   Metricool, then run `/system update tools`"). Ask the plan (Free: 20
   scheduled posts/month).
2. **Carousels.** Node 18+ and Playwright: `npx playwright --version`; if the
   browser is missing, ask before `npx playwright install chromium`.
3. **Video engine.** Ask whether they'll edit video here. If yes:
   `uv run --project .claude/skills/visual/video-edit/scripts python .claude/skills/visual/video-edit/scripts/vedit.py doctor`.
   Missing FFmpeg or uv → give the official install command for their OS and
   wait. Missing env → ask, then `uv sync --project ...` (~350 MB) and
   `vedit.py assets`. Say the Whisper model (~1.6 GB) downloads on first
   transcription.
4. **Optional keys.** `OPENAI_API_KEY` (AI photos), `APIFY_TOKEN` (LinkedIn
   import). Ask the owner to add them to `.env` themselves; never ask them to
   paste a key in chat. Record set / not set.
5. Run `/system doctor` and show its table.

## Module 6 · Past content (optional) → `data/archive/`, `data/metrics/`

Ask: "Import your past posts? It seeds your archive, your voice, and your
analytics baseline." If yes, per platform in `accounts.md`:
- Medium, LinkedIn (Apify), X (data export), Instagram (Meta export):
  hand the job to the `archivist` agent with the handles; it follows
  `.claude/skills/content/archive/SKILL.md`.
- With Metricool connected: run `content-analytics` "Sync from Metricool" for
  the plan's history window to fill `data/metrics/`.
Then pick the 3 best-performing posts the owner wrote and offer to add them to
`voice-samples.md` (refines the fingerprint).

## Finish

1. Summary card (owner's language):

```markdown
### CreatorOS is set up for <Name>

- **Company and accounts**: context/company.md, context/accounts.md
- **Voice**: context/preferences.md (from <N> samples)
- **Strategy**: <N> channels, <N> posts/week, pillars P1-P<N>, themes through <month>
- **Brand**: design guide, logo <found|missing>, brand book PDF, video theme, diagram palettes
- **Tools**: Metricool <connected: networks|not connected>, carousels <ok|missing>, video <ok|skipped|missing>
- **Past content**: <N> pieces imported | skipped
- **Still open**: <every skipped field, one line each; omit when none>

Next: `/content plan` for your first week.
```

2. If the folder name is generic, propose a slug from the brand name
   (lowercase, hyphens, no accents: "Acme Studio" → `acme-studio`) and the
   rename command (PowerShell `Rename-Item <old> <new>` from the parent, or
   `mv`), then: close Claude Code, rename, reopen from the new path.
3. Offer to run `/content plan` (theme week from the first monthly theme).

## Rules

- One question per message. Group only trivially related items (name + first
  name; handles table).
- Each module ends by writing its files and showing them. Never batch writes
  to the end.
- Never store secrets in context files; keys live in `.env` (gitignored).
- Don't install system software without a yes. Don't run paid services.
- Skipping is always fine; a skipped module leaves its files with the marker
  and `/system doctor` lists it.
