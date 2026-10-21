"""Motion compositor: camera, caption pill, tab scenes, template overlays and end card over the base cut.

Driven by work/motion.json. Times are seconds in output time or spoken-word anchors:
"professor" (first occurrence), "professor#2" (second), "professor@end" (word end).
Writes the picture (no audio) and work/events.json, the impact frames the sound mix aligns to.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

import draw as D
import templates as T
from faces import FacePath

STOP = set("""a o e é de da do das dos que em no na nos nas um uma uns umas para pra por com se eu você voce
ele ela isso esse essa aqui lá la mas mais menos the a an and of to in on is it that this you i we for with
are be or as at el la los las y en es un una por con""".split())


# ---------------------------------------------------------------- anchors

class Words:
    def __init__(self, words):
        self.words = words

    @staticmethod
    def norm(s):
        return re.sub(r"[^\w]", "", s.lower())

    def time(self, ref, default=None):
        if ref is None:
            return default
        if isinstance(ref, (int, float)):
            return float(ref)
        m = re.fullmatch(r"(.+?)(?:#(\d+))?(@end)?", str(ref).strip())
        key, nth, end = self.norm(m.group(1)), int(m.group(2) or 1), bool(m.group(3))
        hits = [w for w in self.words if self.norm(w["w"]) == key]
        if len(hits) < nth:
            raise ValueError(f"anchor not spoken: {ref!r}")
        w = hits[nth - 1]
        return w["e"] if end else w["s"]


def sentences(words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r"[.?!]$", w["w"]):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def auto_emphasis(words, spacing=1.2):
    """One stressed word per sentence: the longest content word, not the clip's first word."""
    picks, last = [], -9.0
    for sent in sentences(words):
        cands = [i for i in sent if i > 0 and len(D_clean(words[i]["w"])) >= 4
                 and D_clean(words[i]["w"]).lower() not in STOP]
        if not cands:
            continue
        i = max(cands, key=lambda j: (len(D_clean(words[j]["w"])), -j))
        if words[i]["s"] - last >= spacing:
            picks.append(i)
            last = words[i]["s"]
    return picks


def D_clean(s):
    return re.sub(r"[^\w]", "", s)


# ---------------------------------------------------------------- camera

class Camera:
    """Base zoom alternates per sentence; stressed words get a short push-in; anchor follows the face."""

    def __init__(self, cfg, words, faces, duration):
        self.faces = faces
        self.cfg = cfg
        shots = [(0.0, 1.0)]
        events = []
        if cfg.get("auto", True):
            base = cfg.get("base", [1.0, 1.08])
            for k, sent in enumerate(sentences(words.words)):
                if k:
                    shots.append((words.words[sent[0]]["s"] - 0.06, base[k % len(base)]))
        for s in cfg.get("shots", []):                       # manual shots override timing
            shots.append((words.time(s["at"]) - 0.06, float(s["zoom"])))
        shots.sort()
        self.shots = shots
        push = float(cfg.get("push", 0.07))
        emph = cfg.get("emphasis")
        if emph is None and cfg.get("auto", True):
            idx = auto_emphasis(words.words)
            emph = [(words.words[i]["s"], words.words[i]["e"]) for i in idx]
        else:
            emph = [(float(e), float(e) + 0.4) if isinstance(e, (int, float))
                    else (words.time(e), words.time(str(e).split("@")[0] + "@end"))
                    for e in (emph or [])]
        self.pushes = [(a - 0.06, max(b + 0.35, a + 0.6), push) for a, b in emph]
        for k, (a, _, _) in enumerate(self.pushes):
            events.append({"t": round(a + 0.06, 3), "kind": "swish", "level": -15 if k % 2 else -17})
        self.events = events
        self.duration = duration

    def zoom(self, t):
        k = max(i for i, (s, _) in enumerate(self.shots) if s <= t)
        start, z = self.shots[k]
        end = self.shots[k + 1][0] if k + 1 < len(self.shots) else self.duration
        z = z + 0.02 * D.clamp((t - start) / max(end - start, 0.1))        # slow drift inside a shot
        if k:
            prev = self.shots[k - 1][1]
            z = prev + (z - prev) * D.spring(t - start)
        for a, b, p in self.pushes:
            if a <= t < b + 0.6:
                up = D.spring(t - a)
                down = D.EASE((t - b) / 0.6) if t >= b else 0.0
                z += p * (up * (1 - down))
        return z

    def apply(self, frame, t):
        z = self.zoom(t)
        if abs(z - 1) < 1e-4:
            return frame
        cx, cy, _ = self.faces.at(t)
        m = np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]])
        h, w = frame.shape[:2]
        return cv2.warpAffine(frame, m, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)


