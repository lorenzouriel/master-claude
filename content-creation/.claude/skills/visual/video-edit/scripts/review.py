"""Review tools: cut verification, timeline images, reference measurement, visual suggestions,
caption safety. Everything is measured on the actual media; findings are review candidates."""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from cutplan import HOP, SR, Envelope
from media import load_audio, probe, run


def _norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"[^\w]", "", "".join(c for c in s if not unicodedata.combining(c)))


def _frames(video, times, width):
    out = []
    for t in times:
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", str(video), "-frames:v", "1",
                            "-vf", f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        if r.stdout:
            from io import BytesIO
            out.append(Image.open(BytesIO(r.stdout)).convert("RGB"))
        else:
            out.append(Image.new("RGB", (width, int(width * 16 / 9)), D.NEAR))
    return out


# ---------------------------------------------------------------- cut verification

def verify_cut(work: Path, language=None) -> dict:
    """Re-transcribe the rendered cut and compare with the words the plan meant to keep."""
    from transcribe import transcribe
    plan = json.loads((work / "plan.json").read_text(encoding="utf-8"))
    meant = json.loads((work / "cut_words.json").read_text(encoding="utf-8"))["words"]
    heard = transcribe(work / "cut_audio.wav", language=language)["words"]
    a, b = [_norm(w["w"]) for w in meant], [_norm(w["w"]) for w in heard]
    joins = [s["outStart"] for s in plan["segments"][1:]]
    findings = []
    for op, i0, i1, j0, j1 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        t = meant[i0]["s"] if i0 < len(meant) else (heard[j0]["s"] if j0 < len(heard) else 0)
        near = min(joins, key=lambda j: abs(j - t)) if joins else None
        findings.append({"t": round(t, 2), "type": op,
                         "meant": " ".join(w["w"] for w in meant[i0:i1]),
                         "heard": " ".join(w["w"] for w in heard[j0:j1]),
                         "nearJoin": round(near, 2) if near is not None and abs(near - t) < 0.4 else None})
    audio = load_audio(work / "cut_audio.wav", SR)
    env = Envelope(audio, meant)
    quiet = env.db < env.weak
    silences, run_start = [], None
    for i, q in enumerate(np.append(quiet, False)):
        if q and run_start is None:
            run_start = i
        elif not q and run_start is not None:
            if (i - run_start) * HOP >= 0.7:
                silences.append([round(run_start * HOP, 2), round(i * HOP, 2)])
            run_start = None
    sheet = junction_sheet(work, joins)
    clipped = [f for f in findings if f["nearJoin"] is not None]
    return {"wordsMeant": len(a), "wordsHeard": len(b),
            "match": round(difflib.SequenceMatcher(a=a, b=b).ratio(), 3),
            "findings": findings, "suspectedClippedAtJoin": clipped,
            "longSilences": silences, "junctionSheet": str(sheet) if sheet else None,
            "ok": not clipped and not silences}


