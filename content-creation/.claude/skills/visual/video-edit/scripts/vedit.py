"""vedit: local video editing for the owner's Reels, TikToks and YouTube videos.

Run through the skill's uv project so faster-whisper and numpy resolve:
    uv run --project <SCRIPTS> python <SCRIPTS>/vedit.py <command> ...
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import media  # noqa: E402
from media import MediaError  # noqa: E402

FONTS = HERE / "fonts"
MODEL_REPO = "models--mobiuslabsgmbh--faster-whisper-large-v3-turbo"


def emit(data, as_json):
    if as_json:
        print(json.dumps(data, indent=1, ensure_ascii=False))
    else:
        print(data if isinstance(data, str) else json.dumps(data, indent=1, ensure_ascii=False))


def load_job(job_dir):
    job_dir = Path(job_dir).resolve()
    path = job_dir / "job.json"
    if not path.is_file():
        raise MediaError(f"not a job folder (no job.json): {job_dir}")
    return job_dir, json.loads(path.read_text(encoding="utf-8"))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------- commands

def cmd_doctor(a):
    checks = []
    add = lambda name, ok, detail, required=True: checks.append(
        {"name": name, "ok": bool(ok), "detail": detail, "required": required})
    for tool in ("ffmpeg", "ffprobe"):
        add(tool, shutil.which(tool), shutil.which(tool) or "not on PATH")
    if shutil.which("ffmpeg"):
        have = media.filters_available()
        for f in ("subtitles", "loudnorm", "ebur128", "afftdn", "tile"):
            add(f"filter {f}", f in have, "ok" if f in have else "missing from this FFmpeg build")
        for f in ("zscale", "tonemap"):
            add(f"filter {f} (HDR to SDR)", f in have, "ok" if f in have else "missing", required=False)
        enc = media.encoders_available()
        for e in ("libx264", "aac"):
            add(f"encoder {e}", e in enc, "ok" if e in enc else "missing")
    try:
        import faster_whisper
        add("faster-whisper", True, faster_whisper.__version__)
    except ImportError:
        add("faster-whisper", False, "run: uv sync --project <SCRIPTS>")
    for mod in ("cv2", "PIL"):
        try:
            m = __import__(mod)
            add(mod, True, getattr(m, "__version__", "ok"))
        except ImportError:
            add(mod, False, "run: uv sync --project <SCRIPTS>")
    face = HERE / "assets" / "models" / "face_detection_yunet_2023mar.onnx"
    add("face model (motion)", face.is_file(), "ok" if face.is_file() else "run: vedit.py assets", required=False)
    fx = list((HERE / "assets" / "sfx").glob("*.wav")) if (HERE / "assets" / "sfx").is_dir() else []
    add("sound effects (mix)", bool(fx), f"{len(fx)} files" if fx else "run: vedit.py assets", required=False)
    try:
        tracks = music_catalog()
        missing = [t["id"] for t in tracks if not (MUSIC / t["file"]).is_file()]
        add("music library", not missing, f"{len(tracks)} CC0 tracks" if not missing
            else f"missing: {', '.join(missing[:3])}", required=False)
    except (OSError, ValueError, KeyError):
        add("music library", False, "scripts/music/catalog.json missing", required=False)
    cache = Path.home() / ".cache" / "huggingface" / "hub" / MODEL_REPO
    add("model large-v3-turbo cached", cache.is_dir(), str(cache) if cache.is_dir()
        else "downloads ~1.6 GB on first transcribe", required=False)
    fonts = [f.name for f in FONTS.glob("*.ttf")]
    add("brand fonts", len(fonts) >= 2, ", ".join(fonts) or "missing")
    ok = all(c["ok"] for c in checks if c["required"])
    if a.json:
        emit({"ok": ok, "checks": checks}, True)
    else:
        for c in checks:
            mark = "ok  " if c["ok"] else ("FAIL" if c["required"] else "warn")
            print(f"[{mark}] {c['name']}: {c['detail']}")
        print("ready" if ok else "not ready")
    return 0 if ok else 1


def cmd_inspect(a):
    from transcribe import sample_language
    out = []
    for i, src in enumerate(a.sources):
        info = media.probe(src)
        if not a.no_language and i < 3 and info["audioTracks"]:
            info["speech"] = sample_language(src)
        notes = []
        if info["hdr"]:
            notes.append("HDR source: needs a confirmed SDR conversion (--tonemap) or stays out")
        if info["vfr"]:
            notes.append("variable frame rate: output will be constant at the average rate")
        if info["audioTracks"] == 0:
            notes.append("no audio track: cannot transcribe or cut by speech")
        if info["audioTracks"] > 1:
            notes.append("several audio tracks: only the first is used")
        if not info["color"]["transfer"]:
            notes.append("no color tags: read as BT.709")
        info["notes"] = notes
        out.append(info)
    emit(out, True)


def cmd_new(a):
    job = Path(a.dir).resolve()
    if (job / "job.json").exists():
        raise MediaError(f"job already exists: {job}")
    infos = [media.probe(s) for s in a.src]
    (job / "work" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in FONTS.glob("*.ttf"):
        shutil.copy2(f, job / "work" / "fonts" / f.name)
    data = {"title": a.title or job.name, "slug": a.slug or job.name.split("-", 3)[-1],
            "created": date.today().isoformat(), "sources": [i["path"] for i in infos], "infos": infos}
    write_json(job / "job.json", data)
    emit({"job": str(job), "sources": [i["name"] for i in infos]}, True)


def cmd_transcribe(a):
    from transcribe import takes_markdown, transcribe
    job, data = load_job(a.job)
    work = job / "work"
    all_words = []
    for i, src in enumerate(data["sources"]):
        out = work / f"words-{i}.json"
        if out.exists() and not a.force:
            all_words.append(read_json(out)["words"])
            continue
        print(f"transcribing source {i}: {Path(src).name}", file=sys.stderr)
        result = transcribe(src, language=a.language, prompt=a.prompt, device=a.device)
        write_json(out, result)
        all_words.append(result["words"])
    (work / "takes.md").write_text(takes_markdown(all_words), encoding="utf-8")
    emit({"takes": str(work / "takes.md"), "words": [len(w) for w in all_words]}, True)


def cmd_plan(a):
    from cutplan import plan, remap_words
    job, data = load_job(a.job)
    work = job / "work"
    edl = read_json(a.edl)
    if Path(a.edl).resolve() != (work / "edl.json").resolve():
        write_json(work / "edl.json", edl)
    words = [read_json(work / f"words-{i}.json")["words"] for i in range(len(data["sources"]))]
    used = {int(k.get("src", 0)) for k in edl["keep"]} if edl["keep"] != "all" else set(range(len(words)))
    audio = {i: media.load_audio(data["sources"][i], 16000) for i in used}
    p = plan(edl, data["infos"], words, audio)
    write_json(work / "plan.json", p)
    write_json(work / "cut_words.json", {"words": remap_words(p["segments"], words)})
    emit({k: p[k] for k in ("sourceDuration", "cutDuration", "removed", "joins", "levels")}, True)


def _target_size(data, target):
    from render import TARGETS
    size = TARGETS[target]
    if size is None:
        info = data["infos"][0]
        size = (info["width"], info["height"])
    return size


def cmd_captions(a):
    import captions as cap
    job, data = load_job(a.job)
    work = job / "work"
    words = read_json(work / "cut_words.json")["words"]
    edl = read_json(work / "edl.json") if (work / "edl.json").exists() else {}
    w, h = _target_size(data, a.target)
    layout = cap.layout_for(w, h)
    cues = cap.cues(words, a.max_words, layout["chars"], edl.get("corrections"))
    mono = (a.mono.split(",") if a.mono else []) + edl.get("mono", [])
    (work / "captions.ass").write_text(cap.to_ass(cues, layout, mono), encoding="utf-8")
    write_json(work / "cues.json", cues)
    if a.srt:
        (work / "captions.srt").write_text(cap.to_srt(cues), encoding="utf-8")
    if a.vtt:
        (work / "captions.vtt").write_text(cap.to_vtt(cues), encoding="utf-8")
    issues = cap.lint(cues, words)
    emit({"cues": len(cues), "first": [" ".join(c["tokens"]) for c in cues[:3]], "issues": issues}, True)


def _audio_treatment(a, work):
    """Denoise filter + per-take gains from the flags and work/audio_check.json."""
    from audio_check import denoise_filter
    check = read_json(work / "audio_check.json") if (work / "audio_check.json").exists() else {}
    level = a.denoise
    first = (check.get("sources") or [{}])[0].get("noise", {})
    if level == "auto":
        level = first.get("denoise", "off")
    flt = denoise_filter(level, first.get("floorDb", -50)) if level != "off" else ""
    gains = {}
    if a.level_takes:
        gains = {r["segment"]: r["gainDb"] for r in check.get("takes", []) if r.get("gainDb")}
    return flt, gains, level


def cmd_render(a):
    import captions as cap
    import qa
    from render import render
    job, data = load_job(a.job)
    work = job / "work"
    plan = read_json(work / "plan.json")
    use_captions = not a.no_captions and not a.base and (work / "captions.ass").exists()
    if a.base:
        out = work / "base.mp4"
    elif a.sample:
        out = media.unique_path(work / f"sample-{a.target}.mp4")
    else:
        out = media.unique_path(job / f"{data['slug']}-{a.target}.mp4")
    flt, gains, level = _audio_treatment(a, work)
    result = render(plan, data["infos"], work, out, target=a.target, fit=a.fit, crop_x=a.crop_x,
                    captions_file="captions.ass" if use_captions else None, denoise=flt,
                    sample=a.sample, tonemap=a.tonemap, gains=gains)
    result.update({"denoise": level, "takeGains": gains})
    w, h = _target_size(data, a.target)
    fps = data["infos"][plan["segments"][0]["src"]]["fpsFloat"]
    duration = (a.sample[1] - a.sample[0]) if a.sample else plan["cutDuration"]
    duration = min(duration, plan["cutDuration"] - (a.sample[0] if a.sample else 0))
    issues = None
    if use_captions:
        issues = cap.lint(read_json(work / "cues.json"), read_json(work / "cut_words.json")["words"])
    report = qa.check(out, {"width": w, "height": h, "fps": fps, "duration": duration}, work,
                      caption_issues=issues)
    report["render"] = result
    write_json(work / f"{out.stem}-qa.json", report)
    emit(report, True)
    return 0 if report["ok"] else 1


def cmd_qa(a):
    import qa
    work = Path(a.job).resolve() / "work" if a.job else None
    report = qa.check(a.file, None, work)
    emit(report, True)
    return 0 if report["ok"] else 1


def cmd_assets(a):
    import urllib.request
    import sfx
    from faces import MODEL
    out = {}
    if not MODEL.is_file():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/"
               "face_detection_yunet/face_detection_yunet_2023mar.onnx")
        urllib.request.urlretrieve(url, MODEL)
    out["faceModel"] = f"{MODEL.name} ({MODEL.stat().st_size // 1024} KB)"
    for kind in sfx.KINDS:
        for v in range(3):
            sfx.write(kind, v)
    out["effects"] = f"{len(sfx.KINDS) * 3} generated in {sfx.CACHE}"
    emit(out, True)


def cmd_faces(a):
    from faces import track
    job, _ = load_job(a.job)
    work = job / "work"
    base = work / "base.mp4"
    if not base.exists():
        raise MediaError("render the base first: vedit.py render --job ... --base")
    info = media.probe(base)
    data = track(base, info["width"], info["height"])
    write_json(work / "faces.json", data)
    emit({"found": data["found"], "frames": data["frames"], "union": data["union"]}, True)


def cmd_audio(a):
    import audio_check as ac
    job, data = load_job(a.job)
    work = job / "work"
    out = {"sources": []}
    words = [read_json(work / f"words-{i}.json")["words"] if (work / f"words-{i}.json").exists() else []
             for i in range(len(data["sources"]))]
    for i, src in enumerate(data["sources"]):
        audio = media.load_audio(src, 16000)
        out["sources"].append({"name": Path(src).name, "noise": ac.noise(audio, words[i]), "clipping": ac.clipping(src)})
    if (work / "plan.json").exists():
        out["takes"] = ac.take_levels(read_json(work / "plan.json"), data["sources"], words)
    write_json(work / "audio_check.json", out)
    emit(out, True)


def cmd_motion(a):
    import compose
    job, _ = load_job(a.job)
    work = job / "work"
    path = work / "motion.json"
    if a.auto or not path.exists():
        write_json(path, compose.auto_motion(work))
    emit(read_json(path), True)


def cmd_templates(a):
    import templates
    if not a.preview:
        emit(templates.describe(), True)
        return
    import numpy as np
    from PIL import Image
    import draw as D
    if a.theme:
        D.set_theme(read_json(a.theme).get("theme", read_json(a.theme)))
    params = json.loads(a.params or "{}")
    times = [a.seconds * k / 7 for k in range(8)]
    tiles = []
    for t in times:
        bg = np.full((1920, 1080, 3), (110, 110, 110), np.uint8)
        im = templates.render(a.preview, t, params, 1080)
        if im is not None:
            if getattr(templates.REGISTRY[a.preview]["fn"], "fullframe", False):
                D.paste(bg, im, 0, 0)
            else:
                D.paste(bg, im, (1080 - im.shape[1]) / 2, (1920 - im.shape[0]) / 2)
        tile = Image.fromarray(bg).resize((270, 480))
        from PIL import ImageDraw
        ImageDraw.Draw(tile).text((8, 6), f"{t:.2f}s", font=D.font(22, "mono"), fill=D.WHITE)
        tiles.append(tile)
    sheet = Image.new("RGB", (270 * 8, 480), D.WHITE)
    for k, tile in enumerate(tiles):
        sheet.paste(tile, (k * 270, 0))
    out = Path(a.out or f"template-{a.preview}.jpg")
    sheet.save(out, quality=88)
    emit({"preview": str(out.resolve()), "events": templates.events(a.preview, params)}, True)


def cmd_suggest(a):
    import review
    job, _ = load_job(a.job)
    emit(review.suggest(read_json(job / "work" / "cut_words.json")["words"]), True)


def cmd_compose(a):
    import compose
    job, _ = load_job(a.job)
    work = job / "work"
    root = Path(a.root).resolve() if a.root else Path.cwd()
    stills = [float(x) for x in a.still.split(",")] if a.still else None
    emit(compose.render(work, root, work / "picture.mp4", stills), True)


MUSIC = HERE / "music"


def music_catalog():
    return read_json(MUSIC / "catalog.json")["tracks"]


def resolve_music(ref, start):
    """Track id from the skill's library (music/catalog.json), or a file the owner provides."""
    if not ref:
        return None, start
    for t in music_catalog():
        if t["id"] == ref:
            return str(MUSIC / t["file"]), t["start"] if start is None else start
    if Path(ref).is_file():
        return ref, start or 0.0
    raise MediaError(f"music not found: {ref!r} (track id from `vedit.py music`, or a file path)")


