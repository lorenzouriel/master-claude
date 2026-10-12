---
name: seo
description: Search and AI-answer optimization for Lorenzo's Medium articles and portfolio. Keyword and demand research for a topic, SERP competition check, on-page package for a draft (title, subtitle, SEO title, meta description, tags, slug, headings), topic clusters for the content plan, and GEO/AEO (getting cited by ChatGPT, Perplexity, Claude, Gemini) with a 0-100 score, restructure, re-score loop. Use for "SEO", "keywords for", "will this rank", "optimize this article", "meta description", "Medium tags", "topic cluster", "GEO", "AEO", "get cited by AI", "optimize for AI".
---

# SEO + GEO

Medium articles rank on Google and get quoted by AI assistants for years after
the LinkedIn post is forgotten. This module makes each Wednesday article
findable, and keeps a research trail so topics compound into clusters.

## Modes

| Mode | Trigger | Output file |
|---|---|---|
| `research` | "keywords for X", "is there demand for X", before writing | `data/seo/<YYYY-MM-DD>-<slug>-research.md` |
| `on-page` | a finished draft, "optimize this article", "meta/tags" | appended to the research file, or `data/seo/<slug>-on-page.md` |
| `geo` | "AEO", "get cited by AI", "optimize for AI" | `data/seo/<slug>-geo.md` (scores) + the restructured draft |
| `clusters` | monthly planning, "topic cluster", "what should I write next for search" | `data/seo/clusters.md` (one living file) |
| `monitor` | monthly, "is my SEO working" | `data/seo/monitor-<YYYY-MM>.md` |

Default when a draft is pasted with no instruction: `on-page`, then offer `geo`.

Storage rules: `references/shared/storage.md`.

## Rules (all modes)

- **Research must be real.** Use WebSearch/WebFetch. Never invent search
  volume, difficulty, or rankings. If a number isn't available from a real
  source, say "volume unknown" and reason from SERP evidence instead.
- Copy follows `references/shared/memory/preferences.md`. SEO never beats voice:
  no keyword stuffing, no "ultimate guide" titles Lorenzo wouldn't write.
- Don't change medium-tech-article's skeleton (hook, `Let's [verb]?`, Overview,
  closer). Optimize inside it.
- If data is uncertain, say so.

---

## research

1. **Seed terms** from the topic, the pillar (`references/shared/pillars.md`),
   and how the audience phrases the problem.
2. **Expand** into groups and record for each: intent (informational,
   comparison, how-to, troubleshooting), relevance to Lorenzo's pillars, and
   suggested use (article title, H2, FAQ, skip).
   - Problem/symptom terms ("airflow task stuck in queued").
   - How-to terms ("incremental load delta lake fabric").
   - Comparison terms ("iceberg vs delta 2026").
   - Concept terms ("what is a medallion architecture").
3. **Evidence of demand** (no paid tools assumed): Google autocomplete and
   "People also ask" via WebSearch, Google Trends if reachable, Reddit
   r/dataengineering and Stack Overflow question counts, HN discussion.
4. **SERP check** for the top 5 terms: who ranks (docs, vendor blogs, Medium,
   Reddit), content type and depth, what the top results miss. The gap is the
   angle: usually the measured, lab-first version nobody wrote.
5. **Recommend**: primary keyword, 2-3 secondary, the angle, and a working
   title. Hand the angle to `medium-tech-article`.

## on-page (for a finished draft)

Produce, with char counts:

| Field | Rule |
|---|---|
| Title | Under ~60 chars, primary keyword early, Lorenzo's voice |
| Subtitle | Second keyword + the promise, under ~140 chars |
| SEO title (Medium story settings) | 40-60 chars; can differ from the display title |
| Meta / SEO description | 140-156 chars, states the outcome |
| Slug | Short, keyword-first, no stop words (Medium story settings, "customize link") |
| Tags | Up to 5, most specific first, each with real activity on Medium |
| Headings | H2s that match how people search; Lorenzo's quoted-question headers already do this, keep them |
| Internal links | 2-3 `(check here!)` links to related published articles (`lab-universe.md`) |
| Image alt text | One line per screenshot placeholder |

Also flag: keyword missing from the first 100 words, H2s that hide the topic,
paragraphs over 100 words.

## geo (AI answer optimization)

Score, restructure, score again. Full rubric and capsule rules:
`references/aeo-scoring.md`.

1. **Score** the draft 0-100 (answer capsules 30, question headings 20, link
   hygiene 15, paragraph structure 15, semantic clarity 10, paywall position 10).
2. **Restructure**, with Lorenzo's approval per change type:
   - A 50-80 word answer capsule right after each content H2. Clinical and
     standalone; his voice stays in the text below it.
   - Headings phrased as the question people ask (his quoted-question style).
   - No links inside capsules.
   - Split paragraphs over 100 words.
   - Member-only articles: make sure at least 2 capsules sit in the free part.
3. **Re-score** and show before/after, plus 3-5 test prompts to paste into
   ChatGPT/Perplexity after publishing.

Never add claims the draft doesn't support. A capsule summarizes what the
section already proves.

## clusters

Maintain `data/seo/clusters.md`: one pillar page (the most complete article
on a topic) and its satellites (narrower articles that link to it), per theme.
Each row: target query, status (published URL or `planned`), pipeline id.
Feed `planned` rows into `content-pipeline` as ideas with the pillar code.
Align with the month's dominant theme in `strategy.md`.

## monitor (monthly)

1. Medium stats: views and reads per article, external referrers (Google,
   ChatGPT, Perplexity show up as referrers).
2. Google Search Console, only if Lorenzo has a verified property for his
   portfolio or custom domain. Medium-hosted posts have no GSC access.
3. AI citation check: for 5 published articles, paste their H2 questions into
   ChatGPT and Perplexity; record cited / not cited / competitor cited.
4. Next actions: refresh 1-2 articles that rank on page 2, restructure
   uncited ones with `geo`.

## Related modules

- `medium-tech-article`: writes the article; seo runs after the draft.
- `copywriting`: title and subtitle alternatives.
- `content-pipeline`: clusters become backlog ideas.
- `topic-research`: deeper "what are people saying" research on a topic.