def junction_sheet(work: Path, joins, video=None):
    video = video or (work / "base.mp4")
    if not joins or not video.exists():
        return None
    rows = []
    for j in joins[:12]:
        a, b = _frames(video, [j - 0.1, j + 0.05], 240)
        row = Image.new("RGB", (500, a.height + 40), D.WHITE)
        row.paste(a, (0, 40))
        row.paste(b, (260, 40))
        ImageDraw.Draw(row).text((10, 8), f"join {j:.2f}s  before | after", font=D.font(24, "mono"), fill=D.NEAR)
        rows.append(row)
    sheet = Image.new("RGB", (500 * min(len(rows), 4), rows[0].height * ((len(rows) + 3) // 4)), D.WHITE)
    for k, r in enumerate(rows):
        sheet.paste(r, ((k % 4) * 500, (k // 4) * r.height))
    path = work / "junctions.jpg"
    sheet.save(path, quality=88)
    return path


# ---------------------------------------------------------------- timeline view

def timeline_view(video, start, end, out: Path, words=None, frames=8) -> Path:
    """Filmstrip + waveform + words for one range: timing you can see, not guess."""
    dur = end - start
    times = [start + dur * (k + 0.5) / frames for k in range(frames)]
    imgs = _frames(video, times, 200)
    fw, fh = imgs[0].size
    W = fw * frames
    wave_h, words_h = 220, 90
    canvas = Image.new("RGB", (W, fh + wave_h + words_h + 40), D.WHITE)
    for k, im in enumerate(imgs):
        canvas.paste(im, (k * fw, 0))
    d = ImageDraw.Draw(canvas)
    audio = load_audio(video, SR, start, dur)
    y0 = fh + 20
    if audio.size:
        cols = np.array_split(audio, W)
        peak = np.array([np.abs(c).max() if c.size else 0 for c in cols])
        rms = np.array([np.sqrt(np.mean(c ** 2)) if c.size else 0 for c in cols])
        mid = y0 + wave_h / 2
        hop = int(SR * HOP)
        db = 20 * np.log10(np.sqrt(np.convolve(audio ** 2, np.ones(hop) / hop, mode="same")[::hop]) + 1e-9)
        for i, q in enumerate(db < -35):
            if q:
                x = int(i * HOP / dur * W)
                d.line([(x, y0), (x, y0 + wave_h)], fill=D.LIGHT)
        for x in range(W):
            d.line([(x, mid - peak[x] * wave_h / 2), (x, mid + peak[x] * wave_h / 2)], fill=D.STROKE)
            d.line([(x, mid - rms[x] * wave_h), (x, mid + rms[x] * wave_h)], fill=D.NEAR)
    if words:
        f = D.font(22)
        for k, w in enumerate(w for w in words if start <= w["s"] < end):
            x = (w["s"] - start) / dur * W
            d.line([(x, y0), (x, y0 + wave_h)], fill=D.GREY)
            d.text((x + 3, y0 + wave_h + 10 + (k % 2) * 32), w["w"], font=f, fill=D.NEAR)
    for k in range(int(dur * 2) + 1):
        x = k * 0.5 / dur * W
        d.text((x + 2, canvas.height - 26), f"{start + k * 0.5:.1f}", font=D.font(18, "mono"), fill=D.MID)
    canvas.save(out, quality=90)
    return out


# ---------------------------------------------------------------- reference measurement

def measure_reference(video, out_dir: Path, transcribe_speech=False) -> dict:
    """Editing language of a reference: cut pace, camera zooms, text bands, palette, loudness, end card."""
    import cv2
    out_dir.mkdir(parents=True, exist_ok=True)
    info = probe(video)
    dur, W, H = info["duration"], info["width"], info["height"]
    # Shot changes
    err = run(["ffmpeg", "-hide_banner", "-i", str(video), "-vf", "scale=320:-2,scdet=threshold=12",
               "-f", "null", "-"], check=False).stderr
    cuts = [round(float(x), 2) for x in re.findall(r"lavfi\.scd\.time:\s*([\d.]+)", err)]
    shots = np.diff([0.0] + cuts + [dur])
    # Camera scale per sample (5 fps) from feature matches between consecutive frames
    sw = 360
    sh = int(round(H * sw / W / 2) * 2)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps=5,scale={sw}:{sh},format=gray",
                             "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    orb = cv2.ORB_create(600)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    prev, scales, text_rows, bright = None, [], np.zeros(20), []
    n = 0
    while True:
        buf = proc.stdout.read(sw * sh)
        if len(buf) < sw * sh:
            break
        g = np.frombuffer(buf, np.uint8).reshape(sh, sw)
        bright.append(float(g.mean()))
        grad = cv2.morphologyEx(g, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
        _, bw = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3)))
        cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if w > sw * 0.25 and 8 < h < sh * 0.08 and w / h > 3:      # wide, short blobs read like text lines
                text_rows[min(int((y + h / 2) / sh * 20), 19)] += 1
        s = 1.0
        if prev is not None:
            k1, d1 = orb.detectAndCompute(prev, None)
            k2, d2 = orb.detectAndCompute(g, None)
            if d1 is not None and d2 is not None and len(k1) > 20 and len(k2) > 20:
                m = bf.match(d1, d2)
                if len(m) > 20:
                    p1 = np.float32([k1[x.queryIdx].pt for x in m])
                    p2 = np.float32([k2[x.trainIdx].pt for x in m])
                    A, _ = cv2.estimateAffinePartial2D(p1, p2)
                    if A is not None:
                        s = float(np.hypot(A[0, 0], A[1, 0]))
        scales.append(s)
        prev = g
        n += 1
    proc.wait()
    cum = np.cumprod(scales) if scales else np.array([1.0])
    zoom_events, last = [], -9
    for i in range(3, len(cum)):
        ch = cum[i] / cum[i - 3] - 1
        if abs(ch) > 0.03 and i / 5 - last > 0.8 and not any(abs(i / 5 - c) < 0.4 for c in cuts):
            zoom_events.append({"t": round(i / 5, 1), "dir": "in" if ch > 0 else "out", "change": round(float(ch), 3)})
            last = i / 5
    bands = (text_rows / max(n, 1)).round(2).tolist()
    # Palette from 12 frames
    imgs = _frames(video, [dur * (k + 0.5) / 12 for k in range(12)], 120)
    px = np.concatenate([np.asarray(im).reshape(-1, 3) for im in imgs]).astype(np.float32)
    _, lab, centers = cv2.kmeans(px, 6, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0), 3,
                                 cv2.KMEANS_PP_CENTERS)
    share = np.bincount(lab.ravel(), minlength=6) / len(lab)
    palette = [{"hex": "#%02X%02X%02X" % tuple(int(v) for v in c), "share": round(float(s), 3)}
               for c, s in sorted(zip(centers, share), key=lambda x: -x[1])]
    sheet = out_dir / "reference-contact.jpg"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf",
         f"fps={16 / max(dur, 1):.4f},scale=180:-2,tile=8x2:padding=4:color=white", "-frames:v", "1", sheet])
    loud = re.search(r"I:\s+(-?[\d.]+) LUFS", run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-af",
                                                   "ebur128", "-f", "null", "-"]).stderr.split("Summary:")[-1])
    result = {
        "file": Path(video).name, "duration": round(dur, 2), "size": f"{W}x{H}", "fps": info["fps"],
        "measured": {
            "cuts": cuts, "shotCount": len(shots), "avgShotSeconds": round(float(np.mean(shots)), 2),
            "cameraZoomEvents": zoom_events, "zoomsPerMinute": round(len(zoom_events) / dur * 60, 1),
            "textBandsTopToBottom": bands, "palette": palette,
            "loudnessLUFS": float(loud.group(1)) if loud else None,
            "endCardLikely": bool(bright and np.mean(bright[-10:]) > 200 and np.mean(bright[:-10]) < 180),
        },
        "unknown": ["fonts (not identified)", "exact easing curves", "music source"],
        "contactSheet": str(sheet),
    }
    if transcribe_speech:
        from transcribe import transcribe
        words = transcribe(video)["words"]
        result["measured"]["wordsPerMinute"] = round(len(words) / dur * 60) if dur else None
    (out_dir / "reference.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    md = [f"# Reference style: {result['file']}", "",
          f"- {result['size']}, {result['duration']} s, {info['fps']} fps",
          f"- {len(shots)} shots, average {result['measured']['avgShotSeconds']} s",
          f"- Camera zoom events: {len(zoom_events)} ({result['measured']['zoomsPerMinute']}/min): "
          + ", ".join(f"{z['t']}s {z['dir']} {z['change']:+.0%}" for z in zoom_events[:12]),
          "- Text bands (top to bottom, share of samples): " + " ".join(f"{b:.2f}" for b in bands),
          "- Palette: " + ", ".join(f"{p['hex']} {p['share']:.0%}" for p in palette),
          f"- Loudness: {result['measured']['loudnessLUFS']} LUFS",
          f"- End card likely: {result['measured']['endCardLikely']}",
          "", "Unknown: " + ", ".join(result["unknown"]) + ".",
          "Measured values are observations of this file, not rules; copy the editing language, not the content."]
    (out_dir / "reference.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return result


# ---------------------------------------------------------------- spoken numbers + suggestions

UNITS = {
    # pt
    "zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
    "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "catorze": 14, "quatorze": 14,
    "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19, "vinte": 20, "trinta": 30,
    "quarenta": 40, "cinquenta": 50, "sessenta": 60, "setenta": 70, "oitenta": 80, "noventa": 90, "cem": 100,
    "cento": 100, "duzentos": 200, "trezentos": 300, "quatrocentos": 400, "quinhentos": 500, "seiscentos": 600,
    "setecentos": 700, "oitocentos": 800, "novecentos": 900,
    # en
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
    # es
    "uno": 1, "dos": 2, "cuatro": 4, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "veinte": 20, "treinta": 30,
    "cuarenta": 40, "cincuenta": 50, "cien": 100, "ciento": 100,
}
SCALES = {"mil": 1000, "thousand": 1000, "milhao": 1e6, "milhoes": 1e6, "million": 1e6, "millon": 1e6,
          "millones": 1e6, "bilhao": 1e9, "bilhoes": 1e9, "billion": 1e9, "k": 1000}
JOIN = {"e", "and", "y"}
MONEY = {"reais", "real", "dolares", "dollars", "dolar", "dollar", "euros", "euro", "pesos", "bucks"}
PCT = {"porcento", "percent", "porciento", "%"}
ORD = {"primeiro": 1, "segundo": 2, "terceiro": 3, "quarto": 4, "first": 1, "second": 2, "third": 3,
       "fourth": 4, "primero": 1, "tercero": 3, "cuarto": 4, "primeira": 1, "segunda": 2, "terceira": 3}
CTA = {"comenta", "comente", "comentarios", "comment", "comments", "link", "segue", "siga", "follow",
       "salva", "salve", "save", "compartilha", "share", "inscreva", "subscribe"}


def parse_numbers(words):
    """Spoken numbers with their word span: [{i0, i1, value, money, percent}]."""
    toks = [_norm(w["w"]) for w in words]
    out, i = [], 0
    while i < len(toks):
        t, raw = toks[i], words[i]["w"]
        digits = re.fullmatch(r"(?:r\$|\$)?([\d.,]+)(k|%)?", raw.lower().strip("?!.,"))
        if digits and re.search(r"\d", raw):
            s = digits.group(1)
            s = s.replace(".", "").replace(",", ".") if re.search(r",\d{1,2}$", s) or s.count(".") > 1 else s.replace(",", "")
            try:
                v = float(s) * (1000 if digits.group(2) == "k" else 1)
                out.append({"i0": i, "i1": i, "value": v, "pct": digits.group(2) == "%" or "%" in raw,
                            "money": "$" in raw})
            except ValueError:
                pass
            i += 1
            continue
        if t in UNITS or t in SCALES:
            total, cur, j = 0, 0, i
            while j < len(toks) and (toks[j] in UNITS or toks[j] in SCALES or (toks[j] in JOIN and j + 1 < len(toks)
                                                                                 and toks[j + 1] in UNITS)):
                if toks[j] == "hundred":                     # "three hundred" multiplies
                    cur = max(cur, 1) * 100
                elif toks[j] in UNITS:                       # "trezentos e vinte" adds
                    cur += UNITS[toks[j]]
                elif toks[j] in SCALES:
                    total += max(cur, 1) * SCALES[toks[j]]
                    cur = 0
                j += 1
            v = total + cur
            if t not in ("um", "uma", "one", "uno") or j - i > 1:     # "um" alone is an article
                out.append({"i0": i, "i1": j - 1, "value": v, "pct": False, "money": False})
            i = j
            continue
        i += 1
    for n in out:
        nxt = " ".join(toks[n["i1"] + 1:n["i1"] + 3])
        n["pct"] = n["pct"] or any(p in nxt.replace(" ", "") for p in PCT)
        prev = toks[n["i0"] - 1] if n["i0"] else ""
        n["money"] = n["money"] or prev in ("r", "rs") or any(m in nxt.split() for m in MONEY)
    return out


def suggest(words, min_gap=6.0):
    """Template suggestions from the cut transcript, with word anchors. Values come from the speech."""
    sug = []
    toks = [_norm(w["w"]) for w in words]

    def anchor(i):
        key = toks[i]
        nth = sum(1 for t in toks[:i + 1] if t == key)
        return key if nth == 1 else f"{key}#{nth}"

    for n in parse_numbers(words):
        tmpl = "progress_bar" if n["pct"] and n["value"] <= 100 else "counter"
        params = {"value": n["value"]} if tmpl == "progress_bar" else {
            "value": n["value"], "prefix": "R$ " if n["money"] and any(t in ("reais", "real") for t in toks) else
            ("$" if n["money"] else ""), "suffix": "%" if n["pct"] else ""}
        sug.append({"t": words[n["i0"]]["s"], "template": tmpl, "at": anchor(n["i0"]), "params": params,
                    "why": f"spoken number: {' '.join(w['w'] for w in words[n['i0']:n['i1'] + 1])}"})
    ords = [i for i, t in enumerate(toks) if t in ORD]
    if len(ords) >= 2:
        sug.append({"t": words[ords[0]]["s"], "template": "steps", "at": anchor(ords[0]),
                    "params": {"items": ["<name step 1>", "<name step 2>"][:len(ords)],
                               "times": [anchor(i) for i in ords]},
                    "why": "ordinal sequence: " + ", ".join(words[i]["w"] for i in ords)})
    sent, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r"[.?!]$", w["w"]):
            sent.append(cur)
            cur = []
    if cur:
        sent.append(cur)
    for s in sent:
        text = " ".join(words[i]["w"] for i in s)
        parts = [p.strip() for p in re.split(r",|\b(?:e|and|y)\b(?= \w+[.?!]?$)", text.rstrip(".?!")) if p.strip()]
        heads = [p.split()[0].lower() for p in parts if p.split()]
        if len(parts) >= 3 and all(len(p.split()) <= 4 for p in parts):
            starts = []
            for p in parts:
                first = _norm(p.split()[0])
                idx = next((i for i in s if toks[i] == first and i not in starts), s[0])
                starts.append(idx)
            neg = sum(h in ("nao", "não", "not", "no", "sem", "without") for h in heads) >= 2
            sug.append({"t": words[s[0]]["s"], "template": "strikeout" if neg else "checklist",
                        "at": anchor(starts[0]), "params": {"items": parts, "times": [anchor(i) for i in starts]},
                        "alt": "tab scene with one card per item",
                        "why": f"list of {len(parts)} short items"})
    for i, t in enumerate(toks):
        if t in CTA:
            sug.append({"t": words[i]["s"], "template": "comment_cta" if t.startswith("coment") or t.startswith("comment")
                        else "tab", "at": anchor(i), "params": {},
                        "why": f"call to action: {words[i]['w']}"})
            break
    sug.sort(key=lambda x: x["t"])
    kept, last = [], -99
    for s in sug:
        if s["t"] - last >= min_gap or s["template"] in ("tab", "comment_cta"):
            kept.append(s)
            last = s["t"]
    return kept


