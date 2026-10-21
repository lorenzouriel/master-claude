# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Response Style

Be terse. No filler words, no pleasantries, no hedging. Preserve full technical accuracy.
Strip: "Sure, I'd be happy to...", "It might be worth considering...", "As mentioned above...".
Keep: code blocks, error messages, technical terms, file paths, git output.

## What This Repo Is

master-claude is a laboratory for Claude Code configurations. There is no application code — everything is markdown (skills, agents, commands, knowledge base). There are no build, lint, or test commands.

The repo is organized as **self-contained domain folders**, each carrying its own `.claude/` config. You get a domain's skills by opening Claude Code inside that folder. The repo root has no active skills (`.claude/` at the root holds only local settings) — root sessions are for maintaining the lab itself.

1. **`company/`** — CompanyOS, a skill-driven business operating system. Also the template for new business workspaces.
2. **`engineer/`** — master-claude / AgentSpec, the software-engineering config (agents, SDD commands, data-engineering knowledge base).
3. **`content-creation/`** — Content Creation OS, Lorenzo's personal content system for Medium, LinkedIn, Instagram, and X.

## Architecture

### `company/` — CompanyOS

18 hub skills in `company/.claude/skills/`: `business`, `content`, `ebook`, `formats`, `fundraising`, `growth`, `instagram`, `linkedin`, `market`, `metrics`, `newsletters`, `research`, `strategy`, `system`, `tiktok`, `visual`, `x`, `youtube`.

Each hub is a router: the hub's `SKILL.md` dispatches to sub-skill folders (e.g. `content/` → `archive-content`, `buffer`, `content-planner`, `copywriting`, `humanizer`, `seo`). Invoke as `/hub sub-skill` (`/content plan`, `/business google-ad`, `/system install`) or via plain language — hubs route automatically.

**Single source of truth**: `company/.claude/skills/` is the only copy of the skill set in this repo (the old `.claude/skills/` ↔ `new-company/` duplication is gone). When a useful skill is created inside an instantiated workspace, sync it back here so the template gains it.

Structure of `company/`:
- `.claude/skills/` — the full skill set
- `CLAUDE.md` — CompanyOS operating rules (memory reading, learn-from-corrections flow, skill creation flow)
- `memory/` — `company.md`, `preferences.md`, `strategy.md`
- PARA-method second brain, as flat top-level folders: `inbox/`, `projects/`, `areas/` (also where recurring deliverables like marketing content land), `resources/` (reference + one-off documents; brand identity lives at `resources/identity/design-guide.md`), `archive/`
- `resources/scripts/` — starts empty; integration scripts (image generation, social publishing) are created on demand by skills and need a `.env` with API keys

To spin up a business workspace: copy `company/`, rename it to the business name, open Claude Code inside it, run `/system install` (interview that fills `memory/` and appends business rules to its `CLAUDE.md`). Instantiated company workspaces (e.g. `uriel/`, `monkey/`) are gitignored — add new workspace folders to `.gitignore` when creating them inside the repo.

### `engineer/` — master-claude / AgentSpec

- `.claude/agents/` — sub-agents grouped by domain (architect, cloud, data-engineering, dev, platform/Fabric, python, test, workflow)
- `.claude/commands/` — `/workflow:*` SDD phases (brainstorm → define → design → build → ship), `/review`, `/data-engineering:*`, `/visual-explainer:*`, `/core:*`, `/knowledge:*`
- `.claude/kb/` — data-engineering knowledge base (spark, dbt, airflow, lakehouse, fabric, terraform, …)
- `.claude/sdd/` — SDD workflow artifacts (features, reports, archive)

Its commands and agents are active only in sessions opened inside `engineer/` (or in a project that copies `engineer/.claude/`). Do not document or invoke them as if they were active at the repo root.

### `content-creation/` — Content Creation OS

- `.claude/skills/` — 22 skills, one per module (writing per platform, humanizer, seo, intel, pipeline, buffer, archive, analytics). They route themselves from their descriptions; `CLAUDE.md` keeps only tie-breaks and chained workflows.
- `.claude/agents/` — `researcher`, `editor`, `analyst`, `archivist`: isolated heavy work. Writing stays in the main thread.
- `context/` (memory, pillars, platform rules, storage) and `brand/` (design guide, assets, brand book), auto-loaded via `@imports` in its `CLAUDE.md`.
- `data/` and `output/` are local state, gitignored except `.gitkeep`; CSV schemas live in the owning skills.
- `web/` + `scripts/build-web.py` generate the claude.ai upload bundle into `dist/` (gitignored). `web/overrides/` holds the Drive-specific versions of 7 files; everything else comes from `.claude/skills/`.
