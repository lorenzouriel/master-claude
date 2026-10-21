---
name: metricool
category: content
description: >
  Schedule, draft, and publish finished posts (LinkedIn, Instagram, X, TikTok,
  YouTube, Threads, Bluesky, etc.) and read profile analytics, past posts, best
  posting times, and competitors through the Metricool MCP connector. Use when
  the user asks to schedule, queue, publish, or "send to Metricool" a post, see
  the planner or calendar gaps, edit a scheduled post, pull post or follower
  metrics, list past posts, or find the best time to post. No API key: auth is
  the connector's OAuth.
type: mcp
version: "1.0.0"
mcp_server: https://ai.metricool.com/mcp
categories: [social-media, publishing, scheduling, analytics]
---

# Metricool (MCP)

Schedule posts and read performance data through Metricool's official MCP
server. This skill handles delivery and data pulls only. The copy comes from
another module (linkedin-post, x-post, x-thread, ig-carousel, ig-reel-script,
newsletter-humana, etc.) or from the user, and is never rewritten here beyond
platform limits the user approves.

## Setup (one-time, done by the user)

- **Claude Code:** the server is registered in the project's `.mcp.json`
  (`claude mcp add --transport http --scope project metricool https://ai.metricool.com/mcp`).
  Approve it on first launch, then `/mcp` → `metricool` → Authenticate and
  grant access in the browser.
- **claude.ai / Desktop:** Settings → Connectors → Metricool → Connect, then
  Grant Access.

Works on every Metricool plan, Free included; plan limits apply (Free: 20
scheduled posts per month, 30 days of analytics history). Each social network
must be connected inside Metricool first (one brand = the owner's channels).

If no Metricool tools are present (check with ToolSearch for "metricool"), stop
and tell the user the connector isn't enabled or authenticated. Do not fall
back to the REST API with a token.

## Tools

Names on Metricool's server (they may appear prefixed, e.g.
`mcp__metricool__post_schedule_post`). The list changes with the server, so
read each tool's schema before calling it; the schema wins over this table.

| Tool | Use |
|---|---|
| `get_brands` | Sanity check and the brand ID (`blogId`) every other call needs. Shows connected networks and timezone. |
| `get_scheduled_posts` | Planner: scheduled and draft posts in a date range. |
| `post_schedule_post` | Create a scheduled post, a draft, or a post for review, on one or more networks. |
| `update_schedule_post` | Edit text, date, or network of a scheduled post. |
| `get_best_time_to_post` | Best days and hours per network from the owner's own engagement history. |
| `get_metrics` | Catalog of metrics available per network. Call before `get_analytics` when unsure of a metric name. |
| `get_analytics` | Account-level metrics for a date range (followers, reach, impressions, engagement). |
| `get_linkedin_posts`, `get_x_posts`, `get_instagram_posts`, `get_instagram_reels`, `get_instagram_stories`, `get_tiktok_videos`, `get_youtube_videos`, `get_thread_posts`, `get_bluesky_posts` | Past posts with per-post metrics for a date range. |
| `get_network_competitors`, `get_network_competitors_posts` | Competitor accounts added in Metricool and their posts. |

Not available through the MCP: inbox, reading or replying to comments, Canva or
Drive files, ad campaign management.

## Schedule a post

1. **Resolve the brand and network.** `get_brands`; cache `blogId` and the
   brand timezone for the conversation. Confirm the target network is
   connected; if not, tell the owner to connect it in Metricool.
2. **Resolve the time.** Interpret times in the brand timezone (fallback
   America/Sao_Paulo, as in the old Buffer setup). Get today's date from the system, never from memory.
   Reject times in the past. "Best time" → `get_best_time_to_post` for that
   network and day, and show the slot before using it.
3. **Pre-flight check (no call yet).**
   - LinkedIn 3,000 chars. X 280 (or the account's limit). Threads 500.
     Bluesky 300. Instagram caption 2,200 and requires media. TikTok and
     YouTube require video.
   - Media: check in the tool schema how media is passed (public URL or
     upload). If only URLs are accepted, the file must be publicly reachable;
     say so before scheduling. Carousels and video sometimes need finishing in
     the Metricool planner; the tool response links to it.
   - Links: no links in the body of LinkedIn posts or tweets. If the text has
     one, flag it and propose moving it (LinkedIn → first comment, X → first
     reply); change the text only after the owner agrees. If the schema has a
     first-comment field, use it; otherwise list the first comment as a manual
     step right after the post goes live.
   - X threads: check whether the schema accepts a thread. If not, schedule
     tweet 1 only and hand the owner the rest to post as replies.
4. **Confirmation card.** Network(s), mode (scheduled / draft / review / now),
   time in local + UTC, char count, media, and the exact text. Wait for an
   explicit yes.
5. **Create.** `post_schedule_post` with the mode chosen:
   - Specific time or best time → scheduled at that date.
   - Draft / review → save without auto-publishing, so it waits in the planner.
   - Post now → only if the owner literally said "post now" / "publish now".
   Multi-network: one post per network unless the schema supports multipost,
   all shown in the same card.
6. **Verify.** `get_scheduled_posts` for that day; report status, time, the
   Metricool post ID, and the planner link from the response. One line.
7. **Log.** Update the pipeline row
   (`.claude/skills/content/content-pipeline/SKILL.md`): status `scheduled`
   (or `published` for post now), `scheduled_at`, `metricool_id`. Create the
   row if missing.
8. **Archive.** For `scheduled` or `published` (not drafts), run "File a
   scheduled piece" in `.claude/skills/content/archive/SKILL.md`.

Default when the user says only "send it to Metricool": save as a draft for
review and ask for a time. Never publish immediately without "now".

## Read data

- **Profile metrics:** `get_metrics` for the network, then `get_analytics` for
  the range (default last 30 days vs. the previous 30). Followers, reach,
  impressions, engagement.
- **Past posts:** the `get_<network>_posts` tool for the range. Feeds
  `content-analytics` (it upserts into `data/metrics/posts.csv`, keyed by
  `post_url`, with `collected_at`). History depth depends on the plan (Free:
  30 days); when a range returns nothing older, say the plan limit was
  probably hit instead of reporting zero posts.
- **Best time:** `get_best_time_to_post` per network; feeds the weekly plan.
- **Competitors:** only accounts the owner added in Metricool's Competitors
  section.

Report numbers as returned. Never estimate a missing metric.

## Other operations

- **Planner / gaps:** `get_scheduled_posts` for the week; show date, network,
  first line; flag empty slots against `context/pillars.md`.
- **Edit:** `get_scheduled_posts` to find it, show the diff, then
  `update_schedule_post` after a yes.
- **Delete:** not exposed by the MCP; tell the owner to delete it in the
  Metricool planner.

## Hard rules

- Never create or update a post the user didn't confirm in the card.
- Never bulk-edit scheduled posts.
- Never ask for, store, or use a Metricool API token in this skill.
- Report errors verbatim (short) and diagnose: auth expired → `/mcp`
  re-authenticate; network disconnected → reconnect it in Metricool; plan limit
  (20 posts/month on Free) → say so and offer a draft instead of retrying.
