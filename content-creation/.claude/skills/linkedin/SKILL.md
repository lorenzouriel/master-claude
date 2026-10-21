---
name: linkedin
description: >
  LinkedIn writing hub for the owner. Routes to post drafting (2026 hook formulas,
  humanizer pass, Metricool handoff) and comment drafting on other people's posts. Trigger
  on: "write a LinkedIn post", "LinkedIn hook", "draft and schedule a LinkedIn post", a
  pasted LinkedIn post URL with "comment", "engage", "reply to the author", "be among
  the first commenters".
---

# LinkedIn

Router for the `linkedin` sub-skills. Pick the sub-skill, read its `SKILL.md`, and follow it. Paths inside sub-skills are relative to the project root (`context/...`, `data/...`), except each sub-skill's own `references/` and `scripts/`.

## Command Router

| Command | Sub-Skill | Use for |
|---|---|---|
| `/linkedin post` | `linkedin-post/SKILL.md` | Draft a new post from scratch with a hook formula, humanize, hand off to Metricool. |
| `/linkedin comment` | `linkedin-comment-drafter/SKILL.md` | 1-3 comment variants on someone else's post from its URL, plus reaction type. Not for replies to existing comments. |

If a request spans several sub-skills, run them in order and pass the output forward. Tie-breaks and chained workflows live in the project `CLAUDE.md`.
