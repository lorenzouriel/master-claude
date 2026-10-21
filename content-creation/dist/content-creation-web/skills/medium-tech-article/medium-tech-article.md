---
name: medium-tech-article
description: Write, rewrite, or edit technical articles for Lorenzo's Medium in his engineer-to-engineer voice — lab-first, provable, no fluff. Use this skill whenever the user asks to draft a Medium article, rewrite existing content "in my style", turn notes/study material/documentation into an article, create a hands-on lab or tutorial post, or edit a draft for voice. Also use it when the user pastes raw notes, a Microsoft Learn unit, a command list, or a work document and asks to "make an article" out of it, even if they don't say "Medium". Covers SQL Server, data engineering, AI workflows, and DevOps topics.
---

# Medium Technical Article (Lorenzo's Voice)

Write technical articles that read like one senior engineer showing another how something actually works — with a lab the reader can run, evidence instead of assertions, and named tradeoffs.

## Non-negotiables

These are wrong often enough to state first:

1. **No em-dashes. Ever.** Use periods, commas, colons, or parentheses. This is the single most reliable AI tell.
2. **Prove, don't assert.** Any performance or design claim gets a measurable before/after: STATISTICS IO/TIME, elapsed_ms, a plan property, a row count. If it can't be measured, say why.
3. **Name the price.** Every technique has a cost. State it in the same breath: "The price: ..." / "paid in CPU" / "charges RAM".
4. **Genericize work identifiers.** Company names, internal project names, real DB names, real column names from employers → replace with lab or neutral equivalents. Flag the swap to the user.
5. **Never invent output.** Don't fabricate screenshot numbers or plan values. Use `*Source: Author [screenshot: what it shows]*` placeholders.

## Workflow

1. **Identify the shape.** Lab article, guide, or playbook — see `references/structures.md`. When source material is a course unit, notes, or a command dump, it's usually a lab article and the source's structure should be discarded, not translated.
2. **Find the demo.** For a lab article, ask: what can the reader *break* to feel the problem? The article is built around that moment, not around the feature list. If no demo exists, it's a guide, not a lab.
3. **Check lab continuity.** Read `references/lab-universe.md` before inventing schema. Reuse the `billing` database and its known state.
4. **Draft in the voice.** Read `references/voice.md` for sentence-level rules.
5. **Wire the series.** Cross-link related published articles with the `(check here!)` convention. See `references/lab-universe.md` for what exists.
6. **Deliver as a file.** Save to Drive `output/articles/<YYYY-MM-DD>-<slug>.md` (protocol in `context/storage.md`) and give Lorenzo the link. Also offer the article as a downloadable Markdown file in the chat if he wants to paste it into Medium from there. Then, in chat, explain the structural decisions and flag anything the user must review (version claims, work identifiers, lab-state conflicts).
7. **Log it** in the pipeline as `drafted` (format `article`, platform `medium`, pillar code from `context/pillars.md`). Offer the next steps of the chain: `seo` (on-page package, then optional `geo`), thumbnail prompt, then `repurpose` (the Wednesday set for LinkedIn, X, and Instagram).

## Article skeleton

Every article follows this frame:

```markdown
# Title

*Source: Author*

---

Not a medium member? Read here!

[Hook: 2-5 short paragraphs. A symptom, a mystery, or an uncomfortable
truth. Never "In this article we will explore..."]

[Optional: series context + cross-links]

Let's [verb]?          <- the transition into the body

## [Sections: see references/structures.md]

## Overview

[Numbered recap, 5-8 items, one line each. Compresses the article.]

What about the next steps?

Save the content here, [specific action tied to this article's demo].
It is the best way to learn!
```

The closer is a template with one variable: the dare. Make it specific to what the article proved ("shrink a data file and watch the fragmentation explode", "kill your primary a few times"). Never generic.

## Section headers

Use questions the reader would actually ask, in quotes, when the article is a lab or playbook:

- Good: `## Use Case 02: "Who is blocking who?"`
- Good: `## When NOT to Use JSON`
- Bad: `## Blocking Analysis` / `## JSON Best Practices`

Optionally add a bolded tool line under the header: `**DMVs: sys.dm_exec_requests + sys.dm_exec_sql_text**`

## Defaults

- **T-SQL** with bracketed identifiers `[dbo].[table]`, aliases on tables.
- **Python** for non-SQL code unless the topic dictates otherwise.
- Length: 5-13 minute read. Compress source material aggressively; a 6-unit course becomes one article.
- Tables for comparisons and decision matrices. Bullets only when they genuinely aid scanning.
- Screenshot placeholders at every measurable moment.

## When rewriting existing content

The user's own drafts and third-party material (Microsoft Learn, docs) get the same treatment:

- Rewrite completely in Lorenzo's words. Never lift sentences from third-party sources.
- Keep working code verbatim. Fix it only if it's broken (e.g., a compose snippet missing its `services:` key).
- Add what the source lacks: the failure mode, the measurement, the tradeoff, the "when NOT to".
- Cut what the source over-explains: definitions the reader knows, generic best-practice lists.
- Report the structural changes in chat so the user can push back.

## Reference files

- `references/voice.md` — sentence-level rules, the move list, banned patterns. **Read before drafting.**
- `references/structures.md` — the three article shapes with section patterns.
- `references/lab-universe.md` — the `billing` lab canon, published articles, cross-link conventions. **Read before writing any lab.**
