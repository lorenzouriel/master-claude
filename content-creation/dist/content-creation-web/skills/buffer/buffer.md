---
name: buffer
category: content
description: >
  Publish, queue, and schedule finished posts to social channels (LinkedIn,
  Instagram, X, YouTube, TikTok, Threads, Bluesky, etc.) through the Buffer MCP
  connector. Use when the user asks to schedule, queue, publish, or "send to
  Buffer" a post, list their Buffer channels or queue, save a content idea to
  Buffer, or edit/delete a scheduled post. No API key or CLI: auth is the
  connector's OAuth.
type: mcp
version: "2.0.0"
mcp_server: https://mcp.buffer.com/mcp
categories: [social-media, automation, publishing, scheduling]
---

# Buffer Publisher (MCP)

Schedule and publish posts through Buffer's official MCP server. This skill only
handles delivery. The copy itself comes from another module (linkedin-post,
x-post, x-thread, ig-carousel, ig-reel-script, newsletter-humana, etc.) or from the user, and is never rewritten here
beyond platform limits the user approves.

## Setup (one-time, done by the user)

Add Buffer as a custom connector in Claude: Settings → Connectors → Add custom
connector → URL `https://mcp.buffer.com/mcp`, then sign in with Buffer (OAuth).
Enable it for the chat. Nothing to install, no `BUFFER_API_KEY`, no `.env`.

If no `buffer`/`Buffer` tools are present (check with ToolSearch first), stop and tell
the user the connector isn't enabled in this chat. Do not fall back to the CLI, curl,
or the GraphQL API with a token.

## Tools

Exact names on Buffer's server (they may appear prefixed, e.g. `mcp__Buffer__create_post`):

| Tool | Use |
|---|---|
| `get_account` | Sanity check: who is signed in, plan, org |
| `list_channels` / `get_channel` | Channel IDs, service (linkedin, instagram...), timezone, posting schedule |
| `list_posts` / `get_post` | Queue and status for a channel or a single post |
| `create_post` | Queue, schedule, or draft a post |
| `delete_post` | Remove a scheduled/queued post |
| `create_idea` | Save to Buffer's Ideas library (no channel, no schedule) |
| `introspect_schema` | Inspect GraphQL input shapes when a field is unclear |
| `execute_query` / `execute_mutation` | Escape hatch for operations without a dedicated tool (e.g. editing an existing post) |

Read each tool's schema from its definition before calling it. Field names below are
the expected GraphQL shape (`channelId`, `text`, `schedulingType`, `mode`, `dueAt`),
but the tool schema wins. If anything is ambiguous, call `introspect_schema` rather
than guessing.

## Workflow

1. **Resolve the channel.** Call `list_channels`. Match on the platform the user named.
   If they have more than one channel for that service (e.g. personal + company
   LinkedIn), ask which. Cache the ID for the rest of the conversation.
2. **Resolve the time.** Interpret times in the channel's timezone (from `list_channels`),
   falling back to America/Sao_Paulo. Convert to ISO 8601 UTC. Check the date against the
   current date with the time tool, never from memory. Reject times in the past.
3. **Pre-flight check (no call yet).** Validate against platform limits:
   - LinkedIn: 3,000 chars. X: 280 (or the account's limit). Threads: 500. Bluesky: 300.
     Instagram: caption 2,200, requires media.
   - Media URLs must be publicly reachable; Instagram/TikTok/YouTube posts without media fail.
   - Links: LinkedIn and X penalize links in the body. If the text has a
     link in the body, flag it and propose moving it (LinkedIn → first
     comment, X → first reply); change the text only after the user agrees. Buffer
     schedules the post only; list the first comment/reply in the card as a
     manual step for Lorenzo right after it goes live (or as a Buffer comment
     if the channel's schema exposes one; check with `introspect_schema`).
   - X threads: check whether the X channel's `create_post` input accepts
     a thread (multiple tweets). If not, schedule tweet 1 only and hand Lorenzo
     the rest to post as replies, or give him the whole thread to post by hand.
4. **Confirmation card.** Show channel (name + service), mode, time in local + UTC,
   char count, media, and the exact text. Wait for an explicit yes.
5. **Create.** Call `create_post` with the mode the user chose:
   - Queue → `schedulingType: automatic`, `mode: addToQueue`
   - Specific time → `mode: customScheduled` with `dueAt`
   - Post now → `mode: shareNow` (only if the user literally said post now / publish now)
   - Draft → save as draft so it shows in Buffer for review without publishing
6. **Verify.** Call `get_post` on the returned ID (or `list_posts`) and report status +
   scheduled time. One line, with the Buffer post ID.
7. **Log.** Update the matching row in the pipeline
   (`skills/content-pipeline/content-pipeline.md`): status `scheduled`
   (or `published` for shareNow), `scheduled_at`, `buffer_id`. If no row exists,
   create one. content-analytics later joins metrics on `buffer_id`.

Default when the user says only "send it to Buffer": queue it (`addToQueue`). Never
publish immediately without the words "now" / "publish now".

## Other operations

- **List queue:** `list_posts` for the channel, show time + first line of each post.
- **Edit a scheduled post:** no dedicated tool. `get_post` first, `introspect_schema` for
  the edit mutation's input, then `execute_mutation`. Show the diff before sending.
  If editing isn't supported for that post state, delete + recreate after confirming.
- **Delete:** `delete_post`, always after confirming which post (show its text + time).
- **Ideas:** `create_idea` for drafts the user wants parked without a channel or date.
- **Multi-channel:** one `create_post` per channel, each confirmed in the same card.

## Limits (Free plan)

- 3 channels. Lorenzo has 3 Buffer channels to fill (LinkedIn, Instagram, X;
  Medium is published by hand), so the free plan fits exactly; 10 queued posts per channel (frees up as posts publish).
- API quota also applies to MCP traffic (~100 requests / 15 min). Avoid polling
  `list_posts` in loops; one verify call per post is enough.
- If `create_post` fails because the queue is full, say so and offer `create_idea` or
  a later slot instead of retrying.

## Hard rules

- Never call `execute_mutation` with anything the user didn't confirm in the card.
- Never `delete_post` in bulk.
- Never ask for, store, or use a Buffer API key in this skill.
- Report errors verbatim (short) and diagnose: auth expired → reconnect the connector;
  channel disconnected in Buffer → reconnect it at buffer.com; validation → fix the field.