def cmd_music(a):
    tracks = [t for t in music_catalog() if not a.mood or t["mood"] == a.mood]
    emit([{k: t[k] for k in ("id", "mood", "title", "author", "seconds", "start", "license")} for t in tracks], True)


def cmd_mix(a):
    import qa
    from mix import mix
    job, data = load_job(a.job)
    music, music_start = resolve_music(a.music, a.music_start)
    work = job / "work"
    picture = work / "picture.mp4"
    if not picture.exists():
        raise MediaError("compose the picture first: vedit.py compose --job ...")
    total = media.probe(picture)["duration"]
    motion = read_json(work / "motion.json")
    end_at = None
    if motion.get("endCard"):
        words = read_json(work / "cut_words.json")["words"]
        end_at = words[-1]["e"] + 0.05
    out = media.unique_path(job / f"{data['slug']}-{a.target}.mp4")
    report = mix(work, out, total, music=music, music_start=music_start or 0.0, below=a.below,
                 end_card_at=end_at, effects=not a.no_effects)
    info = media.probe(picture)
    check = qa.check(out, {"width": info["width"], "height": info["height"], "fps": info["fpsFloat"],
                           "duration": total}, work)
    check["mix"] = report
    write_json(work / f"{out.stem}-qa.json", check)
    emit(check, True)
    return 0 if check["ok"] else 1


