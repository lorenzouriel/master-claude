---
name: tiktok-script-writer
description: Write a complete TikTok video script. Covers hook (first 3 seconds), body structure with on-screen text cues, spoken lines, pacing, and CTA. Optimized for TikTok's completion-rate algorithm. Separate from IG Reels because TikTok hooks, pacing, and tone differ. Use for videos 15-180 seconds.
---

# TikTok Script Writer

Write TikTok scripts that drive completion rate — the #1 signal in TikTok's algorithm. If people watch to the end, TikTok pushes the video. If they leave early, it dies.

## When to use

- User says "write me a TikTok script about X"
- User has a topic and needs hook + structure + spoken lines
- User wants timing, on-screen text cues, and spoken word mapped together

## TikTok vs Instagram Reels — key differences

| Dimension | TikTok | Instagram Reels |
|---|---|---|
| Primary signal | Completion rate | Shares to Stories |
| Hook style | More aggressive, faster cut | Can be slightly warmer |
| Tone | Raw, direct, less polished | More "aesthetic" acceptable |
| Audio | Trending sounds matter more | Original audio fine |
| Pacing | Faster (assume short attention) | Slightly slower |
| For You Page | Content-based (new accounts can go viral) | Account-based (followers see first) |

## Script lengths

| Length | Best for |
|---|---|
| 7-15 sec | Quick tips, reactions, "did you know", memes |
| 15-30 sec | Contrarian takes, short tutorials, reveals |
| 30-60 sec | Educational, step-by-step, opinion with evidence |
| 60-180 sec | Story, deep dive, multi-part breakdown |

Default: 30-60 sec unless user specifies.

## Script formats

| Format | Use when |
|---|---|
| Tutorial | Step-by-step, how-to, tools |
| Story | Personal journey, mistake → lesson |
| Listicle | Fast-paced N-item list |
| Opinion/Contrarian | Hot take with argument |
| Behind-the-scenes | Process reveal, day-in-the-life |

Full structures in `references/script-formats.md`.

## Steps

1. **Gather inputs.** Topic, target length, format preference (or skill picks), audience, tone (educational / raw / entertaining).
2. **Pick format.** Tutorial if it's a process. Story if it's personal. Listicle if it's enumerable. Opinion if it's a take.
3. **Write hook (0:00-0:03).** The entire game. Rules:
   - Start mid-action, mid-sentence, or at maximum tension — never with an intro
   - On-screen text must work muted
   - Spoken hook must work without looking at the screen
   - 8 hook formulas in `tiktok-hook-writer/references/hook-formulas.md`
4. **Write body.** One idea per 5-8 seconds. Faster than Instagram. More specific = higher completion.
5. **Write CTA.** One action. Best TikTok CTAs:
   - "Comment [X] if you want part 2"
   - "Follow for [specific content promise]"
   - "Save this for when you need it"
   - Or no CTA — end on the strongest line
6. **Humanizer pass.** Read aloud. If it sounds scripted, rewrite it. TikTok audiences are extremely sensitive to over-produced speech.
7. **Output.** Timing column + on-screen text + spoken lines. Ready to record.

## Hard rules

- Never start with: "Hey guys", "So today", "Welcome back", "In this video I'm going to show you"
- No "Don't forget to like and subscribe" — this is TikTok, not 2015 YouTube
- No "So basically" as filler
- No sentences all the same length — spoken word needs rhythm
- The visual must start doing something in the first second, not just the creator talking to camera

## Algorithm rules (2026 summary)

See `references/algorithm-heuristics.md`. Summary:
- **Completion rate** is the #1 signal. Everything else is secondary.
- **First 3 seconds** determine whether someone stays — they're the most expensive part
- **Shares** are the second-strongest signal
- **TikTok recommends based on content, not account** — new accounts can go viral immediately
- **Trending sounds** give a ~20-40% initial reach boost but don't help retention
- **Comments within 2 hours** matter for the push window — creator replies especially

## Anti-patterns

- Script that sounds like a blog post being read aloud (uniform long sentences)
- Hook that's a vague teaser ("Wait for it..." or "You won't believe this")
- Body that has more setup than payload
- CTA that's longer than the last 5 seconds of content
- Ending on a fade-out or music bed without a verbal close

## Resources

- `references/script-formats.md` — 5 full script formats with worked examples
- `references/algorithm-heuristics.md` — TikTok algorithm rules 2026
- `tiktok-hook-writer/references/hook-formulas.md` — 8 TikTok-specific hook formulas

## Related skills

- `tiktok-hook-writer` — write just the first 3 seconds before committing to a full script
- `tiktok-humanizer` — scrub scripted-sounding patterns from any TikTok script
- `tiktok-content-planner` — schedule this video in the weekly content mix
