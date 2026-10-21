---
name: video-edit
description: Edit a recorded video (Reel, TikTok, YouTube long-form or Short) in the owner's brand with the local vedit engine - cut pauses, breaths, false starts and retakes, burn brand captions, clean and level the voice, face-tracked camera motion, tab scenes, animated data overlays (counter, steps, checklist, charts), sound effects and music, end card, per-platform export, verified output. Use for "edit this video", "cut the pauses", "add captions", "add motion", "make it like this reference", "reframe for vertical", "render the Reel", "edit the Monday video", or when a Reel/YouTube slot has a raw recording.
---

# Video edit

Local editing engine in `scripts/` (`vedit.py`). Everything runs on this
machine; no API key, no upload. Claude Code only. On claude.ai there is no
shell: say editing is unavailable there and stop.

```
uv run --project <S> python <S>/vedit.py <command> ...
```

`<S>` is this skill's `scripts/` folder (absolute path); `<JOB>` is the job
folder. Every command has `--help`.

| Stage | Commands |
|---|---|
| Setup | `doctor`, `assets` |
| Before approval (read-only) | `inspect` |
| Cut | `new`, `transcribe`, `plan`, `audio`, `verify` |
| Captions | `captions`, `safety` |
| Plain render | `render` (cut + captions + loudness, QA) |
| Motion | `render --base`, `faces`, `suggest`, `motion`, `templates`, `compose`, `mix` |
| Review | `qa`, `timeline`, `reference` |

## Preflight (every invocation)

`vedit.py doctor`. Required: ffmpeg/ffprobe with `subtitles`, `loudnorm`,
`ebur128`, `afftdn`; libx264 and aac; faster-whisper; fonts. If the env is
missing, `uv sync --project <S>` (ask first; ~350 MB). First run on a machine:
`vedit.py assets` (YuNet face model, 230 KB from the OpenCV zoo, plus the
procedurally generated sound effects). The `large-v3-turbo` model (~1.6 GB)
downloads on first transcribe if not cached: say so before running. Never
install system tools without a yes.

## 1. Inspect, then the settings card

Read-only before approval: `vedit.py inspect <files>` (ffprobe facts, a 30 s
cached-model language sample, notes on HDR, VFR, missing or extra audio).
Look at 3 frames (10%, 50%, 90%) for face position, existing text, anything
sensitive. With a reference video, also run `vedit.py reference <ref.mp4>`
(read-only: shot pace, zoom events, caption bands, palette, loudness) and
build the Visuals row from `reference.md`, in the owner's brand
(`brand/video-theme.json`, written at install) unless they ask
for the reference's colors.

Then show the card and **wait for a separate reply**. A detailed first prompt
does not approve its own card.

Card format (Markdown, not a code block, no emojis, no em dashes):

```markdown
### <title>: settings to approve

<one sentence: what I'll make from what>

**Your call before I start**
- <unknown or conflicting item> **A)** <recommended> · **B)** <alternative>

**Settings**
- **Goal**: <target reel|youtube|short>, <pacing>, about <duration> _(you asked | suggested)_
- **Videos**: <file (m:ss)> ... _(from your folder)_
- **Cleanup**: remove long pauses, breaths, false starts and retakes; keep complete words _(suggested)_
- **Captions**: <pill with the spoken word lit | static box | off>, word for word, up to 3 words, below the chin, code and tool names in JetBrains Mono · SRT <yes|no> _(suggested)_
- **Language**: <detected> speech · captions as spoken, no translation _(detected in a short sample)_
- **Sound**: voice to -14 LUFS · denoise <off|light|strong> · takes <evened|as recorded> · effects <on movements|off> · music <track, ducked|none> _(suggested)_
- **Visuals**: camera <gentle zooms on the face|still> · <scenes: tab with cards at "...", checklist at "...", counter at "..."> · end card <logo + name|none> _(suggested)_
- **Image**: original look, no filter _(suggested)_
- **Format**: <WxH>, <crop|pad> from <source WxH>, <fps> as source · one MP4 _(from your video)_
- **Review**: I check a 10-15 s sample, then the full QA and a re-transcription of the cut _(suggested)_
- **Delivery**: `output/reels/<YYYY-MM-DD>-<slug>/<slug>-<target>-v001.mp4` _(suggested)_

Technical: <WxH> · <fps> constant · H.264 8-bit 4:2:0 BT.709 · -14 LUFS · peak <= -1 dBTP

Reply **ok** to start, or tell me what to change, e.g. "no music", "keep the pause at 0:42".
```

