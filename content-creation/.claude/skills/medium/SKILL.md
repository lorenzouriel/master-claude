---
name: medium
description: >
  Long-form hub for the owner: Medium technical articles, human-sounding newsletters and
  long posts, and the article thumbnail prompt. Trigger on: "draft a Medium article",
  "rewrite in my style", "turn these notes into an article", "make an article", "hands-on lab
  post", "newsletter", "long-form post", "make this more human" on long text,
  "escrever uma newsletter", "thumbnail", "cover", "header", "thumb prompt" for an
  article.
---

# Medium & Long-form

Router for the `medium` sub-skills. Pick the sub-skill, read its `SKILL.md`, and follow it. Paths inside sub-skills are relative to the project root (`context/...`, `data/...`), except each sub-skill's own `references/` and `scripts/`.

## Command Router

| Command | Sub-Skill | Use for |
|---|---|---|
| `/medium article` | `medium-tech-article/SKILL.md` | Write, rewrite, or edit a Medium article in the owner's voice. |
| `/medium newsletter` | `newsletter-humana/SKILL.md` | Human-sounding newsletters and long-form, plus short posts derived from them (PT or EN). |
| `/medium thumbnail` | `thumbnail-prompt/SKILL.md` | Image prompt for a Medium thumbnail or LinkedIn article cover in the locked thumbnail style from the design guide. |

If a request spans several sub-skills, run them in order and pass the output forward. Tie-breaks and chained workflows live in the project `CLAUDE.md`.
