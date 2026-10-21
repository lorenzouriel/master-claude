# Storage

Modules that keep state (pipeline, metrics, news log, dossiers, reviews) read
and write the files below. Resolve the location once per session.

## Where data lives

1. **Local (Claude Code, preferred).** Use the `data/` folder at the project
   root (next to `CLAUDE.md`). Check by listing `data/`.
2. **Google Drive (claude.ai, scheduled cloud runs).** If there is no writable
   `data/` folder, use the Google Drive connector: folder
   `content-os/data/` in the user's Drive, same file names. Create the folder and
   files from the templates below on first use, after telling the user.
3. **Neither available.** Produce the output in chat and say that nothing was
   saved. Never pretend a file was written.

## Files

| File | Owner module | Format |
|---|---|---|
| `data/pipeline.csv` | content-pipeline | CSV, schema in content-pipeline.md |
| `data/metrics/posts.csv` | content-analytics | CSV, one row per published piece |
| `data/metrics/followers.csv` | content-analytics | CSV, date + platform + followers |
| `data/metrics/raw/` | content-analytics | original exports, untouched, dated file names |
| `data/news/seen.csv` | news-radar | CSV, dedup log of surfaced items |
| `data/dossiers/YYYY-MM-DD.md` | daily-dossier | Markdown, one per day |
| `data/reviews/YYYY-Www.md` | weekly-review | Markdown, ISO week |
| `data/seo/` | seo | Markdown: research, on-page, geo scores, `clusters.md`, monthly monitor |
| `data/research/<topic>-YYYY-MM-DD.md` | topic-research | Markdown briefing |
| `data/archive/YYYY/MM/WEEK NN/<platform>/` | archive | Published pieces as Markdown (+ images for Instagram) |

Working outputs (drafts before they are published) live outside `data/`:
`output/articles/`, `output/carousels/`, `output/reels/`. The archive module
moves them into `data/archive/` once they are approved and scheduled.

## Rules

- Append or update rows; never rewrite a CSV from memory. Read it, change it,
  write it back.
- Dates in ISO 8601 (`2026-10-06`). Times in UTC with offset noted.
- Keep raw exports. Analysis must be reproducible from `raw/`.
- Get today's date from the system, not from memory.