def cmd_verify(a):
    import review
    job, _ = load_job(a.job)
    report = review.verify_cut(job / "work", a.language)
    write_json(job / "work" / "verify.json", report)
    emit(report, True)
    return 0 if report["ok"] else 1


def cmd_timeline(a):
    import review
    words = None
    if a.job:
        p = Path(a.job).resolve() / "work" / "cut_words.json"
        words = read_json(p)["words"] if p.exists() else None
    out = Path(a.out) if a.out else Path(a.file).with_name(f"{Path(a.file).stem}-timeline-{a.start:.1f}-{a.end:.1f}.png")
    emit({"timeline": str(review.timeline_view(a.file, a.start, a.end, out, words))}, True)


def cmd_reference(a):
    import review
    out = Path(a.out) if a.out else Path(a.video).with_suffix("").with_name(Path(a.video).stem + "-reference")
    emit(review.measure_reference(a.video, out, a.transcribe), True)


def cmd_safety(a):
    import review
    job, _ = load_job(a.job)
    work = job / "work"
    y = a.y
    if y is None:
        import compose
        from faces import FacePath
        info = media.probe(work / "base.mp4")
        faces = FacePath.load(work / "faces.json", info["width"], info["height"])
        caps = compose.Captions(read_json(work / "motion.json").get("captions", {}) if (work / "motion.json").exists()
                                else {}, compose.Words([]), [], info["width"], info["height"], faces)
        y = caps.y
    report = review.caption_safety(work, y)
    if a.samples is not None:
        report["styleSamples"] = str(review.style_samples(work, a.samples, y, work / "caption-styles.jpg"))
    emit(report, True)


