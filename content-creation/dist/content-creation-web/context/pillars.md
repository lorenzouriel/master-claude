# Content pillars and topic radar

> Shared by every module. Writing modules use it to pick angles, news-radar uses
> it to score relevance, content-pipeline uses it to check balance. Edit here,
> never in a module.

## Positioning

Senior Data Engineer & AI Engineer teaching system design, production patterns,
real projects, and AI engineering for data people. Engineer-to-engineer.
Proof over opinion.

## Audience

- Primary: data engineers and analytics engineers (mid to senior) who want to
  move into AI engineering or senior/staff scope.
- Secondary: DBAs and SQL developers growing into data engineering (his own
  path, so "write for past self" works here).
- Tertiary: tech leads and hiring managers who buy data consulting.

## Pillars (target mix per week)

| Code | Pillar | Mix | Examples |
|---|---|---|---|
| P1 | Data engineering in production | 35% | pipeline design, orchestration, lakehouse, Fabric/Databricks/AWS patterns, cost, failures |
| P2 | AI engineering for data people | 30% | LLM apps on data, RAG, agents, evals, Claude/MCP tooling, AI in pipelines |
| P3 | System design & architecture | 15% | tradeoffs, decision records, scaling stories, design reviews |
| P4 | Databases & SQL depth | 10% | SQL Server internals, tuning, query plans (legacy strength, now supporting) |
| P5 | Career & building in public | 10% | consulting, solopreneur numbers, SaaS build log, Toronto, learning |

Every piece maps to exactly one primary pillar. Store the code (P1-P5) in the
pipeline and metrics files so analytics can compare pillars.

## Topic radar (for news-radar scoring)

High relevance (score boost):
- Microsoft Fabric, Databricks, Snowflake, AWS data services (Glue, Redshift, S3 Tables, Bedrock)
- Apache Iceberg, Delta Lake, Spark, dbt, Airflow, Dagster, DuckDB, Polars, Kafka
- Anthropic/Claude, OpenAI, MCP, agent frameworks, LLM evals, vector search
- SQL Server and Azure SQL releases
- Data engineering hiring market, AI engineer role evolution

Medium relevance:
- General cloud pricing changes, Postgres, Python tooling, observability
- Big-company engineering blog posts on data/AI architecture

Ignore:
- Crypto, consumer gadgets, funding news without a technical angle
- Generic "AI will replace X" opinion pieces with no data

## Formats and cadence per platform

Why this cadence: `context/strategy.md`. Algorithm rules per
platform: `context/platform-rules.md`.

| Platform | Formats | Cadence target |
|---|---|---|
| Medium | lab article, guide, playbook | 1 article/week, Wednesday |
| LinkedIn | text post, carousel (PDF doc), comments | 5 posts/week (Mon-Fri), 10-15 comments/day |
| Instagram | carousel, single post, Reel | 5 posts/week (Mon-Fri), same day and theme as LinkedIn |
| X | tweet, thread, reply, quote | 5 posts/week (Mon-Fri, one is the Wednesday thread), 10-15 replies/day |

No weekend posting on any channel.

## Weekly slot map

Content-pipeline fills these slots. Formulas are defaults; swap when the
topic fits another one better.

| Day | Theme | LinkedIn | Instagram | X | Medium |
|---|---|---|---|---|---|
| Mon | Reflection (career, tech, goals) | post, F3 or F4 | single post | tweet, T3 | |
| Tue | Concept explainer with a diagram | post or carousel + diagram | carousel | tweet, T8 or T2 | |
| Wed | Medium recap | post, link in first comment | carousel recap | thread, T4/T9/T10, link in last tweet | article |
| Thu | Meme-format CTA to Wednesday's piece | post (meme image) | single post (meme) | tweet, T1 or T5 | |
| Fri | Curated list of the week | post (list) | carousel (list) | tweet, best item | |

The month's dominant theme (see strategy.md) feeds Tue and Wed first.