# ---------------------------------------------------------------- captions

class Captions:
    def __init__(self, cfg, words, cues, width, height, faces):
        self.style = cfg.get("style", "pill")
        self.bounce = bool(cfg.get("bounce", True))
        self.words = words.words
        self.size = int(cfg.get("size", 66 if height > width else 54))
        self.f = D.font(self.size)
        self.mono = {w.lower() for term in cfg.get("mono", []) for w in term.split()}
        chin = faces.chin_y()
        default_y = min(max(chin + 110, height * 0.62), height * 0.80) if height > width else height * 0.88
        self.y = float(cfg.get("y", default_y))
        self.cx = width / 2
        self.cues, i = [], 0
        for c in cues:
            n = len(c["tokens"])
            self.cues.append((c["start"], c["end"], list(range(i, i + n)), c["tokens"]))
            i += n
        self.cache = {}

    def _img(self, idx, toks, active):
        key = (tuple(idx), active)
        if key in self.cache:
            return self.cache[key]
        f = self.f
        mono = D.font(self.size, "mono")
        fonts = [mono if (tok.lower() in self.mono or re.search(r"[_/(){}=<>`]|[a-z][A-Z]", tok)) else f for tok in toks]
        space = f.getlength(" ")
        widths = [ff.getlength(s) for ff, s in zip(fonts, toks)]
        asc, desc = f.getmetrics()
        px, py = 36, 18
        w, h = int(sum(widths) + space * (len(toks) - 1) + 2 * px), int(asc + desc + 2 * py)
        im = D.layer(w + 24, h + 24)
        d = ImageDraw.Draw(im)
        radius = h // 2 if self.style == "pill" else 10
        d.rounded_rectangle((12, 12, 12 + w, 12 + h), radius=radius, fill=D.C("dark") + (245,))
        x = 12 + px
        for j, s, sw, ff in zip(idx, toks, widths, fonts):
            if self.style != "pill":
                color = D.C("inkLight")
            else:
                color = D.C("capActive") if j == active else D.C("capIdle")
            d.text((x, 12 + py), s, font=ff, fill=color)
            x += sw + space
        self.cache[key] = D.arr(im)
        return self.cache[key]

    def draw(self, frame, t):
        if self.style == "off":
            return
        for a, b, idx, toks in self.cues:
            if a <= t < b:
                active = idx[0]
                for j in idx:
                    if j < len(self.words) and self.words[j]["s"] <= t:
                        active = j
                im = self._img(idx, toks, active)
                s = 0.82 + 0.18 * D.spring(t - a)
                if self.bounce and active != idx[0]:      # small bump when the next word lights up
                    since = t - self.words[active]["s"]
                    s *= 1 + 0.035 * np.exp(-12 * since) * np.cos(20 * since) if since < 0.4 else 1
                im = D.scaled(im, s)
                D.paste(frame, im, self.cx - im.shape[1] / 2, self.y - im.shape[0] / 2,
                        alpha=D.clamp((t - a) / 0.1))
                return


# ---------------------------------------------------------------- tab scene

ICONS = {"down", "check", "arrow", "none"}


