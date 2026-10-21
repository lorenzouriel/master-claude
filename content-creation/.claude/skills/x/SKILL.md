---
name: x
description: >
  X (Twitter) writing hub for the owner. Routes to single posts, full threads, and replies
  or quote posts on other people's tweets. Trigger on: "tweet this", "X post", "hook for
  X", "short take", "thread", "turn this into a thread", "X thread about the article", a
  pasted x.com / twitter.com link with "reply", "respond", "quote", "my X replies for
  today".
---

# X (Twitter)

Router for the `x` sub-skills. Pick the sub-skill, read its `SKILL.md`, and follow it. Paths inside sub-skills are relative to the project root (`context/...`, `data/...`), except each sub-skill's own `references/` and `scripts/`.

## Command Router

| Command | Sub-Skill | Use for |
|---|---|---|
| `/x post` | `x-post/SKILL.md` | Single tweet or thread opener with one of ten hook formulas, humanize, hand off to Metricool. |
| `/x thread` | `x-thread/SKILL.md` | 3-10 tweet thread, usually the anchor article recap. Link only in the last tweet. |
| `/x reply` | `x-reply-drafter/SKILL.md` | 1-3 reply or quote variants on someone else's post from a URL or pasted text. |

If a request spans several sub-skills, run them in order and pass the output forward. Tie-breaks and chained workflows live in the project `CLAUDE.md`.
