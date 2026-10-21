---
name: copywriting
description: Conversion copy for the owner's own surfaces. Headlines and titles (Medium titles and subtitles, carousel covers, hook alternatives), CTAs (end-of-article, first comments, link-in-bio lines), profile copy for the four channels (X bio, LinkedIn headline and About, Instagram bio, Medium bio), and page copy for the portfolio, consulting offer, or future SaaS landing page. Use for "write copy for", "headline options", "better title", "CTA", "rewrite my bio", "LinkedIn headline", "landing page copy", "about page".
---

# Copywriting

Copy that gets one specific action from one specific reader. This module
writes words; it doesn't design pages (for a built page, hand the approved
copy to the `landing-page` skill if installed, or to an HTML artifact).

## Scope

| Job | Output |
|---|---|
| Titles and headlines | Medium title + subtitle, carousel cover line, newsletter-style headline; 3-5 options each |
| CTAs | Article closer dare, LinkedIn first comment, X last-tweet line, "link in bio" line, Buy Me a Coffee ask |
| Profile copy | X bio (160 chars), LinkedIn headline (220 chars) + About, Instagram bio (150 chars), Medium bio (160 chars) and short "about" |
| Page copy | Portfolio home, consulting/services page, SaaS landing page, about page |

Out of scope: the posts and articles themselves (use the writing modules),
email sequences, ads.

## Before writing

Read these instead of asking the owner again:

1. `context/company.md`: offer, clients, income streams.
2. `context/strategy.md`: positioning and current focus.
3. `context/pillars.md`: audience (primary, secondary, tertiary).
4. `context/preferences.md`: voice.

Then ask only what's missing, usually:

- The ONE action this copy should produce (follow, read, book a call, buy).
- Where the reader arrives from (a post, search, a referral).
- Proof available: numbers, client outcomes, article stats. **Never invent
  proof.** No fake testimonials, no rounded-up metrics.

## Principles

- **Clear over clever.** If you must choose, choose clear.
- **Specific over vague.** "Cut a nightly Spark job from 3 h 40 min to 22 min"
  beats "optimize your pipelines".
- **Reader's words over company words.** Use the phrases the audience in
  `context/company.md` actually says (tech example: "my DAG failed at 3 AM",
  not "pipeline reliability challenges").
- **Benefit, then the mechanism.** What it gets them, then how.
- **One idea per section, one CTA per page.**
- Voice rules still apply: the avoid-list in `context/preferences.md`, plus no
  "leverage / unlock / seamless / game-changer".

## Profile copy (the four bios)

All four say the same positioning in different sizes. Positioning source:
the Positioning section of `context/pillars.md`.

Formula: **what you do, specifically → for whom → one proof → what they get
from following.**

| Channel | Limit | Notes |
|---|---|---|
| X bio | 160 chars | Densest version. One proof point. Link field → Medium or portfolio. |
| LinkedIn headline | 220 chars | Searchable terms first (role, niche, main tools). |
| LinkedIn About | 2,600 chars | First 3 lines show before "see more": who, for whom, proof. Then what they post, then how to work with them. |
| Instagram bio | 150 chars | Shortest. Say what the link in bio is. |
| Medium bio | 160 chars | What readers get from following: labs, production patterns. |

Deliver all four together so they stay consistent. Show char counts.

## Titles and headlines

- Medium: under ~60 chars for the title; subtitle carries the second keyword
  and the promise. Coordinate with `writing/seo` when the piece targets search.
- Give 3-5 options, each labeled with its formula from
  `references/copy-frameworks.md`, and mark one as the pick with a one-line
  reason.
- Lab articles: the title names the thing the reader will break or measure.

## CTAs

Formula: **action verb + what they get + qualifier if needed.**

- Article closer: if `context/preferences.md` lists a fixed closer, keep it
  verbatim; only its variable part changes.
- LinkedIn first comment / X last tweet: say what is behind the link ("Full
  guide with the templates: <link>").
- Link in bio: say what is behind the link.
- Service page: a specific offer ("Book a 30-minute review of your funnel") beats "Contact me".
- Weak (avoid): Submit, Sign up, Learn more, Click here, Get started.

## Page copy

Use the section types and templates in `references/copy-frameworks.md`. For
The owner's pages the usual order is:

1. Hero: outcome headline, one-line subhead, one CTA.
2. Proof bar: clients served, years, article count, a real metric.
3. Problem: the reader's situation in their words.
4. What they do: 3 services or 3 benefits, each with a proof.
5. How it works: 3 steps.
6. Selected work or articles.
7. FAQ: real objections (cost, timezone, stack fit).
8. Final CTA.

## Output format

- Copy organized by section (or by bio/title).
- Annotation per key element: which principle or formula, and why.
- 2-3 alternatives for headlines and CTAs, each with a rationale.
- For pages: SEO title and meta description (hand to `writing/seo` for
  keyword checks when ranking matters).
- Run the humanizer `quick` pass on the final copy.

## Resources

- `references/copy-frameworks.md`: headline formulas, page section types,
  page templates.
- `references/natural-transitions.md`: transitions that read human, and the
  ones that read like AI.
- `references/persuasion-playbook.md`: awareness levels, attention drivers,
  curiosity loop, CTA endings, and the off-brand list. Read before bios,
  page copy, and offers.

## Related modules

- `seo`: titles and meta that need to rank.
- `ig-carousel`: cover lines.
- `medium-tech-article`: the closer dare.
