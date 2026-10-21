---
name: system
description: CreatorOS setup and maintenance hub. Routes to the install interview (builds the whole content base from scratch - company, voice, strategy, pillars, brand kit, Metricool, tools, past content), the health check, and targeted updates. Trigger on "install", "set up CreatorOS", "start", "onboarding", "/system install", "doctor", "check my setup", "is everything configured", "update my brand", "change my pillars", "new logo", "update voice", "connect Metricool".
---

# System

Router for CreatorOS setup and upkeep. Pick the sub-skill, read its `SKILL.md`,
and follow it. Paths are relative to the project root.

## Command Router

| Command | Sub-Skill | Use for |
|---|---|---|
| `/system install` | `install/SKILL.md` | First run. Interview in modules (company, voice, strategy and pillars, brand kit, tools and Metricool, past content) that fills `context/`, `brand/`, and checks every tool. Resumable. |
| `/system doctor` | `doctor/SKILL.md` | Read-only health check: unfilled templates, missing brand files, tools, Metricool connection, video engine. |
| `/system update <module>` | `update/SKILL.md` | Re-run one install module (company, voice, strategy, brand, tools, import) without touching the rest. |

A file still starting with `<!-- creatoros:template -->` has not been filled.
Writing skills that need a template file stop and point to `/system install`.
