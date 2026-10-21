# Article structures

> Reconstructed because the original file was missing. Replace with the original
> if you have it. All three shapes sit inside the skeleton in `medium-tech-article.md`.

## 1. Lab article

Use when the reader can reproduce and break something.

1. Hook: the symptom the reader has seen in production.
2. Setup: the lab (reuse `billing` from `lab-universe.md`), one code block to get there.
3. Break it: the demo that makes the problem visible. Measure it.
4. Explain it: the mechanism, only as deep as needed to understand the fix.
5. Fix it: the technique. Measure again. Before/after table.
6. The price: what the fix costs (CPU, RAM, storage, complexity, licensing).
7. When NOT to use it.
8. Overview + closer with the dare.

## 2. Guide

Use when there is no single breakable demo: concepts, comparisons, setup walkthroughs.

1. Hook: the decision or confusion the reader faces.
2. The mental model in one paragraph, optionally one diagram.
3. Sections per option or step, each with a concrete example and its tradeoff.
4. Decision matrix table (option × criteria).
5. Overview + closer.

## 3. Playbook

Use for operational "when X happens, do Y" content (incident response, monitoring, DMV kits).

1. Hook: the 3 AM moment.
2. Use cases as question headers: `## Use Case 01: "Who is blocking who?"`
3. Each use case: tool line, the query/command, how to read the output, what to do next.
4. A "first five minutes" checklist.
5. Overview + closer.

## Picking a shape

| Source material | Shape |
|---|---|
| Course unit, docs page, command dump with a reproducible problem | Lab |
| Comparison, architecture choice, "which tool" | Guide |
| Troubleshooting notes, runbook, DMV/query collection | Playbook |
| AI engineering build (RAG, agent, eval) with runnable code | Lab |
