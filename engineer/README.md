# engineer/

master-claude / AgentSpec — the software-engineering config for Claude Code. Self-contained: open Claude Code inside this folder (or copy `engineer/.claude/` into another repo) to get its agents, commands, KB, and skills.

## What's here

| Path | Contents |
|------|----------|
| `.claude/agents/` | 68 domain sub-agents across architect, cloud (AWS/GCP), data-engineering (incl. SQL Server), dev, platform (Microsoft Fabric), python, javascript, dotnet, test, workflow |
| `.claude/commands/` | 35 slash commands: 5-phase SDD workflow, data-engineering, code review, visual-explainer, core utilities |
| `.claude/kb/` | 27 registered knowledge-base domains (dbt, spark, airflow, lakehouse, medallion, microsoft-fabric, terraform, streaming, sql-patterns, prompt-engineering, javascript, dotnet, ...) |
| `.claude/sdd/` | SDD workflow artifacts — `features/` (active), `reports/` (build outputs), `archive/` (shipped), `templates/`, `architecture/` |
| `.claude/skills/` | 29 skills: SDD phase methodology, agent-router, create-agent/create-skill, kb-build, kb-coverage-audit, appsec-review, cloud-finops, diagramming, github issue/ADR flow, project-docs, meeting-analysis, standup-report, sycophancy, ... |

## Quick start — SDD workflow

```
/workflow:brainstorm "idea"     # Phase 0 — explore, optional
/workflow:define <brainstorm>   # Phase 1 — capture requirements, Clarity Score >= 12/15
/workflow:design <define>       # Phase 2 — architecture + agent matching
/workflow:build <design>        # Phase 3 — delegated implementation
/workflow:ship <define>         # Phase 4 — archive + lessons learned
/workflow:iterate <doc> "change"   # mid-stream update to any phase doc
```

Design matches files to agents automatically via `Glob(.claude/agents/**)` — new agents dropped into `.claude/agents/` are picked up with zero config.

## Other command groups

| Group | Examples |
|-------|----------|
| `/data-engineering:*` | `/pipeline`, `/schema`, `/data-quality`, `/lakehouse`, `/sql-review`, `/ai-pipeline`, `/data-contract`, `/migrate` |
| `/knowledge:*` | `/create-kb` — scaffold a new KB domain |
| `/review` | dual-AI code review; `/judge` for cross-model second opinion |
| `/visual-explainer:*` | HTML diagrams, slide decks, diff/plan review, project recaps |
| `/core:*` | `/status`, `/meeting`, `/memory`, `/sync-context`, `/readme-maker` |
| `/project:docs` | scaffold PMBOK-lite project documentation |

Full command reference: [.claude/commands/README.md](.claude/commands/README.md).

## Deeper docs

- [.claude/sdd/README.md](.claude/sdd/README.md) — AgentSpec architecture, phase details, agent-matching internals, extension guide
- [.claude/sdd/architecture/](.claude/sdd/architecture/) — workflow contracts, ADRs
- Repo-wide layout and plugin install: [../README.md](../README.md)

## Adding to this config

- New agent → `.claude/agents/{category}/{name}.md`, standard frontmatter (role, model, capabilities); auto-discovered by Design.
- New KB domain → `/create-kb "name"` or manually under `.claude/kb/{domain}/`, then register in `.claude/kb/_index.yaml`.
- New skill or command → see `create-skill` skill and [.claude/commands/README.md](.claude/commands/README.md) for conventions.
