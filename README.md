<div align="center">
  <img src="docs/master-claude.png" alt="logo" width="300">
</div>

# master-claude

> A laboratory for Claude Code configurations. Everything here is markdown — skills, agents, commands, knowledge base. No application code, no build, no tests.

---

## Layout

```
master-claude/
├── company/               ← CompanyOS: business operating system + workspace template
│   ├── .claude/skills/    ← THE skill tree (18 hubs, 112 skills) — single source of truth
│   ├── CLAUDE.md          ← CompanyOS operating rules
│   ├── memory/  brain/  output/  scripts/
│   └── SETUP.md           ← non-technical setup guide
├── engineer/              ← master-claude / AgentSpec: software-engineering config
│   └── .claude/           ← agents, commands, kb, sdd, skills
├── docs/                  ← repo assets
├── CLAUDE.md              ← lab operating rules (loaded when working on the lab itself)
└── .mcp.json              ← Playwright MCP
```

Each domain folder is **self-contained**: it carries its own `.claude/` config, and you get its skills by opening Claude Code *inside* that folder. The repo root has no active skills — root sessions are for maintaining the lab itself.

---

## Install as Plugins

The repo doubles as a **Claude Code plugin marketplace** ([.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)). Each domain config installs independently, into any project, with updates pulled from this repo:

```
/plugin marketplace add lorenzouriel/master-claude

/plugin install company-os@master-claude    # 18 hub skills, 112 sub-skills
/plugin install engineer@master-claude      # domain agents + SDD commands + KB
```

Update later with `/plugin marketplace update master-claude`. Plugin components are namespaced (e.g. `/engineer:review`).

Note: the **company-os plugin ships the skills only**. For a full business workspace (CLAUDE.md operating rules, `memory/`, `brain/`, `output/`), copy the `company/` folder instead — see [Spinning Up a Business Workspace](#spinning-up-a-business-workspace).

Instantiated business workspaces (`uriel/`, `monkey/`, ...) are copies of `company/` and are gitignored wherever they live.

---

## The Domain Configs

### `company/` — CompanyOS
A skill-driven business operating system, doubling as the template for new business workspaces.
18 hub skills, each a router — the hub's `SKILL.md` dispatches to sub-skill folders:

| Hub | Sub-skills |
|-----|-----------|
| `business` | ads-report, approve-post, cold-email, google-ad, professional-email, ... |
| `content` | archive-content, buffer, content-planner, copywriting, humanizer, seo |
| `ebook` | inventory, outline, write, assemble |
| `formats` | docx, pdf, pptx, xlsx |
| `fundraising`, `growth`, `market`, `metrics`, `strategy` | business strategy and ops (incl. brand-identity + brand-book) |
| `instagram`, `linkedin`, `newsletters`, `tiktok`, `x`, `youtube` | per-platform content creation |
| `research` | scraping, deep research, second-brain ingestion |
| `system` | install, open, save, update, file-organizer, new-project, ... |
| `visual` | diagrams, landing pages, motion, visual explainers |

Invoke as `/hub sub-skill` (`/content plan`, `/business google-ad`, `/system install`) or plain language — hubs route automatically.

`company/.claude/skills/` is the **only** copy of the skill set in the repo. Skills created inside instantiated workspaces should be synced back here to become part of the template.

### `engineer/` — master-claude / AgentSpec
The software-engineering config. Open Claude Code inside `engineer/` (or copy `engineer/.claude/` into an engineering project) to use it.

- **`agents/`** — sub-agents grouped by domain: architect, cloud (AWS/GCP), data-engineering (Spark, dbt, Airflow, Lakeflow), dev, platform (Microsoft Fabric), python, test, workflow
- **`commands/`** — the AgentSpec 5-phase SDD workflow (`/workflow:brainstorm` → `define` → `design` → `build` → `ship`, plus `iterate` and `create-pr`), `/review`, `/data-engineering:*`, `/visual-explainer:*`, `/core:*`, `/knowledge:*`
- **`kb/`** — knowledge base: spark, dbt, airflow, lakehouse, medallion, fabric, terraform, streaming, sql-patterns, prompt-engineering, ...
- **`sdd/`** — workflow artifacts (features, reports, archive of shipped features)