class Tab:
    """Full-screen tab: slides up, speaker shrinks into a PiP, one card per spoken item, pushed in."""
    ENTER, EXIT, PUSH = 0.45, 0.42, 0.38
    PIP = (247, 790, 586, 1042)

    def __init__(self, cfg, words, width, height, end_default):
        self.w, self.h = width, height
        self.cards = [dict(c, t=words.time(c["at"]) - 0.12) for c in cfg["cards"]]
        self.t0 = self.cards[0]["t"]
        self.t1 = words.time(cfg.get("end"), end_default)
        self.light = cfg.get("bg", cfg.get("theme", "dark")) in ("light", "soft")
        self.bg = D.C("soft") if self.light else D.C("dark")
        self._shadow = None
        self.numbered = cfg.get("numbered", len(self.cards) > 1)
        self.events = [{"t": round(self.t0 + 0.10, 3), "kind": "whoosh", "level": -9}]
        for k, c in enumerate(self.cards):
            self.events.append({"t": round(c["t"] + (0.17 if k == 0 else 0.07), 3), "kind": "pop", "level": -13})
            if k:
                self.events.append({"t": round(c["t"] + 0.12, 3), "kind": "swish", "level": -12})
            self.events.append({"t": round(c["t"] + (0.32 if k == 0 else 0.25), 3), "kind": "click", "level": -9})
        if self.t1 < end_default - 0.05:
            self.events.append({"t": round(self.t1 + 0.10, 3), "kind": "whoosh", "level": -11})
        self._cards = {}

    def owns(self, t):
        return self.t0 <= t < self.t1 + self.EXIT

    def _chrome(self, n, active, pop):
        im = D.layer(self.w, 140)
        d = ImageDraw.Draw(im)
        L = self.light
        bar = D.C("barOnLight") if L else D.C("bar")
        d.rounded_rectangle((48, 20, self.w - 48, 124), radius=28, fill=bar)
        for k in range(3):
            cx = 104 + k * 36
            d.ellipse((cx - 11, 61, cx + 11, 83), fill=D.C("line") if L else D.mix(D.C("inkLight"), bar, 0.3))
        x = 230
        for k in range(n):
            s = pop if k == n - 1 else 1.0
            w, h = 150 * s, 64 * s
            on = k == active
            fill = (D.C("accentOnLight") if L else D.C("accent")) if on else (D.C("trackOnLight") if L else D.C("track"))
            if w > 1:
                d.rounded_rectangle((x, 72 - h / 2, x + w, 72 + h / 2), radius=h / 2, fill=fill)
                if s > 0.6:
                    ink = ((D.C("inkLight") if L else D.C("dark")) if on
                           else (D.C("dimOnLight") if L else D.C("dim")))
                    d.text((x + w / 2, 72), f"{k + 1:02d}", font=D.font(36, "mono"), fill=ink, anchor="mm")
            x += 168
        return D.arr(im)

    def _card(self, k):
        if k in self._cards:
            return self._cards[k]
        c = self.cards[k]
        f = D.font(88)
        icon = c.get("icon", "number" if self.numbered else "check")
        lines = D.wrap(c["text"], f, self.w - 340)
        asc, desc = f.getmetrics()
        disc, gap, px, py = 120, 36, 48, 48
        th = (asc + desc) * len(lines) + 12 * (len(lines) - 1)
        h = max(disc, th) + 2 * py
        w = int(px + disc + gap + max(f.getlength(l) for l in lines) + px)
        im = D.layer(self.w, h + 40)
        d = ImageDraw.Draw(im)
        x0 = (self.w - w) // 2
        ink = D.C("inkDark")
        cardfill = D.C("inkLight")                      # icon strokes on the accent disc
        d.rounded_rectangle((x0, 0, x0 + w, h), radius=24, fill=D.C("light"),
                            outline=D.C("line") if self.light else None, width=3 if self.light else 0)
        cx, cy = x0 + px + disc / 2, h / 2
        d.ellipse((cx - disc / 2, cy - disc / 2, cx + disc / 2, cy + disc / 2), fill=D.C("accentOnLight"))
        if icon == "down":
            d.line([(cx, cy - 30), (cx, cy + 28)], fill=cardfill, width=12)
            d.line([(cx - 24, cy + 4), (cx, cy + 30), (cx + 24, cy + 4)], fill=cardfill, width=12, joint="curve")
        elif icon == "arrow":
            d.line([(cx - 28, cy), (cx + 26, cy)], fill=cardfill, width=12)
            d.line([(cx + 2, cy - 24), (cx + 28, cy), (cx + 2, cy + 24)], fill=cardfill, width=12, joint="curve")
        elif icon == "number":
            d.text((cx, cy), str(k + 1), font=D.font(64, "bold"), fill=cardfill, anchor="mm")
        else:
            d.line([(cx - 27, cy + 2), (cx - 7, cy + 22), (cx + 29, cy - 19)], fill=cardfill, width=14, joint="curve")
        y = cy - th / 2
        for line in lines:
            d.text((x0 + px + disc + gap, y), line, font=f, fill=ink)
            y += asc + desc + 12
        self._cards[k] = D.arr(im)
        return self._cards[k]

    def draw(self, frame, face, t):
        p = D.EASE((t - self.t0) / self.ENTER) if t < self.t1 else 1 - D.EASE((t - self.t1) / self.EXIT)
        k = max(i for i, c in enumerate(self.cards) if c["t"] <= t) if t >= self.cards[0]["t"] else 0
        tab = np.empty((self.h, self.w, 3), np.uint8)
        tab[:] = self.bg
        pop = D.spring(t - self.cards[k]["t"]) if k else (min(D.spring(t - self.t0 - 0.1), 1.2) if t - self.t0 > 0.1 else 0.0)
        D.paste(tab, self._chrome(k + 1 if self.numbered else 1, k if self.numbered else 0, max(pop, 0.0)), 0, 120)
        u = D.SNAPPY((t - self.cards[k]["t"]) / self.PUSH) if k else 1.0
        if k and u < 1:
            D.paste(tab, self._card(k - 1), int(-self.w * u), 300)
        c, dy = D.screen_in(self._card(k), (t - self.cards[k]["t"] - (0.12 if k == 0 else 0.05)) / 0.42)
        D.paste(tab, c, int(self.w * (1 - u)), 300 + dy)
        if self.light:                                   # soft shadow under the PiP on a light tab
            if self._shadow is None:
                from PIL import ImageFilter
                x, y, w, h = self.PIP
                im = D.layer(self.w, self.h)
                ImageDraw.Draw(im).rounded_rectangle((x + 16, y + 24, x + w - 16, y + h + 24), radius=32,
                                                     fill=D.C("dark") + (90,))
                self._shadow = D.arr(im.filter(ImageFilter.GaussianBlur(24)))
            D.paste(tab, self._shadow, 0, 0)
        off = int(round(self.h * (1 - p)))
        if off < self.h:
            frame[off:] = tab[:self.h - off]
        x, y, w, h = self.PIP
        rx, ry = int(x * p), int(y * p)
        rw, rh = int(round(self.w + (w - self.w) * p)), int(round(self.h + (h - self.h) * p))
        small = cv2.resize(face, (rw, rh), interpolation=cv2.INTER_AREA)
        m = D.rounded_mask(rw, rh, int(32 * p) + 1)
        roi = frame[ry:ry + rh, rx:rx + rw].astype(np.float32)
        frame[ry:ry + rh, rx:rx + rw] = (small * m + roi * (1 - m)).astype(np.uint8)


