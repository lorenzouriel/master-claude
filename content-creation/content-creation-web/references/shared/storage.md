# Storage (Claude web: Google Drive)

> This is the claude.ai web build. Skill files are read-only and the chat
> sandbox is wiped after each conversation, so **all state lives in Google
> Drive**, reached through the Google Drive connector. Every module path that
> starts with `data/` or `output/` means the matching folder under
> `content-os/` in Drive. Resolve it with the rules below; never write state
> anywhere else.

## Requirements

- The **Google Drive** connector is enabled in this chat. Check with the tool
  list before the first read or write. If it's missing, stop and tell the user
  to enable it (Settings → Connectors). Never pretend a file was saved.
- Tools used: `search_files`, `download_file_content`, `read_file_content`,
  `create_file`, `trash_file`, `get_file_metadata`.

## Folder map

Folder IDs are stable. Use them directly as `parentId`; don't search for
folders.

| Logical path | Drive folder | Folder ID |
|---|---|---|
| (root) | `content-os/` | `1rYEa4zjBqiiVLpxL328fy02urKp33KIl` |
| `data/` | `content-os/data/` | `1b3k8Nd9r4EAOjSMB2rTJb5BMqjDDPPNr` |
| `data/metrics/` | `content-os/data/metrics/` | `1fHiUW15TJ8Ro4Jicj4C79_CV74f2ryqi` |
| `data/metrics/raw/` | `content-os/data/metrics/raw/` | `1-OzEaVXTtqdKyXyy2bNLs5kF9uE9DaqS` |
| `data/news/` | `content-os/data/news/` | `192zSD2Gmy1xLbavbonl5UfGXhbsOrkIY` |
| `data/dossiers/` | `content-os/data/dossiers/` | `1M6J-v_bL_UAYtwm1ZRuFEPzLblQgvQYn` |
| `data/reviews/` | `content-os/data/reviews/` | `1tBb58f_AAS4wx1NqW0F0mI2WnW66DK60` |
| `data/research/` | `content-os/data/research/` | `1p3i4cW79OPlvcuaIoekJ3sli1Bvgaqut` |
| `data/seo/` | `content-os/data/seo/` | `1n-ieaGUvlSfLjSOgrv1fNzhPymB8ueaf` |
| `data/archive/` | `content-os/data/archive/` | `1D1zyq0dXi0vbjqLoMXsBXF1cdf6wgbTS` |
| `output/` | `content-os/output/` | `1JlCXjOGR-dMt9PExBu0ZgMPaEDQXnC0f` |
| `output/articles/` | `content-os/output/articles/` | `13fjXWpwdL4aNkwR8a2Xzr19srbbfiwdM` |
| `output/carousels/` | `content-os/output/carousels/` | `1PPbjuC8eerPu44s1NekWJ007Lz-CENF7` |
| `output/reels/` | `content-os/output/reels/` | `1Pvhcw5jI5xXE1vn90D0nbc_MNi2gpvGM` |

If a folder ID returns "not found" (the user moved or deleted it), search for
the folder by title under its parent, tell the user, and ask before creating a
replacement.

## Files

| Logical file | Owner module | Format |
|---|---|---|
| `memory-overrides.md` (root) | every module (see SKILL.md) | Markdown table of saved corrections |
| `data/pipeline.csv` | content-pipeline | CSV, schema in content-pipeline.md |
| `data/metrics/posts.csv` | content-analytics | CSV, one row per published piece |
| `data/metrics/followers.csv` | content-analytics | CSV, date + platform + followers |
| `data/metrics/raw/` | content-analytics | original exports, untouched, dated file names |
| `data/news/seen.csv` | news-radar | CSV, dedup log of surfaced items |
| `data/dossiers/YYYY-MM-DD.md` | daily-dossier | Markdown, one per day |
| `data/reviews/YYYY-Www.md` | weekly-review | Markdown, ISO week |
| `data/seo/...` | seo | Markdown: research, on-page, geo scores, `clusters.md`, monthly monitor |
| `data/research/<topic>-YYYY-MM-DD.md` | topic-research | Markdown briefing |
| `data/archive/YYYY-MM-<platform>-<slug>.md` | archive | Published pieces, flat (see "Archive layout") |
| `output/articles/`, `output/carousels/`, `output/reels/` | writing modules | Drafts before publishing |

## How to read a file

1. Find it: `search_files` with
   `parentId = '<folder ID>' and title = '<file name>'`, **`pageSize: 50`**,
   `excludeContentSnippets: true`. If the result is empty but has a
   `nextPageToken`, follow the token before concluding the file is missing.
   File IDs change on every write (see below), so never reuse a file ID from
   an earlier conversation; always look it up.
2. Read it: `download_file_content` (returns base64; decode as UTF-8). Use
   `read_file_content` only for PDFs, Office files, and images.
3. If two files have the same title in the same folder (an interrupted
   write), use the one with the newest `modifiedTime`, then trash the older
   one and say so in one line.

## How to write a file

The Drive connector **cannot edit a file's content**. `update_file` only
renames or moves. So every change is a full rewrite:

1. Read the current file (above). Never rebuild a CSV from memory.
2. Apply the change to the full text (append rows, update cells).
3. `create_file` in the same folder, same title, with:
   - `textContent`: the full new text
   - `contentMimeType`: `text/csv` for CSV, `text/markdown` for Markdown
   - `disableConversionToGoogleType: true` (otherwise Drive turns it into a
     Google Doc or Sheet and the next read breaks)
4. Only after `create_file` succeeds, `trash_file` the old file ID. Trash is
   recoverable for 30 days, which doubles as a version history.
5. Report one line: what changed and the file link (`viewUrl`).

New files (a dossier, a review, a research brief) are just step 3.

For binary files (images, PDFs, xlsx exports): `create_file` with
`base64Content` and the real `contentMimeType` (`image/png`,
`application/pdf`, ...), `disableConversionToGoogleType: true`.

## Archive layout

Drive folders can't be created cheaply per week, so the web archive is flat
inside `data/archive/`, with the date and platform in the file name:

`YYYY-MM-DD-<platform>-<slug>.md` (e.g. `2026-10-08-x-why-dq-tests-fail.md`).

Carousels in the archive: one folder per carousel named
`YYYY-MM-DD-instagram-<slug>` (create it with
`mimeType`/`contentMimeType` `application/vnd.google-apps.folder`), holding
the slide PNGs, `carousel.pdf`, and `caption.md`.

The Claude Code build uses `YYYY/MM/WEEK NN/<platform>/` locally. When the
two meet (e.g. Lorenzo uploads a local archive to Drive), keep both layouts;
modules search by title, so either works.

## Rules

- Dates in ISO 8601 (`2026-10-06`). Times in UTC with offset noted.
- Keep raw exports. Analysis must be reproducible from `raw/`.
- Get today's date from the system, not from memory.
- Never write the same CSV twice in parallel. One write at a time per file.
- Batch: if a task changes the same file several times (e.g. logging 8
  pieces from repurpose), apply all changes in memory and write once.
