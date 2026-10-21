---
name: tiktok
description: >
  The TikTok creator skill. Covers video scripting, hook writing, content strategy,
  algorithm optimization, trending sounds, posting cadence, and viral content patterns.
  Routes to specialized sub-skills for each task. Triggers on: "tiktok", "tiktok script",
  "tiktok strategy", "tiktok hook", "tiktok content plan", "tiktok growth", "viral on tiktok",
  "for you page", "FYP", "tiktok algorithm", "write a tiktok script", "short video script",
  "completion rate", "trending sounds", "tiktok marketing".
tools:
  - Read
  - Write
  - Bash
  - WebSearch
  - Edit
  - Grep
  - Glob
  - Agent
---

# Claude TikTok — TikTok Creator Skill

> Orchestrator for TikTok content creation, strategy, and growth. Routes to the
> right sub-skill based on your request. Sub-skills and reference files do the
> work — this file routes, delegates, and quality-checks.

## Command Router

| Command | Sub-Skill | Trigger Phrases |
|---------|-----------|----------------|
| `/tiktok script` | `tiktok-script-writer/SKILL.md` | "TikTok script", "write a TikTok about X", "hook for TikTok", "15-second script", "60-second TikTok", "video script for TikTok" |
| `/tiktok strategy` | `tiktok-content-strategy/SKILL.md` | "TikTok strategy", "grow on TikTok", "TikTok algorithm", "why isn't my TikTok growing", "TikTok content plan", "viral content ideas", "TikTok for app marketing" |

> **Planned sub-skills** (route to script or strategy for now):
> - `tiktok-hook-writer` — write just the first 3 seconds before committing to a full script
> - `tiktok-humanizer` — scrub scripted-sounding patterns from any TikTok script
> - `tiktok-content-planner` — build the weekly content calendar from a strategy

If a request spans multiple sub-skills (e.g., "plan my TikTok strategy and write the first 3 scripts"),
run strategy first, then script-writer for each video.

## In this workspace (Content Creation OS)

Niche, audience, and goal come from `context/company.md`, `context/pillars.md`,
and `context/strategy.md`: don't ask for them, only confirm follower tier if unknown.
Voice and banned patterns: `context/preferences.md` (no emojis, no em dashes,
no guru vocabulary). Every script or caption passes `humanizer` before it is
used. Visuals follow `brand/design-guide.md`. Save drafts to `output/reels/`
and log them in `content-pipeline`. Publishing goes through `metricool` only.

## Context-Gathering Protocol

Before invoking ANY sub-skill, collect these inputs. If any are missing, ask:

1. **Account/brand niche** — What is the account about? Be specific (not "health" — "managing phone anxiety in young adults").
2. **Account size tier:**
   - New: < 1K followers
   - Growing: 1K–10K followers
   - Established: 10K–100K followers
   - Authority: 100K+ followers
3. **Primary goal:** User Acquisition / Brand Awareness / Community / Creator Growth

## TikTok vs Instagram Reels — Key Differences

Both platforms use short video, but algorithm mechanics differ significantly.

| Dimension | TikTok | Instagram Reels |
|-----------|--------|-----------------|
| #1 signal | Completion rate | Shares to Stories |
| Hook style | Aggressive, immediate | Slightly warmer acceptable |
| Tone | Raw, unpolished | More "aesthetic" OK |
| Reach model | Content-based (new accounts can go viral) | Account-based (followers see first) |
| Pacing | Faster | Slightly slower |

## TikTok Algorithm (2026)

| Signal | Priority | Notes |
|--------|----------|-------|
| Completion rate | #1 | Watch all the way through — everything else is secondary |
| Shares | #2 | Highest-intent engagement signal |
| Comments | #3 | Especially within first 2 hours |
| Rewatches | #4 | Dense, replayable content |
| Likes | #5 | Weakest signal |

Trending sounds → ~20–40% initial reach boost but do NOT improve retention.

## Reference Files

Load on-demand when a sub-skill requires them.

| File | Content |
|------|---------|
| `tiktok-script-writer/references/script-formats.md` | 5 full script formats with worked examples (tutorial, story, listicle, opinion, BTS) |
| `tiktok-script-writer/references/algorithm-heuristics.md` | TikTok 2026 algorithm rules, completion benchmarks, posting windows |

## Hook Rule (First 3 Seconds)

The first 3 seconds determine everything on TikTok. This is not optional.

**Hard rules:**
- Start mid-action, mid-sentence, or at maximum tension — never with a greeting
- On-screen text must work muted (many users never turn on sound)
- Spoken hook must work without looking at screen
- Never: "Hey guys", "So today I'm going to show you", "Wait for it...", intro animations

**Hook patterns:**
- Problem/pain point: "Phone anxiety is ruining your life..."
- Shocking stat: "97% of people don't know this..."
- Pattern interrupt: "Stop using [common thing]..."
- Quick win: "Here's how to [outcome] in 60 seconds"
- Relatable moment: "POV: You're trying to [relatable struggle]"

## Quality Gates

Every sub-skill output MUST pass before delivery:

1. **Specificity** — Every recommendation must be actionable for THIS account's niche and tier.
2. **Platform accuracy** — No advice contradicting 2026 TikTok algorithm rules. Never hallucinate benchmarks.
3. **Script authenticity** — No scripted-sounding prose. Read aloud test: if it sounds written, it fails. No uniform sentence lengths, no filler phrases.

## Self-Anneal Loop

If a sub-skill output fails a quality gate:
1. Identify which gate failed and why
2. Re-read the relevant reference file
3. Re-generate only the failing sections
4. If still failing after 2 attempts, deliver with explicit caveats

## Output Format

Default to markdown. For scripts: timing column + on-screen text column + spoken lines — ready to record. For strategy: structured report with content pillars and weekly mix. Always end with "Next Steps" pointing to the logical next sub-skill.
