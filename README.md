# Master Claude

> A curated knowledge base of tools, skills, and frameworks for the Claude Code ecosystem.

---

## Table of Contents

- [Overview](#overview)
- [Repositories](#repositories)
  - [Caveman](#-caveman)
  - [Squeez](#-squeez)
  - [AgentSpec](#-agentspec)
  - [Claude-Mem](#-claude-mem)
  - [Bedrock](#-bedrock)
  - [Oh My ClaudeCode](#-oh-my-claudecode)
  - [OpenSquad](#-opensquad)

---

## Overview

Master Claude is a living reference document that consolidates the repositories, tools, and plugins I use for Claude Code development. Each entry covers what the tool does, how to install it, and key usage notes — everything needed to get up and running fast.

---

## Repositories

### 🪨 Caveman

| | |
|---|---|
| **Repository** | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) |
| **Category** | Token Optimization · Claude Code Skill |
| **License** | MIT |

#### What it does

A Claude Code skill that forces Claude to respond in caveman-speak — stripping filler words, pleasantries, and hedging while preserving full technical accuracy. The result is roughly **75% fewer output tokens**, which translates directly to lower cost and faster responses.

**What gets removed:** articles (a, an, the), pleasantries ("Sure, I'd be happy to..."), hedging ("It might be worth considering...").

**What stays intact:** code blocks, technical terms, error messages, git commits, and PR descriptions are all written normally.

#### Install

```bash
claude install-skill JuliusBrussee/caveman
```

#### Usage

Activate it in a session with any of these triggers:

- `/caveman`
- `"talk like caveman"`
- `"caveman mode"`
- `"less tokens please"`

Deactivate with `"stop caveman"` or `"normal mode"`.

---

### 🗜️ Squeez

| | |
|---|---|
| **Repository** | [claudioemmanuel/squeez](https://github.com/claudioemmanuel/squeez) |
| **Category** | Token Compression · Context Optimization · Claude Code Hooks |
| **License** | MIT |
| **Language** | Rust (90%) / Shell (10%) |

#### What it does

Squeez is a Rust-based tool that hooks into Claude Code to automatically compress bash output, track token usage, and inject session memory — all with zero configuration. It operates via three Claude Code hooks:

1. **Bash compression** (`PreToolUse`) — intercepts every bash command, removes noise from the output. Achieves up to 95% token reduction on commands like `ps aux`.
2. **Session memory** (`SessionStart`) — summarizes the previous session (files touched, errors resolved, test results, git events) and injects it as a banner when a new session starts.
3. **Token tracking** (`PostToolUse`) — tracks cumulative context usage across tool calls and emits a warning at 80% of the context budget.

#### Benchmarks

| Fixture | Before | After | Reduction |
|---|---|---|---|
| `ps aux` | 40,373 tk | 2,352 tk | **-95%** |
| `git log` (200 commits) | 2,667 tk | 819 tk | **-70%** |
| `docker logs` | 665 tk | 186 tk | **-73%** |
| `ls -la` | 1,782 tk | 886 tk | **-51%** |
| `git diff` | 502 tk | 317 tk | **-37%** |

All fixtures complete under 10ms latency.

#### Install

```bash
curl -fsSL https://raw.githubusercontent.com/claudioemmanuel/squeez/main/install.sh | sh
```

Restart Claude Code after installation.

#### Escape hatch

Bypass compression for a specific command:

```bash
--no-squeez git log --all --graph
```

#### Configuration (optional)

Create `~/.claude/squeez/config.ini`:

```ini
# Compression
max_lines = 200
dedup_min = 3
git_log_max_commits = 20
docker_logs_max_lines = 100
bypass = docker exec, psql, ssh

# Session memory
compact_threshold_tokens = 160000
memory_retention_days = 30
```

#### Local development

```bash
git clone https://github.com/claudioemmanuel/squeez.git
cd squeez
cargo test
cargo build --release
mkdir -p "$HOME/.claude/squeez/bin"
cp target/release/squeez "$HOME/.claude/squeez/bin/squeez"
bash install.sh
```

To uninstall: `bash uninstall.sh`

---

### 📋 AgentSpec

| | |
|---|---|
| **Repository** | [luanmorenommaciel/agentspec](https://github.com/luanmorenommaciel/agentspec) |
| **Category** | Spec-Driven Development · Workflow Framework · Claude Code Plugin |
| **License** | MIT |
| **Version** | 1.0.0 |

#### What it does

AgentSpec is a Spec-Driven Development (SDD) framework for Claude Code. It replaces ad-hoc prompting with a structured 5-phase workflow that produces traceable artifacts at every step — from brainstorming through shipping.

It includes **17 specialized agents** across four categories: workflow (6), code quality (6), communication (3), and exploration (2). It also ships a knowledge base framework for building domain-specific grounding.

#### The 5-Phase Workflow

```
/brainstorm  →  /define  →  /design  →  /build  →  /ship
   (Explore)    (Capture)   (Architect)  (Execute)  (Archive)
```

| Phase | Command | Artifact produced |
|---|---|---|
| Brainstorm | `/brainstorm` | `BRAINSTORM_*.md` |
| Define | `/define` | `DEFINE_*.md` |
| Design | `/design` | `DESIGN_*.md` |
| Build | `/build` | `BUILD_REPORT_*.md` |
| Ship | `/ship` | `SHIPPED_*.md` |

During `/build`, AgentSpec automatically matches the right agents to the task based on what the DESIGN doc mentions (e.g., references to Pydantic and pytest will route to the python-developer, test-generator, and code-reviewer agents).

#### Install

```bash
git clone https://github.com/luanmorenommaciel/agentspec.git
cd your-project
claude --plugin-dir /path/to/agentspec
```

#### Project structure it creates

```
your-project/
├── .claude/
│   └── sdd/
│       ├── features/     # Active feature documents
│       ├── reports/      # Build reports
│       └── archive/      # Shipped features & lessons learned
```

#### Quick example

```bash
claude> /brainstorm "Add user authentication to the app"
claude> /define
claude> /design
claude> /build
claude> /ship
```

---

### 🧠 Claude-Mem

| | |
|---|---|
| **Repository** | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) |
| **Category** | Persistent Memory · Context Compression · Claude Code Plugin |
| **License** | AGPL-3.0 |
| **Language** | TypeScript (83%) / JavaScript (11%) / Shell (3%) |
| **Version** | 6.5.0+ (230 releases) |

#### What it does

Claude-Mem is a persistent memory compression system for Claude Code. It automatically captures everything Claude does during coding sessions — tool usage, decisions, errors resolved — compresses it with AI (via the Claude Agent SDK), and injects relevant context back into future sessions. This gives Claude continuity across sessions without any manual intervention.

It works through 5 lifecycle hooks (SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd), a worker service on port 37777 with a web viewer UI, a SQLite database for storage, and a Chroma vector database for hybrid semantic + keyword search.

Key capabilities: persistent memory across sessions, progressive disclosure (layered retrieval with token cost visibility), MCP-based search tools with a 3-layer workflow (search → timeline → get_observations) for ~10x token savings, privacy control via `<private>` tags, web viewer UI at `http://localhost:37777`, and multi-language mode support.

#### Install

```bash
npx claude-mem install
```

Or via plugin marketplace:

```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

Restart Claude Code after installation.

#### Requirements

Node.js 18+, Bun (auto-installed), uv (auto-installed), SQLite 3 (bundled).

#### Configuration

Settings managed in `~/.claude-mem/settings.json` (auto-created on first run). Supports mode/language configuration via `CLAUDE_MEM_MODE` (e.g., `"code--zh"` for Simplified Chinese).

#### MCP search tools

Four MCP tools follow a token-efficient workflow: `search` (compact index, ~50-100 tokens/result) → `timeline` (chronological context) → `get_observations` (full details, ~500-1000 tokens/result). Always filter before fetching.

---

### 🪨 Bedrock

| | |
|---|---|
| **Repository** | [iurykrieger/claude-bedrock](https://github.com/iurykrieger/claude-bedrock) |
| **Category** | Second Brain · Obsidian Automation · Claude Code Plugin |
| **License** | MIT |
| **Language** | HTML (41%) / TypeScript (40%) / JavaScript (16%) |
| **Version** | 1.1.2 |

#### What it does

Bedrock is a Claude Code plugin that turns any Obsidian vault into a structured Second Brain using AI agents. It organizes knowledge into 7 entity types (actors, people, teams, topics, discussions, projects, fleeting notes) following adapted Zettelkasten principles — with automatic entity detection, bidirectional wikilinks, external source ingestion, deduplication, and sync.

No build system or runtime needed — just markdown files, AI agents, and your vault.

#### Skills

| Skill | Purpose |
|---|---|
| `/bedrock:setup` | Interactive vault initialization and configuration |
| `/bedrock:ask` | Orchestrated vault reader — decomposes questions, searches graph and entities |
| `/bedrock:teach` | Ingest external sources (Confluence, Google Docs, GitHub, CSV) and create entities |
| `/bedrock:preserve` | Single write point — detect, match, create/update entities with bidirectional links |
| `/bedrock:compress` | Deduplication and vault health — broken links, orphans, stale content |
| `/bedrock:sync` | Re-sync entities with external sources |

#### Install

```
/plugin marketplace add iurykrieger/claude-bedrock
/plugin install iurykrieger/claude-bedrock
```

Then run the setup wizard:

```
/bedrock:setup
```

The setup guides through language selection, dependency checks, vault objective preset (engineering team, product management, company wiki, personal second brain, etc.), and scaffolding of directories, templates, config, and example entities.

#### Vault structure

```
your-vault/
├── actors/          # Systems, services, APIs (permanent notes)
├── people/          # Contributors, team members (permanent notes)
├── teams/           # Squads, organizational units (permanent notes)
├── topics/          # Cross-cutting subjects with lifecycle (bridge notes)
├── discussions/     # Meeting notes, conversations (bridge notes)
├── projects/        # Initiatives with scope and deadline (index notes)
└── fleeting/        # Raw ideas, unstructured captures (fleeting notes)
```

#### Optional dependencies

graphify (semantic code extraction for GitHub repos), confluence-to-markdown, gdoc-to-markdown — none are required.

---

### ⚡ Oh My ClaudeCode

| | |
|---|---|
| **Repository** | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) |
| **Category** | Multi-Agent Orchestration · Parallel Execution · Claude Code Plugin |
| **License** | MIT |
| **Language** | TypeScript (69%) / JavaScript (26%) / Python (3%) |
| **Stars** | 3.6k |

#### What it does

Oh My ClaudeCode (OMC) is a multi-agent orchestration framework for Claude Code with 5 execution modes, 31+ skills, and 32 specialized agents. It provides automatic parallelization, persistent execution (won't stop until verified complete), smart model routing (Haiku for simple tasks, Opus for complex reasoning), and cost optimization that saves 30–50% on tokens.

#### Execution modes

| Mode | Description |
|---|---|
| **Autopilot** | Full autonomous workflows |
| **Ultrapilot** | 3–5x faster via parallel multi-component execution |
| **Ecomode** | Token-efficient, 30–50% cheaper |
| **Swarm** | Coordinated parallel independent tasks |
| **Pipeline** | Sequential multi-stage processing |

#### Install

```
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
/plugin install oh-my-claudecode
```

Then run setup:

```
/oh-my-claudecode:omc-setup
```

#### Magic keywords

| Keyword | Effect |
|---|---|
| `autopilot` | Full autonomous execution |
| `ralph` | Persistence mode (includes ultrawork parallel execution) |
| `ulw` | Maximum parallelism |
| `eco` | Token-efficient execution |
| `plan` | Planning interview |

Usage is natural language — keywords are optional shortcuts: `autopilot: build a REST API for managing tasks`.

#### Rate limit wait

```bash
omc wait --start   # Enable auto-resume daemon (requires tmux)
omc wait --stop    # Disable
```

#### Requirements

Claude Code CLI, Claude Max/Pro subscription or Anthropic API key.

---

### 👥 OpenSquad

| | |
|---|---|
| **Repository** | [renatoasse/opensquad](https://github.com/renatoasse/opensquad) |
| **Category** | Multi-Agent Orchestration · Squad Framework · IDE-Agnostic |
| **License** | MIT |
| **Language** | TypeScript (35%) / JavaScript (25%) / HTML (24%) / Python (15%) |

#### What it does

OpenSquad is a multi-agent orchestration framework that lets you create squads of AI agents that collaborate on tasks — directly from your IDE. You describe what you need in natural language, and OpenSquad creates a team of specialized agents (researcher, strategist, writer, reviewer, designer, etc.) that execute in a pipeline, pausing only at decision checkpoints where your input is needed.

It supports multiple IDEs: Claude Code, Codex (OpenAI), Cursor, VS Code + Copilot, Open Code, and Antigravity.

It also includes a **Virtual Office** — a 2D visual dashboard that shows your agents working in real time.

#### Install

**Prerequisite:** Node.js 20+

```bash
npx opensquad init
```

To update: `npx opensquad update`

#### Usage

```
/opensquad                  # Open the main menu
/opensquad create           # Create a new squad
/opensquad run <name>       # Run a squad
/opensquad list             # List your squads
/opensquad edit <name>      # Modify a squad
/opensquad skills           # Browse installed skills
/opensquad install <name>   # Install a skill from catalog
/opensquad dashboard        # Generate the Virtual Office dashboard
```

#### Virtual Office

After generating the dashboard, serve it locally and open `http://localhost:3000`:

```bash
/opensquad dashboard
npx serve squads/<squad-name>/dashboard
```

#### Example squad creation

```
/opensquad create "Squad that generates Instagram carousels from trending news, creates the images, and publishes automatically"
```

The **Architect** agent asks a few questions, designs the squad, and sets everything up. You approve the design before execution begins.

---

*Last updated: April 22, 2026*