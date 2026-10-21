---
name: linkedin-post
description: Draft a new LinkedIn post from scratch using a 2026 hook formula (anaphora, R.I.P., year-pivot, time-anchor, self-proving, paid-vs-free, curiosity-gap, odd-money, contrarian). Runs the humanizer pass and hands off to Metricool on approval. Use whenever the user asks to write a LinkedIn post, needs a hook, wants a proven post format, or wants to draft and schedule a post in one flow.
---

# LinkedIn Post Writer

Ship long-form LinkedIn posts using hook formulas that performed in 2025-2026.
Engagement numbers are relative reference points, not guarantees.

## When to use

- User says "write me a LinkedIn post about X"
- User has a topic + a rough angle and needs a hook + structure
- User wants to pick from known-winning formats and fill in their voice
- User wants to audit + schedule in one flow

## Formulas this skill can use

| Code | Formula | Reference eng | Best for |
|---|---|---|---|
| F1 | Platform Risk Anaphora | 4,240 | Category/platform posts, product-as-fix |
| F2 | R.I.P. Obituary | 3,822 | Era-ending claims, industry pivots |
| F3 | Year-over-Year Pivot | 494, 3.74x | Identity shifts, founder reflection |
| F4 | Time-Anchor Confession | 1,519+ | Vulnerability, voice reset, ICP re-targeting |
| F5 | Self-Proving Meta | 1,082 / 435 comments | Commitment-based posts, tests in public |
| F6 | Comment-Gate Lead Magnet | 717-3,008 | List building (use sparingly, capped reach) |
| F7 | Odd-Precision Money Ledger | 1,755, 9.4x | Founder build-log, cost breakdowns |
| F8 | Paid-vs-Free Reversal | 550, 19.64x | Free framework give-away |
| F9 | Curiosity-Gap Teaser | 306, 4.25x | Emergent behavior, behind-the-scenes |
| F10 | Contrarian + Historical Receipts | 3,083 | Sacred-cow takes, AI/tech cycles |

Full skeletons with worked examples in `references/hook-formulas.md`.

## Steps

1. **Gather inputs.** Topic, angle, draft ideas if the user has them, pillar (P1-P5 from `context/pillars.md`), desired length (short 300-500 / medium 900-1300 / long 1500-1900 chars). Default audience is the one in `pillars.md`. If the topic came from a dossier or news-radar item, carry its source link (it goes in the first comment, never the body).
2. **Pick the formula.** If the user didn't specify, suggest 2-3 formulas that fit the topic and let them pick. Show the reference engagement number next to each. See the picking-a-formula table in `references/hook-formulas.md`. If `data/metrics/posts.csv` has 10+ rows, also show the owner's own median engagement per formula (see content-analytics) and prefer their data over the reference numbers.
3. **Draft the post.** Fill the formula skeleton with user voice. Respect the 2026 algorithm rules:
   - Hook in first 210 chars (before "… see more")
   - 900-1,300 char sweet spot for text posts
   - Double line-breaks between ideas, not single
   - 0-2 hashtags, placed at end
   - No external links in body (move to first comment)
   Full rules in `references/algorithm-heuristics.md`.
4. **Humanizer pass.** Strip em dashes, AI vocab, rule-of-three, generic openers. Add at least 1 specific number, 1 named entity, 1 first-person concrete detail per 100 words. Full scrub list in `references/humanizer-checklist.md`, plus the LinkedIn block of `.claude/skills/content/humanizer/references/platform-scrub-rules.md`.
5. **Audit.** Re-read the draft against `.claude/skills/content/humanizer/SKILL.md` (the audit loop: "what still sounds like AI here?") and `references/algorithm-heuristics.md`. Fix, then continue.
6. **Approval card.** Show: formula used (F-code), pillar (P-code), full draft, char count, suggested posting window (the day's slot from the slot map in `context/pillars.md`, 7:30-9:00 AM local; Tue-Thu are the strongest days), first-comment text if there is a link.
7. **On approval.** Log it in the pipeline as `drafted` (see `.claude/skills/content/content-pipeline/SKILL.md`), storing formula and pillar. If the user wants it scheduled, hand the exact approved text to `.claude/skills/content/metricool/SKILL.md`. Never publish from this module.

## Hard rules (from user feedback)

Global voice rules: `context/preferences.md`. Additional skill-specific rules:

- Never frame LinkedIn as inferior in a LinkedIn post (algo penalty).
- Don't name-drop the user's product in a way that reads as self-promo. One mention max, and only when it's the natural conclusion, not the pitch.
- Include at least one moment of real vulnerability or concrete stakes. Pure insight posts don't land in 2026.
- Vary sentence length aggressively. Mix 3-word sentences and 25-word sentences.

## Anti-patterns (skill will refuse)

- All-caps first line ("THIS CHANGED EVERYTHING.")
- Em dashes anywhere
- "In today's fast-paced world" openers
- Rule-of-three lists without receipts
- "Game-changer", "deep dive", "leverage", "fundamentally"
- External links in the body
- Reused engagement-bait closers ("tag someone who needs this")

## Resources

- `references/hook-formulas.md` — all 10 formula skeletons with worked examples and a picking-a-formula table
- `references/algorithm-heuristics.md` — 2026 posting rules (timing, format, length, engagement protocol)
- `references/humanizer-checklist.md` — the full scrub list
- `.claude/skills/content/copywriting/references/persuasion-playbook.md` — awareness levels, attention patterns, PS-over-CTA endings (when picking an angle or ending)

- `.claude/skills/content/humanizer/SKILL.md` — full AI-tell guide, used in the audit step

## Related modules

- `metricool` — scheduling after approval
- `content-analytics` — which formulas actually work for the owner
- `repurpose` — when the post comes from an existing article