# ---------------------------------------------------------------- overlays

class Overlay:
    def __init__(self, cfg, words, width, height, faces, duration):
        self.name = cfg["template"]
        if self.name not in T.REGISTRY:
            raise ValueError(f"unknown template {self.name!r}; see `vedit.py templates`")
        self.t0 = words.time(cfg["at"]) - 0.12
        self.t1 = words.time(cfg.get("end"), self.t0 + float(cfg.get("seconds", 3.0)))
        params = dict(cfg.get("params", {}))
        if "times" in params:
            params["times"] = [words.time(x) - self.t0 for x in params["times"]]
        self.params = params
        self.place = cfg.get("place", "auto")
        self.hides_captions = bool(cfg.get("hidesCaptions", False))
        self.w, self.h, self.faces = width, height, faces
        self.fullframe = getattr(T.REGISTRY[self.name]["fn"], "fullframe", False)
        self.events = [{"t": round(self.t0 + dt, 3), "kind": kind, "level": -12}
                       for dt, kind in T.events(self.name, params)]
        self.events.append({"t": round(self.t1, 3), "kind": "swish", "level": -18})

    def owns(self, t):
        return self.t0 <= t < self.t1 + 0.3

    def draw(self, frame, t):
        lt = t - self.t0
        im = T.render(self.name, lt, self.params, self.w)
        if im is None:
            return
        if t >= self.t1:                                        # exit: fade + drop
            k = D.EASE((t - self.t1) / 0.3)
            im = im.copy()
            im[..., 3] *= 1 - k
        if self.fullframe:
            D.paste(frame, im, 0, 0)
            return
        h, w = im.shape[:2]
        if isinstance(self.place, (list, tuple)):
            x, y = self.place
        else:
            x = (self.w - w) / 2
            _, cy, fh = self.faces.at(t)
            top_room = cy - fh * 0.7 - 230
            y = {"top": 230, "center": (self.h - h) / 2, "bottom": self.h * 0.80 - h}.get(self.place)
            if y is None:   # auto: above the face if it fits, else under the chin
                y = 230 if top_room >= h else min(cy + fh * 0.8, self.h * 0.80 - h)
        D.paste(frame, im, x, y)