# ---------------------------------------------------------------- entry

def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(prog="vedit", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("doctor", help="check FFmpeg, filters, model cache, fonts")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_doctor)

    s = sub.add_parser("inspect", help="read-only facts + 30 s language sample per source")
    s.add_argument("sources", nargs="+")
    s.add_argument("--no-language", action="store_true")
    s.set_defaults(fn=cmd_inspect)

    s = sub.add_parser("new", help="create the job folder (only after the settings card is approved)")
    s.add_argument("--dir", required=True, help="output/reels/YYYY-MM-DD-slug")
    s.add_argument("--src", nargs="+", required=True)
    s.add_argument("--title")
    s.add_argument("--slug")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("transcribe", help="word-level transcript + takes.md")
    s.add_argument("--job", required=True)
    s.add_argument("--language", help="ISO code; default auto-detect")
    s.add_argument("--prompt", help="proper names only, never a script")
    s.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_transcribe)

    s = sub.add_parser("plan", help="EDL -> measured, frame-exact segments")
    s.add_argument("--job", required=True)
    s.add_argument("--edl", required=True)
    s.set_defaults(fn=cmd_plan)

    s = sub.add_parser("captions", help="brand ASS captions (+ SRT/VTT)")
    s.add_argument("--job", required=True)
    s.add_argument("--target", default="reel", choices=["reel", "short", "youtube", "source"])
    s.add_argument("--max-words", type=int, default=3)
    s.add_argument("--mono", help="comma-separated terms set in JetBrains Mono")
    s.add_argument("--srt", action="store_true")
    s.add_argument("--vtt", action="store_true")
    s.set_defaults(fn=cmd_captions)

    s = sub.add_parser("render", help="render sample or final, then run QA")
    s.add_argument("--job", required=True)
    s.add_argument("--target", default="reel", choices=["reel", "short", "youtube", "source"])
    s.add_argument("--fit", default="crop", choices=["crop", "pad", "scale"])
    s.add_argument("--crop-x", type=float, default=0.5, help="0 = left edge, 1 = right edge")
    s.add_argument("--sample", nargs=2, type=float, metavar=("START", "END"), help="output-time window")
    s.add_argument("--no-captions", action="store_true")
    s.add_argument("--base", action="store_true", help="work/base.mp4 for compose: no captions, no versioning")
    s.add_argument("--denoise", default="off", choices=["off", "light", "strong", "auto"])
    s.add_argument("--level-takes", action="store_true", help="apply per-take gains from `audio`")
    s.add_argument("--tonemap", action="store_true", help="confirmed HDR to SDR conversion")
    s.set_defaults(fn=cmd_render)

    s = sub.add_parser("qa", help="checks on any exported file")
    s.add_argument("file")
    s.add_argument("--job")
    s.set_defaults(fn=cmd_qa)

    s = sub.add_parser("assets", help="download the face model, generate the sound effects")
    s.set_defaults(fn=cmd_assets)

    s = sub.add_parser("audio", help="noise/SNR, clipping and per-take levels -> work/audio_check.json")
    s.add_argument("--job", required=True)
    s.set_defaults(fn=cmd_audio)

    s = sub.add_parser("faces", help="face path on the base cut -> work/faces.json")
    s.add_argument("--job", required=True)
    s.set_defaults(fn=cmd_faces)

    s = sub.add_parser("motion", help="show work/motion.json (creates an automatic one if missing)")
    s.add_argument("--job", required=True)
    s.add_argument("--auto", action="store_true", help="overwrite with a fresh automatic plan")
    s.set_defaults(fn=cmd_motion)

    s = sub.add_parser("templates", help="animated overlay templates and their params")
    s.add_argument("--preview", help="template name: write an 8-frame preview sheet")
    s.add_argument("--params", help="JSON params for the preview")
    s.add_argument("--seconds", type=float, default=2.0)
    s.add_argument("--theme", help="JSON file: a theme object or a motion.json with one")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_templates)

    s = sub.add_parser("suggest", help="visual suggestions from the cut transcript")
    s.add_argument("--job", required=True)
    s.set_defaults(fn=cmd_suggest)

    s = sub.add_parser("compose", help="motion.json -> work/picture.mp4 + events.json")
    s.add_argument("--job", required=True)
    s.add_argument("--root", help="folder logo paths are relative to (default: cwd)")
    s.add_argument("--still", help="comma-separated output times: write stills instead of rendering")
    s.set_defaults(fn=cmd_compose)

    s = sub.add_parser("mix", help="picture + voice + effects + music -> final, then QA")
    s.add_argument("--job", required=True)
    s.add_argument("--target", default="reel", choices=["reel", "short", "youtube", "source"])
    s.add_argument("--music", help="track id from `vedit.py music`, or a file path")
    s.add_argument("--music-start", type=float, help="seconds into the track (default: the track's catalog start)")
    s.add_argument("--below", type=float, default=18.0, help="music LU under the voice")
    s.add_argument("--no-effects", action="store_true")
    s.set_defaults(fn=cmd_mix)

    s = sub.add_parser("music", help="CC0 tracks bundled with the skill")
    s.add_argument("--mood", choices=["calm", "chill-beat", "emotional", "groove", "hiphop", "upbeat"])
    s.set_defaults(fn=cmd_music)

    s = sub.add_parser("verify", help="re-transcribe the cut: clipped words, long silences, junction sheet")
    s.add_argument("--job", required=True)
    s.add_argument("--language")
    s.set_defaults(fn=cmd_verify)

    s = sub.add_parser("timeline", help="filmstrip + waveform + words PNG for a range")
    s.add_argument("file")
    s.add_argument("start", type=float)
    s.add_argument("end", type=float)
    s.add_argument("--job")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_timeline)

    s = sub.add_parser("reference", help="measure a reference video's editing language")
    s.add_argument("video")
    s.add_argument("--out")
    s.add_argument("--transcribe", action="store_true")
    s.set_defaults(fn=cmd_reference)

    s = sub.add_parser("safety", help="existing text under the caption band; optional style samples")
    s.add_argument("--job", required=True)
    s.add_argument("--y", type=float)
    s.add_argument("--samples", type=float, metavar="TIME", help="render caption style samples at TIME")
    s.set_defaults(fn=cmd_safety)

    a = p.parse_args(argv)
    try:
        return a.fn(a) or 0
    except (MediaError, ValueError, KeyError, OSError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
