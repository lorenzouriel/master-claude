# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A curated directory of third-party Claude Code plugins, grouped into five "teams" by what
they do for you. There is **no application code** — the repo is a root `README.md`, five
team `README.md` files, and `image.png` (the wizard logo, shown at the top of the root
README). There is nothing to build, lint, run or test; `git` is the only tooling. Do not
invent build or test commands, and do not add `package.json`, CI, or scaffolding unless
asked.

Remote: `git@github.com:lorenzouriel/master-claude.git` (branch `main`).

## Layout

```
README.md                    index: team table, five picks, caveats
01-build-team/README.md      plan-then-ship plugins     (7)
02-design-team/README.md     UI, taste, diagrams        (7)
03-research-team/README.md   web/file/app research      (6)
04-content-team/README.md    decks, docs, video, copy   (6)
05-office-team/README.md     tunes Claude itself        (6)
```

The numeric prefixes set reading order. The root README duplicates figures that live in the
team files — the total (32), each team's count, the "most stars" column, and the five
starting picks. Any edit to a team file has to be carried back to it. Its deep links are
written as `0N-x-team/README.md#anchor`, not `0N-x-team/#anchor`, so the heading anchor
still resolves on GitHub.

## The README Contract

Every team file follows the same shape, and new entries must match it exactly:

1. `# Team N — The <name> team`, then a bold one-line promise, then a `>` blockquote tagline,
   then a short paragraph naming the plugin count and the theme.
2. A summary table: `| Plugin | Role | What it does | Stars |`. The Plugin cell is an anchor
   link to the section below (`[Superpowers](#superpowers)`). Role is Title Case
   ("Senior dev", "Art director"). "What it does" is one plain-English clause — the
   non-technical register is deliberate.
3. `---`, then one `## <Plugin>` section per row, **in the same order as the table**.
4. Each section: a backticked uppercase role and star count on one line
   (`` `PLANNER` · 318k ``), one or two sentences of editorial judgment (when to pick it,
   what it beats, what it is a reaction to — not a feature list), then
   `- **Repo:** [owner/name](https://github.com/owner/name)`.

Conventions that are easy to break:

- **Sort by stars, descending**, in both the table and the sections.
- Stars are rounded strings (`462k`, `5.2k`), copied from the source — don't recompute them.
- A plugin not in the original five-team roundup carries an extra bullet saying so
  (see Security Audit, Excalidraw Diagram), and that bullet is where caveats go: missing
  licence, stale last-push date.
- Cross-references between plugins use in-file anchors (`[Diagram Design](#diagram-design)`).
- Prose is British-leaning ("summarises", "licence"), hard-wrapped around 90 columns, and
  em-dashes are used freely. Keep voice opinionated: each entry says who should use it.

When adding a plugin, update the table row and the section together, re-sort by stars, and
update the count in the intro paragraph and the table header blurb.

## History

`d7f4611` deleted an earlier incarnation — a plugin marketplace of ~2100 files
(`company/` CompanyOS skills, `engineer/` AgentSpec, `content-creation/` CreatorOS,
`.claude-plugin/marketplace.json`, `.mcp.json`). That removal was deliberate: this repo is
now a directory, not a marketplace. Don't restore those trees or treat them as the current
design; they're reachable in git history if a past skill needs to be consulted.