# ---------------------------------------------------------------- end card

ICON_PATHS = {   # 24-unit grid, drawn as a stroke that draws itself on (lucide "activity" = pulse)
    "pulse": [(22, 12), (19.5, 12), (17.6, 13.5), (15.2, 21.8), (8.8, 2.2), (6.4, 10.5), (4.5, 12), (2, 12)],
}


class EndCard:
    """Light card slides up, band settles, logo pops (image, or an accent tile whose icon draws on),
    then the name and an optional mono kicker screen in. Layout `stack` (logo above name) or `row`."""

    def __init__(self, cfg, start, width, height, root):
        self.t0, self.len = start, float(cfg.get("seconds", 2.0))
        self.w, self.h = width, height
        self.layout = cfg.get("layout", "stack")
        logo = cfg.get("logo")
        self.logo = None
        if logo:
            im = Image.open((root / logo) if not Path(logo).is_absolute() else logo).convert("RGBA")
            self.logo = im.crop(im.getbbox())
        self.tile = cfg.get("tile")                               # {"icon": "pulse"}
        self.size = int(cfg.get("logoSize", 184 if self.tile else 380))
        name = cfg.get("name", "")
        face = cfg.get("nameFont", "bold" if self.layout == "row" else "display")
        f = D.font(int(cfg.get("nameSize", 112 if self.layout == "row" else 84)), face)
        im = D.layer(int(f.getlength(name)) + 20, int(f.size * 1.5))
        ImageDraw.Draw(im).text((10, im.height / 2), name, font=f, fill=D.C("inkDark"), anchor="lm")
        self.name = D.arr(im) if name else None
        kicker = cfg.get("kicker", "").upper()
        self.kicker = None
        if kicker:
            kf = D.font(34, "mono")
            ki = D.layer(int(kf.getlength(kicker)) + 20, 60)
            ImageDraw.Draw(ki).text((10, 30), kicker, font=kf, fill=D.C("dimOnLight"), anchor="lm")
            self.kicker = D.arr(ki)
        self.events = [{"t": round(start + 0.10, 3), "kind": "whoosh", "level": -8},
                       {"t": round(start + 0.33, 3), "kind": "pop", "level": -9},
                       {"t": round(start + 0.62, 3), "kind": "swish", "level": -16}]
        if self.tile:
            self.events.append({"t": round(start + 0.47, 3), "kind": "tick", "level": -16})

    def _tile(self, size, s):
        im = D.layer(size + 2, size + 2)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, size, size), radius=int(size * 0.28), fill=D.C("accentOnLight"))
        pts24 = ICON_PATHS.get(self.tile.get("icon", "pulse"))
        k = D.clamp((s - 0.45) / 0.6)
        if pts24 and k > 0 and size > 40:
            unit, ox = size * 0.56 / 24, size * 0.22
            pts = [(ox + x * unit, ox + y * unit) for x, y in pts24]
            seg = [((pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5 for i in range(len(pts) - 1)]
            left, path = sum(seg) * D.EASE(k), [pts[0]]
            for i, L in enumerate(seg):
                if left <= 0:
                    break
                r = min(left / L, 1)
                path.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r))
                left -= L
            d.line(path, fill=D.C("inkLight"), width=max(int(2.25 * unit), 2), joint="curve")
        return D.arr(im)

    def draw(self, frame, t):
        if t < self.t0:
            return
        s = t - self.t0
        p = D.EASE(s / 0.5)
        card = np.empty((self.h, self.w, 3), np.uint8)
        card[:] = D.C("light")
        band = int(self.h * (0.56 if self.layout == "row" else 0.62) + 220 * (1 - D.EASE((s - 0.1) / 0.6)))
        card[band:] = D.C("soft")
        off = int(round(self.h * (1 - p)))
        if off < self.h:
            frame[off:] = card[:self.h - off]
        if s < 0.25:
            return
        sc = max(D.spring(s - 0.25), 0.0)
        logo = None
        if sc > 0.02:
            size = max(int(self.size * sc), 2)
            if self.tile:
                logo = self._tile(size, s)
            elif self.logo is not None:
                logo = D.arr(self.logo.resize((size, max(int(size * self.logo.height / self.logo.width), 1)),
                                              Image.LANCZOS))
        if self.layout == "row":
            cy = self.h * 0.47
            nw = self.name.shape[1] if self.name is not None else 0
            x0 = (self.w - (self.size + 40 + nw)) / 2
            if logo is not None:
                D.paste(frame, logo, x0 + (self.size - logo.shape[1]) / 2, cy - logo.shape[0] / 2)
            if self.name is not None:
                wp = (s - 0.5) / 0.5
                a, _ = D.screen_in(self.name, wp, rise=0, blur=6)
                if a is not None:
                    D.paste(frame, a, x0 + self.size + 40 - 40 * (1 - D.EASE(wp)), cy - a.shape[0] / 2)
            below = cy + self.size / 2 + 60
        else:
            cy = self.h * 0.43
            if logo is not None:
                D.paste(frame, logo, self.w / 2 - logo.shape[1] / 2, cy - logo.shape[0] / 2)
            if self.name is not None:
                a, dy = D.screen_in(self.name, (s - 0.5) / 0.5, rise=30, blur=6)
                if a is not None:
                    D.paste(frame, a, self.w / 2 - a.shape[1] / 2, cy + self.size * 0.62 + dy)
            below = cy + self.size * 0.62 + 140
        if self.kicker is not None:
            a, dy = D.screen_in(self.kicker, (s - 0.7) / 0.5, rise=20, blur=4)
            if a is not None:
                D.paste(frame, a, self.w / 2 - a.shape[1] / 2, below + dy)


