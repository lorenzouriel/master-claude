# AEO scoring and restructure

Adapted from master-claude's `newsletter-optimization` (originally for
Substack). Used by `seo` in `geo` mode.

**Principle:** do everything AEO requires, add nothing it doesn't. AI models
scan for extractable blocks; give them one per section without touching
Lorenzo's voice in the rest of the text.

The stats often quoted for AEO (zero-click share, citation lift from answer
capsules) come from industry reports, not controlled studies. Treat them as
direction, and trust Lorenzo's own monthly citation checks over them.

---

## The score (100 points)

| Category | Max | What is measured |
|---|---|---|
| Answer capsules | 30 | Every content H2 has a 50-80 word direct answer right after it. Standalone, no preamble. |
| Question headings | 20 | Content H2s phrased as the question a reader would type (How / What / Why / When / Which, or Lorenzo's quoted-question form). |
| Link hygiene | 15 | Zero links inside capsules. Links live in the supporting text below. |
| Paragraph structure | 15 | Paragraphs under 100 words, one idea each. |
| Semantic clarity | 10 | Natural language, no keyword stuffing, varied references to the main entity. |
| Paywall position | 10 | Member-only: at least 2 capsules in the free preview, and the preview is useful on its own. Free or friend-linked article: 10/10. |

Exempt from capsules and question headings: the hook (before the first H2),
`## Overview`, and the closer.

| Score | Meaning | Action |
|---|---|---|
| 90-100 | High citation readiness | Publish |
| 70-89 | Good, minor gaps | Quick fixes |
| 50-69 | Some sections citeable | Restructure the weak sections |
| 30-49 | AI will mostly skip it | Restructure most sections |
| 0-29 | Invisible | Rebuild the section structure |

### Score output

```
AEO SCORE (BEFORE): XX/100

  Answer capsules:     XX/30  (X of Y sections)
  Question headings:   XX/20  (X of Y headings)
  Link hygiene:        XX/15  (X links inside capsule zones)
  Paragraph structure: XX/15  (X paragraphs over 100 words)
  Semantic clarity:    XX/10  (natural / some stuffing / heavy)
  Paywall position:    XX/10  (free / capsules in preview / capsules hidden)

Per section:
  H2 "<heading>": capsule missing | ok (NN words); heading statement | question;
                  links in capsule: N; extractable: yes | no

Top 3 issues:
  1. ...
```

---

## Restructure rules

### Answer capsules (the core)

```markdown
## "How do I stop a Spark job from spilling to disk?"

**<50-80 words. Direct answer, no preamble, no links, no "as I said above".
Specific numbers where the section has them. Makes sense with nothing else
on the page.>**

<Lorenzo's existing text: the demo, the measurement, the price, the dare.>
```

- Under 50 words: too thin to extract. Over 80: often truncated.
- Good capsule: answers the heading, has a specific, commits (no hedging).
- Bad capsule: starts with "So," or "Well,", points elsewhere in the article,
  contains a link, or restates the heading.
- The capsule summarizes what the section proves. **Never add a claim, number,
  or recommendation the section doesn't already support.**
- Bold is the only formatting allowed in a capsule.

### Headings

- Content H2s become the question people ask. Lorenzo's lab style already does
  this (`## Use Case 02: "Who is blocking who?"`); keep the quotes and the
  use-case numbering.
- Natural phrasing only. If it sounds odd as a question, leave it a statement.
- Overview and closer stay as they are.

### Links

Remove links from capsule zones, keep the mention as plain text, and move the
link to the supporting paragraph.

### Paragraphs

Split anything over 100 words at the natural seam. Don't split mid-thought.

### Semantic clarity

Replace repeated exact-match keywords with natural references ("the job",
"Spark", "the executor") without becoming synonym cycling (humanizer pattern 11).

### Member-only articles

AI crawlers and Google see only the free preview of a member-only Medium story.
Make sure the first two capsules sit before the cut, or publish the friend link
in the places AI tools crawl (LinkedIn first comment, portfolio).

### Don't

- Add filler paragraphs.
- Rewrite paragraphs that are fine.
- Reorder sections or change the lab's flow.
- Touch Lorenzo's voice below the capsules.

---

## After restructuring

Show the before/after table, then:

```
AI CITATION TEST (run after publishing):
  1. "<question from H2 #1>"
  2. "<question from H2 #2>"
  3. "<question from H2 #3>"
Paste each into ChatGPT and Perplexity. Record cited / not cited /
competitor cited in data/seo/monitor-<YYYY-MM>.md.
```

## SEO vs AEO

| | SEO | AEO |
|---|---|---|
| Goal | Rank on Google | Get cited by AI assistants |
| Levers | Title, meta, slug, tags, headings, links | Capsules, question headings, clean extraction |
| Measured by | Medium referrers, Search Console (own domain only) | Monthly manual AI queries |

They stack: capsules also win featured snippets, and question headings help
both. Run `on-page` first, then `geo`.
