"""Animated overlays in the brand's monochrome. Each template draws ONE frame at local time `t`.

    render(t, params, width) -> RGBA float array (or None while invisible)
    events(params) -> [(local_time, sound_kind)]   impact frames for the sound plan

`params["times"]` (seconds after the item starts, already resolved from spoken words) drive
per-element reveals; without them elements are staggered. Values must come from the recording:
a template never invents a number, a name or a result.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import ImageDraw

import draw as D

REGISTRY = {}


def template(name, when, params):
    def wrap(fn):
        REGISTRY[name] = {"fn": fn, "when": when, "params": params}
        return fn
    return wrap


def _theme(p):
    if p.get("theme", "dark") == "dark":
        return {"card": D.C("dark"), "ink": D.C("inkLight"), "dim": D.C("dim"), "track": D.C("track"),
                "accent": D.C("accent"), "on_accent": D.C("dark")}
    return {"card": D.C("light"), "ink": D.C("inkDark"), "dim": D.C("dimOnLight"), "track": D.C("trackOnLight"),
            "accent": D.C("accentOnLight"), "on_accent": D.C("inkLight")}


def _times(p, n, start=0.15, gap=0.45):
    t = list(p.get("times") or [])
    while len(t) < n:
        t.append((t[-1] + gap) if t else start)
    return t[:n]


def _entrance(im, t, delay=0.0):
    """Whole card: pop 0.9 -> 1 and fade in over ~0.3 s."""
    a = D.arr(im)
    s = 0.9 + 0.1 * D.spring(t - delay)
    a = D.scaled(a, s)
    a[..., 3] *= D.clamp((t - delay) / 0.15)
    return a


def _fmt(v, decimals, sep):
    s = f"{v:,.{decimals}f}"
    if sep == ".":                       # pt-BR / es: 1.234,5
        s = s.replace(",", "_").replace(".", ",").replace("_", ".")
    return s


# ---------------------------------------------------------------- counter

@template("counter", "A spoken number, price, percentage or count that should land hard.",
          {"value": "number (required, as spoken)", "prefix": "e.g. R$, $", "suffix": "e.g. %, x, k",
           "label": "short caption under the number", "decimals": "int", "sep": "',' or '.' thousands",
           "duration": "count time s (1.0)"})
def counter(t, p, width):
    th = _theme(p)
    dur = float(p.get("duration", 1.0))
    v = float(p["value"]) * D.EASE(t / dur)
    num = f"{p.get('prefix', '')}{_fmt(v, int(p.get('decimals', 0)), p.get('sep', ','))}{p.get('suffix', '')}"
    final = f"{p.get('prefix', '')}{_fmt(float(p['value']), int(p.get('decimals', 0)), p.get('sep', ','))}{p.get('suffix', '')}"
    f = D.font(150, "bold")
    lf = D.font(46)
    w = int(max(f.getlength(final), lf.getlength(p.get("label", ""))) + 120)
    h = 230 + (80 if p.get("label") else 0)
    im = D.card(w, h, th["card"], 28)
    d = ImageDraw.Draw(im)
    d.text((w / 2, 125), num, font=f, fill=th["ink"], anchor="mm")
    if p.get("label"):
        d.text((w / 2, 250), p["label"], font=lf, fill=th["dim"], anchor="mm")
    return _entrance(im, t)


counter.events = lambda p: [(0.0, "pop")] + [(float(p.get("duration", 1.0)), "success")]


# ---------------------------------------------------------------- steps

@template("steps", "An ordered process of 2-4 steps said in sequence (first, then, finally).",
          {"items": "list of 2-4 short names", "times": "reveal time per step", "vertical": "bool"})
def steps(t, p, width):
    th = _theme(p)
    items = p["items"][:4]
    n = len(items)
    times = _times(p, n)
    w, h = width - 120, 420
    im = D.card(w, h, th["card"], 28)
    d = ImageDraw.Draw(im)
    margin = 150                                  # room for a centered label under the end circles
    gap = (w - 2 * margin) / max(n - 1, 1)
    cy, r = 150, 56
    nf, lf = D.font(56, "bold"), D.font(38)
    for i, name in enumerate(items):
        cx = margin + i * gap if n > 1 else w / 2
        on = t >= times[i]
        if i:   # arrow from the previous step draws during the 0.3 s before this one
            px = margin + (i - 1) * gap + r + 12
            qx = cx - r - 12
            k = D.clamp((t - (times[i] - 0.3)) / 0.3)
            d.line([(px, cy), (qx, cy)], fill=th["track"], width=6)
            if k > 0:
                ex = px + (qx - px) * D.EASE(k)
                d.line([(px, cy), (ex, cy)], fill=th["accent"], width=6)
                if k >= 1:
                    d.polygon([(qx, cy), (qx - 22, cy - 14), (qx - 22, cy + 14)], fill=th["accent"])
        s = D.spring(t - times[i]) if on else 0
        rr = r * (0.8 + 0.2 * s) if on else r
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=th["accent"] if on else th["track"])
        d.text((cx, cy), str(i + 1), font=nf, fill=th["on_accent"] if on else th["dim"], anchor="mm")
        if on:
            k = D.EASE((t - times[i]) / 0.35)
            for j, line in enumerate(D.wrap(name, lf, min(gap - 10, 2 * margin - 20) if n > 1 else w - 80)[:2]):
                d.text((cx, cy + r + 50 + j * 46 + 20 * (1 - k)), line, font=lf,
                       fill=D.mix(th["ink"], th["card"], k), anchor="mm")
    return _entrance(im, t, 0.0)


steps.events = lambda p: [(x, "pop") for x in _times(p, len(p["items"][:4]))]


# ---------------------------------------------------------------- checklist

@template("checklist", "A list of 2-5 items/benefits said one after the other.",
          {"title": "optional heading", "items": "list of short items", "times": "reveal time per item"})
def checklist(t, p, width):
    th = _theme(p)
    items = p["items"][:5]
    times = _times(p, len(items))
    tf, f = D.font(52, "bold"), D.font(50)
    w = width - 120
    top = 110 if p.get("title") else 50
    row = 108
    h = top + row * len(items) + 30
    im = D.card(w, h, th["card"], 28)
    d = ImageDraw.Draw(im)
    if p.get("title"):
        d.text((50, 70), p["title"], font=tf, fill=th["ink"], anchor="lm")
    for i, item in enumerate(items):
        y = top + row * i + row / 2
        k = D.EASE((t - times[i]) / 0.4)
        r = 30
        d.ellipse((50, y - r, 50 + 2 * r, y + r), outline=th["dim"], width=4)
        if k > 0:
            c = D.clamp((t - times[i] - 0.1) / 0.25)
            d.ellipse((50, y - r, 50 + 2 * r, y + r), fill=th["accent"])
            pts = [(50 + 17, y + 2), (50 + 27, y + 12), (50 + 45, y - 11)]
            seg = pts[:2] if c < 0.5 else pts
            if c > 0:
                d.line(seg, fill=th["on_accent"], width=7, joint="curve")
            d.text((50 + 2 * r + 30 + 40 * (1 - k), y), item, font=f,
                   fill=D.mix(th["ink"], th["card"], k), anchor="lm")
    return _entrance(im, t)


checklist.events = lambda p: [(x + 0.1, "click") for x in _times(p, len(p["items"][:5]))]


# ---------------------------------------------------------------- strikeout

@template("strikeout", "Things being rejected or negated in a list (not X, not Y).",
          {"title": "optional heading", "items": "list", "times": "time each item is crossed"})
def strikeout(t, p, width):
    th = _theme(p)
    items = p["items"][:5]
    times = _times(p, len(items), 0.4, 0.5)
    f = D.font(54)
    w = width - 120
    top = 110 if p.get("title") else 40
    row = 100
    h = top + row * len(items) + 30
    im = D.card(w, h, th["card"], 28)
    d = ImageDraw.Draw(im)
    if p.get("title"):
        d.text((50, 70), p["title"], font=D.font(52, "bold"), fill=th["ink"], anchor="lm")
    for i, item in enumerate(items):
        y = top + row * i + row / 2
        k = D.EASE((t - times[i]) / 0.3)
        col = th["ink"] if k <= 0 else tuple(int(a + (b - a) * k) for a, b in zip(th["ink"], th["dim"]))
        d.text((50, y), item, font=f, fill=col, anchor="lm")
        if k > 0:
            tw = f.getlength(item)
            d.line([(40, y + 4), (40 + (tw + 20) * k, y + 4)], fill=th["accent"], width=8)
    return _entrance(im, t)


strikeout.events = lambda p: [(x, "swish") for x in _times(p, len(p["items"][:5]), 0.4, 0.5)]


# ---------------------------------------------------------------- bar chart

@template("bar_chart", "2-6 spoken values to compare (before/after, tools, costs).",
          {"bars": "[{label, value}]", "highlight": "index of the bar to emphasize", "suffix": "unit",
           "prefix": "", "title": "optional", "times": "start time per bar", "decimals": "int"})
def bar_chart(t, p, width):
    th = _theme(p)
    bars = p["bars"][:6]
    n = len(bars)
    times = _times(p, n, 0.2, 0.25)
    hi = p.get("highlight", n - 1)
    w, h = width - 120, 760
    top = 120 if p.get("title") else 60
    im = D.card(w, h, th["card"], 28)
    d = ImageDraw.Draw(im)
    if p.get("title"):
        d.text((50, 70), p["title"], font=D.font(52, "bold"), fill=th["ink"], anchor="lm")
    vmax = max(float(b["value"]) for b in bars) or 1
    base = h - 120
    span = base - top - 90
    slot = (w - 100) / n
    bw = slot * 0.62
    vf, lf = D.font(42, "bold"), D.font(36)
    d.line([(50, base), (w - 50, base)], fill=th["track"], width=4)
    for i, b in enumerate(bars):
        k = D.EASE((t - times[i]) / 0.6)
        if k <= 0:
            continue
        x0 = 50 + i * slot + (slot - bw) / 2
        bh = max(span * float(b["value"]) / vmax * k, 2)
        col = th["accent"] if i == hi else th["dim"]
        d.rounded_rectangle((x0, base - bh, x0 + bw, base), radius=12, fill=col)
        val = f"{p.get('prefix', '')}{_fmt(float(b['value']) * k, int(p.get('decimals', 0)), p.get('sep', ','))}{p.get('suffix', '')}"
        d.text((x0 + bw / 2, base - bh - 34), val, font=vf, fill=th["ink"], anchor="mm")
        d.text((x0 + bw / 2, base + 50), b["label"], font=lf, fill=th["ink"] if i == hi else th["dim"], anchor="mm")
    return _entrance(im, t)


bar_chart.events = lambda p: [(x, "pop") for x in _times(p, len(p["bars"][:6]), 0.2, 0.25)]


# ---------------------------------------------------------------- line chart

@template("line_chart", "A trend over time (growth, latency drop, cost curve).",
          {"points": "list of numbers", "labels": "optional x labels (first/last shown)",
           "title": "optional", "suffix": "unit for the end value", "duration": "draw time s (1.2)"})
def line_chart(t, p, width):
    th = _theme(p)
    pts = [float(v) for v in p["points"]]
    dur = float(p.get("duration", 1.2))
    w, h = width - 120, 680
    top = 120 if p.get("title") else 70
    im = D.card(w, h, th["card"], 28)
    d = ImageDraw.Draw(im)
    if p.get("title"):
        d.text((50, 70), p["title"], font=D.font(52, "bold"), fill=th["ink"], anchor="lm")
    lo, hi_v = min(pts), max(pts)
    rng = (hi_v - lo) or 1
    x0, x1, y0, y1 = 70, w - 170, top + 40, h - 100
    xy = [(x0 + (x1 - x0) * i / (len(pts) - 1), y1 - (y1 - y0) * (v - lo) / rng) for i, v in enumerate(pts)]
    for gy in np.linspace(y0, y1, 4):
        d.line([(x0, gy), (x1, gy)], fill=th["track"], width=2)
    k = D.EASE(t / dur)
    total = len(xy) - 1
    upto = k * total
    seg = [xy[0]]
    for i in range(1, len(xy)):
        if i <= upto:
            seg.append(xy[i])
        else:
            r = upto - (i - 1)
            if r > 0:
                seg.append((xy[i - 1][0] + (xy[i][0] - xy[i - 1][0]) * r, xy[i - 1][1] + (xy[i][1] - xy[i - 1][1]) * r))
            break
    if len(seg) > 1:
        d.line(seg, fill=th["accent"], width=9, joint="curve")
    ex, ey = seg[-1]
    d.ellipse((ex - 14, ey - 14, ex + 14, ey + 14), fill=th["accent"])
    if k >= 0.98:
        end = f"{_fmt(pts[-1], int(p.get('decimals', 0)), p.get('sep', ','))}{p.get('suffix', '')}"
        d.text((ex + 26, ey), end, font=D.font(46, "bold"), fill=th["ink"], anchor="lm")
    labels = p.get("labels") or []
    if labels:
        lf = D.font(34)
        d.text((x0, h - 50), str(labels[0]), font=lf, fill=th["dim"], anchor="lm")
        d.text((x1, h - 50), str(labels[-1]), font=lf, fill=th["dim"], anchor="rm")
    return _entrance(im, t)


line_chart.events = lambda p: [(0.0, "whoosh"), (float(p.get("duration", 1.2)), "pop")]


# ---------------------------------------------------------------- progress bar

@template("progress_bar", "A percentage of completion, coverage or share.",
          {"value": "0-100", "label": "text above the bar", "duration": "fill time s (1.0)"})
def progress_bar(t, p, width):
    th = _theme(p)
    dur = float(p.get("duration", 1.0))
    v = float(p["value"]) * D.EASE(t / dur)
    w, h = width - 120, 250
    im = D.card(w, h, th["card"], 28)
    d = ImageDraw.Draw(im)
    d.text((50, 70), p.get("label", ""), font=D.font(46), fill=th["ink"], anchor="lm")
    d.text((w - 50, 70), f"{v:.0f}%", font=D.font(56, "bold"), fill=th["ink"], anchor="rm")
    d.rounded_rectangle((50, 140, w - 50, 190), radius=25, fill=th["track"])
    fw = (w - 100) * v / 100
    if fw > 4:
        d.rounded_rectangle((50, 140, 50 + fw, 190), radius=25, fill=th["accent"])
    return _entrance(im, t)


progress_bar.events = lambda p: [(0.0, "riser"), (float(p.get("duration", 1.0)), "pop")]


# ---------------------------------------------------------------- impact word

@template("impact_word", "1-4 punchy words that should slam on screen (the hook, the verdict).",
          {"words": "list of 1-4 words", "times": "slam time per word"})
def impact_word(t, p, width):
    words = [w.upper() for w in p["words"][:4]]
    times = _times(p, len(words), 0.0, 0.3)
    f = D.font(150, "bold")
    lines = [w for i, w in enumerate(words) if t >= times[i] - 0.12]
    if not lines:
        return None
    lh = 165
    w = int(max(f.getlength(x) for x in words) + 80)
    h = lh * len(words) + 40
    im = D.layer(w, h)
    d = ImageDraw.Draw(im)
    for i, word in enumerate(words):
        dt = t - times[i]
        if dt < -0.12:
            continue
        fall = D.clamp((dt + 0.12) / 0.12)                       # falls in for 0.12 s, lands at times[i]
        s = 1.6 - 0.6 * fall ** 2
        squash = 1 + 0.12 * math.exp(-18 * max(dt, 0)) * math.sin(30 * max(dt, 0)) if dt >= 0 else 1
        fs = max(int(150 * s * squash), 10)
        fi = D.font(fs, "bold")
        d.text((w / 2, 20 + lh * i + lh / 2), word, font=fi, fill=D.C("inkLight") + (int(255 * min(fall * 1.5, 1)),),
               anchor="mm", stroke_width=10, stroke_fill=D.C("dark") + (int(255 * fall),))
    a = D.arr(im)
    last = max((x for x in times if x <= t), default=None)
    if last is not None and t - last < 0.25:                    # shake on landing
        e = math.exp(-14 * (t - last))
        a = np.roll(a, int(14 * e * math.sin(80 * (t - last))), axis=1)
    return a


impact_word.events = lambda p: [(x, "impact") for x in _times(p, len(p["words"][:4]), 0.0, 0.3)]


# ---------------------------------------------------------------- label (lower third)

@template("label", "Name a tool, concept or section: mono kicker + title (lower third).",
          {"kicker": "UPPERCASE mono label, e.g. STACK", "title": "short title"})
def label(t, p, width):
    kf, tf = D.font(34, "mono"), D.font(64, "bold")
    kicker, title = p.get("kicker", "").upper(), p["title"]
    w = int(max(kf.getlength(kicker), tf.getlength(title)) + 100)
    h = 200 if kicker else 130
    k = D.EASE(t / 0.45)
    im = D.card(w, h, D.C("dark"), 18)
    d = ImageDraw.Draw(im)
    y = 60
    if kicker:
        d.text((50, y), kicker, font=kf, fill=D.C("dim"), anchor="lm")
        y += 75
    d.text((50, y), title, font=tf, fill=D.C("inkLight"), anchor="lm")
    a = D.arr(im)
    cut = int(w * k)                                            # wipes in from the left
    a[:, cut:, 3] = 0
    return a


label.events = lambda p: [(0.0, "swish")]


# ---------------------------------------------------------------- notification

@template("notification", "A message/alert arriving (an alert fired, a client wrote, a job failed).",
          {"app": "generic source name (no real brand)", "title": "bold line", "body": "text line"})
def notification(t, p, width):
    w, h = width - 120, 210
    im = D.card(w, h, D.C("light"), 36, 245)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 45, 120, 125), radius=20, fill=D.C("accentOnLight"))
    d.text((80, 85), (p.get("app") or "!")[:1].upper(), font=D.font(46, "bold"), fill=D.C("inkLight"), anchor="mm")
    d.text((150, 62), (p.get("app") or "").upper(), font=D.font(28, "mono"), fill=D.C("dimOnLight"), anchor="lm")
    d.text((150, 108), p["title"], font=D.font(44, "bold"), fill=D.C("inkDark"), anchor="lm")
    if p.get("body"):
        d.text((150, 160), p["body"], font=D.font(38), fill=D.C("dimOnLight"), anchor="lm")
    a = D.arr(im)
    k = D.spring(t)                                             # drops from above
    pad = np.zeros((h + 200, w, 4), np.float32)
    off = int((1 - k) * -220) + 100
    y0 = max(off, 0)
    src = a[max(-off, 0):]
    pad[y0:y0 + src.shape[0]] = src[:pad.shape[0] - y0]
    return pad


notification.events = lambda p: [(0.1, "notification")]


# ---------------------------------------------------------------- comment CTA

@template("comment_cta", "Ask viewers to comment a keyword.",
          {"keyword": "word to type", "placeholder": "Add a comment..."})
def comment_cta(t, p, width):
    kw = p["keyword"]
    w, h = width - 120, 150
    im = D.card(w, h, D.C("light"), 75, 250)
    d = ImageDraw.Draw(im)
    d.ellipse((25, 25, 125, 125), fill=D.C("trackOnLight"))
    d.ellipse((60, 45, 90, 75), fill=D.C("line"))
    d.pieslice((45, 80, 105, 140), 180, 360, fill=D.C("line"))
    typed = int(D.clamp((t - 0.3) / max(0.08 * len(kw), 0.2)) * len(kw))
    room = w - 160 - 150                                  # between the avatar and the send button
    longest = max([kw, p.get("placeholder", "Add a comment...")], key=len)
    size = 52
    while size > 28 and D.font(size).getlength(longest) > room:
        size -= 2
    f = D.font(size)
    if typed:
        d.text((160, h / 2), kw[:typed], font=f, fill=D.C("inkDark"), anchor="lm")
        cx = 160 + f.getlength(kw[:typed]) + 6
    else:
        d.text((160, h / 2), p.get("placeholder", "Add a comment..."), font=f, fill=D.C("dimOnLight"), anchor="lm")
        cx = 160
    if int(t * 2.5) % 2 == 0 and typed < len(kw):
        d.line([(cx, h / 2 - 30), (cx, h / 2 + 30)], fill=D.C("inkDark"), width=4)
    sent = t > 0.45 + 0.08 * len(kw)
    r = 48 * (1 + 0.15 * math.exp(-10 * max(t - 0.45 - 0.08 * len(kw), 0)) if sent else 1)
    bx = w - 85
    d.ellipse((bx - r, h / 2 - r, bx + r, h / 2 + r), fill=D.C("accentOnLight") if sent else D.C("line"))
    d.polygon([(bx - 18, h / 2 - 20), (bx + 24, h / 2), (bx - 18, h / 2 + 20), (bx - 8, h / 2)], fill=D.C("inkLight"))
    return _entrance(im, t)


comment_cta.events = lambda p: [(0.3 + 0.08 * i, "type") for i in range(len(p["keyword"]))] + \
    [(0.45 + 0.08 * len(p["keyword"]), "click")]


# ---------------------------------------------------------------- highlight

@template("highlight", "Point at something already on screen (a number on a slide, a line of code).",
          {"target": "[x, y, w, h] in output px", "shape": "circle | underline | arrow", "note": "optional"})
def highlight(t, p, width, height=1920):
    x, y, w, h = p["target"]
    k = D.EASE(t / 0.5)
    im = D.layer(width, height)
    d = ImageDraw.Draw(im)
    shape = p.get("shape", "circle")
    if shape == "circle":
        cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2 + 30, h / 2 + 30
        pts = [(cx + rx * math.cos(a), cy + ry * math.sin(a))
               for a in np.linspace(-2.2, -2.2 + 2 * math.pi * 1.05 * k, max(int(80 * k), 2))]
        d.line(pts, fill=D.C("accent"), width=10, joint="curve")
    elif shape == "underline":
        d.line([(x, y + h + 14), (x + w * k, y + h + 14)], fill=D.C("accent"), width=10)
    else:
        sx, sy = x + w + 160, y + h + 160
        ex, ey = sx + (x + w + 20 - sx) * k, sy + (y + h + 20 - sy) * k
        d.line([(sx, sy), (ex, ey)], fill=D.C("accent"), width=10)
        if k > 0.95:
            d.polygon([(ex, ey), (ex + 40, ey + 8), (ex + 8, ey + 40)], fill=D.C("accent"))
    if p.get("note") and k > 0.9:
        d.text((x, y + h + 60), p["note"], font=D.font(48, "bold"), fill=D.C("accent"),
               stroke_width=6, stroke_fill=D.C("dark"))
    return D.arr(im)


highlight.events = lambda p: [(0.0, "swish")]
highlight.fullframe = True


def render(name, t, params, width):
    return REGISTRY[name]["fn"](t, params, width)


def events(name, params):
    return REGISTRY[name]["fn"].events(params)


def describe():
    return {k: {"when": v["when"], "params": v["params"]} for k, v in REGISTRY.items()}