# ---------------------------------------------------------------- compose

def measured_words(work: Path, words):
    """Whisper can start a word inside the pause before it. When the start lands in silence, move it
    to the measured onset (up to 0.6 s later); inside connected speech keep Whisper's time."""
    from cutplan import FORWARD, HOP, SR, Envelope
    from media import load_audio
    wav = work / "cut_audio.wav"
    if not wav.exists() or not words:
        return words
    env = Envelope(load_audio(wav, SR), words)
    out = []
    for w in words:
        s = w["s"]
        i = env.i(s)
        if env.db[i] < env.weak:
            hi = env.i(min(s + FORWARD, w["e"] + 0.2))
            k = next((j for j in range(i, hi + 1) if env.db[j] >= env.speech), None)
            if k is not None:
                while k > i and env.db[k - 1] >= env.weak:
                    k -= 1
                s = k * HOP
        out.append({**w, "s": round(s, 3), "e": round(max(w["e"], s + 0.12), 3), "whisperStart": w["s"]})
    return out


def build(work: Path, root: Path):
    motion = json.loads((work / "motion.json").read_text(encoding="utf-8"))
    theme = motion.get("theme")
    brand_theme = root / "brand" / "video-theme.json"         # written by /system install from the design guide
    if theme is None and brand_theme.is_file():
        theme = json.loads(brand_theme.read_text(encoding="utf-8"))
    D.set_theme(theme)
    words = Words(measured_words(work, json.loads((work / "cut_words.json").read_text(encoding="utf-8"))["words"]))
    cues = json.loads((work / "cues.json").read_text(encoding="utf-8"))
    base = work / "base.mp4"
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams",
                                      "-show_format", str(base)], capture_output=True, text=True).stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    width, height = v["width"], v["height"]
    num, den = map(int, v["r_frame_rate"].split("/"))
    fps = num / den
    duration = float(info["format"]["duration"])
    faces = FacePath.load(work / "faces.json", width, height)

    cam = Camera(motion.get("camera", {}), words, faces, duration)
    caps = Captions(motion.get("captions", {}), words, cues, width, height, faces)
    end_at = words.words[-1]["e"] + 0.05 if words.words else duration
    tabs = [Tab(s, words, width, height, duration if not motion.get("endCard") else end_at)
            for s in motion.get("scenes", []) if s.get("type") == "tab"]
    overlays = [Overlay(s, words, width, height, faces, duration)
                for s in motion.get("scenes", []) if s.get("type") == "overlay"]
    endcard = EndCard(motion["endCard"], end_at, width, height, root) if motion.get("endCard") else None
    total = (end_at + endcard.len) if endcard else duration
    events = cam.events + [e for x in tabs + overlays for e in x.events] + (endcard.events if endcard else [])
    events.sort(key=lambda e: e["t"])
    return dict(cam=cam, caps=caps, tabs=tabs, overlays=overlays, endcard=endcard, total=total,
                width=width, height=height, fps=fps, fps_str=v["r_frame_rate"], base=base,
                events=events, duration=duration)