# ---------------------------------------------------------------- caption safety

def caption_safety(work: Path, y: float, height: float = 1920) -> dict:
    """Existing text in the base video (2 fps) near the caption band."""
    import cv2
    video = work / "base.mp4"
    info = probe(video)
    sw = 360
    sh = int(round(info["height"] * sw / info["width"] / 2) * 2)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps=2,scale={sw}:{sh},format=gray",
                             "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    hits, n = [], 0
    band = (y / height * sh - sh * 0.05, y / height * sh + sh * 0.05)
    while True:
        buf = proc.stdout.read(sw * sh)
        if len(buf) < sw * sh:
            break
        g = np.frombuffer(buf, np.uint8).reshape(sh, sw)
        grad = cv2.morphologyEx(g, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
        _, bw = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3)))
        cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, yy, w, h = cv2.boundingRect(c)
            if w > sw * 0.25 and 8 < h < sh * 0.08 and w / h > 3 and band[0] < yy + h / 2 < band[1]:
                hits.append(round(n / 2, 1))
                break
        n += 1
    proc.wait()
    return {"captionY": y, "samples": n, "textLikeInBand": sorted(set(hits)),
            "ok": len(hits) <= max(1, n // 20)}


def style_samples(work: Path, at: float, y: float, out: Path) -> Path:
    """The caption looks the card can offer, drawn on a real frame of the cut."""
    import compose
    frame = _frames(work / "base.mp4", [at], 1080)[0]
    words = json.loads((work / "cut_words.json").read_text(encoding="utf-8"))["words"]
    cues = json.loads((work / "cues.json").read_text(encoding="utf-8"))
    cue = min(cues, key=lambda c: abs(c["start"] - at))
    tiles = []
    for style in ("pill", "box"):
        f = np.asarray(frame).copy()
        caps = compose.Captions({"style": style, "y": y}, compose.Words(words), [cue], f.shape[1], f.shape[0],
                                type("F", (), {"chin_y": lambda self: y - 110})())
        caps.draw(f, cue["start"] + 0.5)
        im = Image.fromarray(f).resize((360, 640))
        ImageDraw.Draw(im).text((12, 12), style, font=D.font(28, "mono"), fill=D.WHITE, stroke_width=3,
                                stroke_fill=D.NEAR)
        tiles.append(im)
    sheet = Image.new("RGB", (360 * len(tiles) + 8 * (len(tiles) - 1), 640), D.WHITE)
    for k, im in enumerate(tiles):
        sheet.paste(im, (k * 368, 0))
    sheet.save(out, quality=90)
    return out