- Tag each value's origin. Unknowns go in "Your call" with lettered options.
  Omit that block when nothing is open; then ask for **ok**.
- "ok" approves only if it answers every open item. Any change: show the whole
  card again with changed rows prefixed "Changed:" and wait again.
- Defaults: cleanup on, pill captions, denoise from the measurement, effects
  and music off, camera motion off, no scenes, no end card. Motion, effects,
  music and end card are offered, not assumed.
- HDR source: offer **A)** convert to SDR (`--tonemap`) or **B)** leave it out.
- Narrower scope stays narrow: "captions only" means no recut, no loudness change.

## 2. Job, transcript, audio check (after approval)

```
vedit.py new --dir output/reels/<YYYY-MM-DD>-<slug> --src <file> [<file> ...] --slug <slug>
vedit.py transcribe --job <JOB> [--language pt] [--prompt "<brand and product names>"]
vedit.py audio --job <JOB>
```

- `--prompt` takes proper names only, never the script.
- `takes.md`: one line per phrase with source times, pauses, `[?]` on
  low-confidence words.
- `audio` measures each source: SNR from this recording's own pauses (>= 30 dB
  clean, 20-30 light denoise, < 20 strong), clipping (times to listen; clipped
  speech can't be restored, suggest a retake), and after `plan`, per-take
  levels. Rerun `audio` after `plan` to get take gains.
- Raw files stay where they are. Never move, overwrite or delete a recording.

Post one short progress line per phase (transcribing, cutting, checking the
sample, rendering, checking the file). No commands or paths in them.

## 3. EDL and plan

Write `<JOB>/work/edl.json` from `takes.md`:

```json
{
  "keep": [{"src": 0, "from": 1.12, "to": 14.12, "why": "hook, take 2"}],
  "maxPause": 0.35, "joinGap": 0.25,
  "protect": [[42.0, 43.4]],
  "corrections": {"Fabrik": "Fabric"},
  "mono": ["dbt", "Delta Lake"]
}
```

| Field | Meaning |
|---|---|
| `keep` | Source-second ranges in output order. `"keep": "all"` keeps every word (tighten only). |
| `maxPause` / `joinGap` | Pauses longer than `maxPause` are cut down to `joinGap`. |
| `tighten` | `false` keeps internal pauses. |
| `protect` | Source intervals never cut. |
| `corrections` | Caption-only spelling fixes the owner approved. |
| `mono` | Terms in JetBrains Mono (tokens with `_ / . () =`, flags, camelCase are automatic). |

Editorial rules: clearest complete take, not the last one; hook (first 3 s) is
speech, not a greeting or title card; never cut a negation, qualifier, number
or command; recorded speech is the truth, the script only helps spelling.

`vedit.py plan --job <JOB> --edl <JOB>/work/edl.json` measures every edge on
the waveform (10 ms envelope relative to this speaker, 60/70 ms pads, 120 ms
reach for quiet consonants; a Whisper start that lands inside a pause is
searched up to 0.6 s forward), snaps to frames, and writes `plan.json` and
`cut_words.json`.

## 4. Captions

```
vedit.py captions --job <JOB> --target reel|short|youtube [--srt] [--vtt]
vedit.py safety --job <JOB> [--samples <time>]
```

`captions` groups up to 3 words and lints coverage, em dashes, emojis, `[?]`;
fix every issue before rendering. `safety` checks the base for existing
on-screen text in the caption band and, with `--samples`, draws the pill and
box styles on a real frame (`work/caption-styles.jpg`) to show on the card.

## 5a. Plain render (no motion)

```
vedit.py render --job <JOB> --target reel --sample <start> <end>
vedit.py render --job <JOB> --target reel [--fit crop|pad] [--crop-x 0.5] [--denoise auto] [--level-takes] [--tonemap]
```

Burned ASS captions, two-pass loudness, QA. `--denoise auto` uses the `audio`
recommendation (highpass 80 Hz + afftdn at the measured floor).

## 5b. Motion render

```
vedit.py render --job <JOB> --target reel --base [--denoise auto] [--level-takes]
vedit.py faces --job <JOB>
vedit.py suggest --job <JOB>
vedit.py motion --job <JOB>                      # creates work/motion.json (auto camera + pill captions)
vedit.py compose --job <JOB> --still 0.5,3.2,6.0 # stills to check placement before the full render
vedit.py compose --job <JOB>
vedit.py music [--mood chill-beat]               # bundled CC0 tracks
vedit.py mix --job <JOB> --target reel [--music <track id | file>] [--music-start S] [--below 18] [--no-effects]
```

- `faces`: YuNet face path 10 times a second, smoothed. Zooms anchor on the
  face, captions sit below the chin, overlays avoid the face.
- `suggest`: spoken numbers (pt/en/es words, money, percentages), ordinal
  steps, short lists, negated lists, calls to action, mapped to templates with
  word anchors. Suggestions, not decisions; values come only from the speech.
- `motion.json` (edit it after `motion` creates it):

```json
{
  "camera": {"auto": true, "base": [1.0, 1.08], "push": 0.07, "emphasis": ["colei", "professor#2"]},
  "captions": {"style": "pill", "mono": ["home office"]},
  "scenes": [
    {"type": "tab", "cards": [{"at": "mais", "text": "Mais controle"}, {"at": "menos", "text": "Menos riscos"}],
     "end": "segurança@end", "numbered": true},
    {"type": "overlay", "template": "counter", "at": "dois", "end": "reais@end",
     "params": {"value": 2000, "prefix": "R$ "}, "place": "auto", "hidesCaptions": false}
  ],
  "endCard": {"logo": "brand/assets/logo-dark.png", "name": "<Brand name>", "kicker": "", "seconds": 2.0}
}
```

  Colors and fonts: `brand/video-theme.json` (written by `/system install` from
  the design guide) applies to every render; a `"theme"` object in motion.json
  overrides it for one job (e.g. a client's brand, same role names).
  Times are output seconds or word anchors: `"word"`, `"word#2"` (second
  occurrence), `"word@end"`. Camera: base zoom alternates per sentence, one
  push-in per stressed word, gentle springs, never tilts or shakes. Card icons:
  `number`, `check`, `down`, `arrow`. Run `compose` from the content-creation
  root (or pass `--root`) so the logo path resolves.
- Templates (`vedit.py templates` lists params; `templates --preview NAME
  --params '{...}'` writes an 8-frame sheet): `counter`, `steps`, `checklist`,
  `strikeout`, `bar_chart`, `line_chart`, `progress_bar`, `impact_word`,
  `label`, `notification`, `comment_cta`, `highlight`. Colored by the brand
  theme; dark card by default, `"theme": "light"` for a white card.
- `compose` also writes `events.json` (every movement's impact time). `mix`
  turns it into a sound plan (effect peaks land on the frame, close events
  collapse to the stronger one), adds music solved `--below` LU under the
  voice with sidechain ducking and a lift on the end card, then two-pass
  loudness and QA.
- Effects are generated by `sfx.py` (whoosh, swish, pop, click, tick, type,
  riser, impact, success, notification).
- Music lives in the skill: `scripts/music/`, 23 CC0 tracks in six moods
  (calm, chill-beat, emotional, groove, hiphop, upbeat) by HoliznaCC0, Frank
  Nora and Rafael Krux, listed in `music/catalog.json`. Pick by mood with
  `vedit.py music`, pass the track id to `mix`; it starts at the track's
  catalog `start` (where it is full) unless `--music-start` says otherwise.
  Name the track and its license on the card. A file the owner provides also
  works as `--music <path>`.

## 6. Verify, then deliver

```
vedit.py verify --job <JOB> [--language pt]
vedit.py timeline <file> <start> <end> --job <JOB>
```

- `verify` re-transcribes the rendered cut and diffs it against the words the
  plan meant to keep. A missing word near a join means a clipped word: fix the
  EDL and re-plan. It also lists silences >= 0.7 s and writes
  `junctions.jpg` (frames before/after every join).
- `timeline` draws filmstrip + waveform + words for a range. Use it on
  `work/base.mp4` (voice only) whenever timing looks off; a still frame can't
  show timing.
- QA results: decode, size, fps, duration, one audio track, -14 +/-1 LUFS,
  true peak <= -1 dBTP, caption text. Caption OCR is `not_checked` (no local
  reader): say so. Any failed check blocks delivery.

Delivery card:

```markdown
### Your video is ready

- **Video**: `output/reels/<...>/<slug>-reel-v001.mp4`
- **What changed**: 0:31 to 0:29 · 3 pauses removed · captions · 4 push-ins · tab with 3 cards · end card · effects + music
- **Checked**: decode, size, frame rate, duration, loudness, true peak, caption text, re-transcription 100% match
- **Not checked**: caption OCR (no local reader), checked by eye on the stills
- **Limits**: <source limits or workarounds; omit when none>

Want changes? e.g. "bigger captions", "no music".
```

Then update the pipeline row (`content-pipeline`) with the file path. Status
stays `drafted` until `metricool` schedules it.

## Export specs

| Target | Size | Length | Notes |
|---|---|---|---|
| `reel` | 1080x1920 | 15-60 s, 90 s max | Same file to Instagram and TikTok. No text in the bottom 20% or right 15% |
| `youtube` | 1920x1080 | 8-15 min | Long-form; per the YouTube slot in `context/pillars.md` |
| `short` | 1080x1920 | under 60 s | Strongest segment of the long-form. New job on the raw recording (the master has captions burned in), `keep` = that segment's source times |
| `source` | as recorded | | No scale |

Reframe: `--fit crop` fills the target (horizontal to vertical: `--crop-x`
from a frame, 0 left, 1 right); `--fit pad` letterboxes on black. In motion
renders the zoom follows the tracked face.

## When a step fails

An engine error is not the owner's problem. No tracebacks in chat. Retry
through another route (plain render instead of compose, no denoise, no
effects) and note the workaround once in the delivery card. If no route
works, stop that step, explain in one line, offer concrete choices. Never
drop an approved setting silently, never call an unchecked file verified.

## Hard rules

- Never publish or upload. Only `metricool` schedules; it needs the file at a
  public URL, which the owner provides.
- Never send media off this machine without an explicit yes.
- Never invent caption text, numbers, results or names in overlays. Unclear
  word: `[?]` and ask.
- On-screen text follows the avoid-list in `context/preferences.md`; colors
  come only from the brand theme.
- Logo only when the card's end card row says so.

## Related modules

- `ig-reel-script`, `tiktok`, `youtube`: write the script this edits.
- `youtube` (`thumbnail`) and `youtube-thumbnail`: cover for the long-form.
- `metricool`: schedules the rendered file.

Engine design follows [editonny](https://github.com/soumatheusgomes/editonny)
by Matheus Gomes (MIT): the approval card, waveform trimming, face-anchored
camera, tab scenes, template set, peak-aligned sound plan, cut verification
and reference measurement. No editonny code is included; the bundled music is
CC0 (OpenGameArt and FreePD originals).