def frame_at(s, raw, t):
    face = s["cam"].apply(raw, t)
    frame = face.copy()
    owned = False
    for tab in s["tabs"]:
        if tab.owns(t):
            tab.draw(frame, face, t)
            owned = True
    hide = any(o.owns(t) and o.hides_captions for o in s["overlays"])
    if not owned and not hide and (s["endcard"] is None or t < s["endcard"].t0):
        s["caps"].draw(frame, t)
    for o in s["overlays"]:
        if o.owns(t) and not owned:
            o.draw(frame, t)
    if s["endcard"]:
        s["endcard"].draw(frame, t)
    return frame


def frames(s):
    w, h = s["width"], s["height"]
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(s["base"]), "-vf", "format=rgb24",
                            "-f", "rawvideo", "-"], stdout=subprocess.PIPE, bufsize=w * h * 3)
    n_total = int(round(s["total"] * s["fps"]))
    last = None
    for n in range(n_total):
        raw = dec.stdout.read(w * h * 3)            # past the cut (end card): keep the last frame
        if len(raw) == w * h * 3:
            last = np.frombuffer(raw, np.uint8).reshape(h, w, 3).copy()
        yield n, last
    dec.stdout.close()
    dec.wait()


def render(work: Path, root: Path, out: Path, stills=None):
    s = build(work, root)
    (work / "events.json").write_text(json.dumps(s["events"], indent=1), encoding="utf-8")
    if stills:
        want = {int(round(t * s["fps"])): t for t in stills}
        paths = []
        for n, raw in frames(s):
            if n in want:
                p = work / f"still_{want[n]:06.2f}.jpg"
                Image.fromarray(frame_at(s, raw, n / s["fps"])).save(p, quality=90)
                paths.append(str(p))
            if n > max(want):
                break
        return {"stills": paths, "events": len(s["events"])}
    w, h = s["width"], s["height"]
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", s["fps_str"], "-i", "-",
                            "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-colorspace", "bt709",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                            "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    for n, raw in frames(s):
        enc.stdin.write(frame_at(s, raw, n / s["fps"]).tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("picture encode failed")
    return {"picture": str(out), "seconds": round(s["total"], 3), "events": len(s["events"]),
            "endCardAt": round(s["endcard"].t0, 3) if s["endcard"] else None}


def auto_motion(work: Path):
    """Starting motion.json: auto camera + pill captions. Claude adds scenes and the end card."""
    words = json.loads((work / "cut_words.json").read_text(encoding="utf-8"))["words"]
    emph = []
    for i in auto_emphasis(words):
        key = Words.norm(words[i]["w"])
        nth = sum(1 for w in words[:i + 1] if Words.norm(w["w"]) == key)
        emph.append(key if nth == 1 else f"{key}#{nth}")
    return {"camera": {"auto": True, "base": [1.0, 1.08], "push": 0.07, "emphasis": emph},
            "captions": {"style": "pill", "mono": []},
            "scenes": [],
            "endCard": None}
