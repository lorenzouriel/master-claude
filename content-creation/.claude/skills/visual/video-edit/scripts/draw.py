"""Drawing kit shared by the compositor and the templates: brand palette, fonts, easing, RGBA layers.

Layers are float32 RGBA numpy arrays (0-255). Everything is monochrome (brand/design-guide.md).
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTS = Path(__file__).resolve().parent / "fonts"

BLACK, NEAR, WHITE = (0, 0, 0), (26, 26, 26), (255, 255, 255)
SOFT, LIGHT, STROKE = (245, 245, 245), (239, 239, 239), (191, 191, 191)
MID, GREY, BAR = (95, 95, 95), (150, 150, 150), (44, 44, 44)

# Color roles. Monochrome is the fallback; brand/video-theme.json (from /system install) or a
# motion.json "theme" overrides roles and fonts.
DEFAULT_THEME = {
    "dark": NEAR, "light": WHITE, "soft": SOFT, "line": STROKE,
    "inkDark": NEAR, "inkLight": WHITE,
    "accent": WHITE, "accentOnLight": NEAR,
    "dim": GREY, "dimOnLight": MID,
    "track": (64, 64, 64), "trackOnLight": LIGHT,
    "bar": BAR, "barOnLight": WHITE,
    "capIdle": GREY, "capActive": WHITE,
    "fonts": {"text": "Inter-SemiBold.ttf", "bold": "Inter-ExtraBold.ttf",
              "mono": "JetBrainsMono-Medium.ttf", "display": "Fraunces-SemiBold.ttf"},
}
THEME = {**DEFAULT_THEME, "fonts": dict(DEFAULT_THEME["fonts"])}


def hex_rgb(v):
    if isinstance(v, (list, tuple)):
        return tuple(int(x) for x in v[:3])
    v = v.lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def set_theme(cfg):
    """Apply a theme: {"role": "#RRGGBB", ..., "fonts": {"text": "Figtree-SemiBold.ttf"}}. Unknown roles fail."""
    THEME.clear()
    THEME.update({**DEFAULT_THEME, "fonts": dict(DEFAULT_THEME["fonts"])})
    for k, v in (cfg or {}).items():
        if k.startswith("_"):                                     # comments in theme files
            continue
        if k == "fonts":
            THEME["fonts"].update(v)
        elif k == "name":
            continue
        elif k in DEFAULT_THEME:
            THEME[k] = hex_rgb(v)
        else:
            raise ValueError(f"unknown theme role {k!r}; roles: {', '.join(r for r in DEFAULT_THEME if r != 'fonts')}")
    font.cache_clear()


def C(role):
    return THEME[role]


@lru_cache(maxsize=256)
def font(size: int, face: str = "text"):
    name = THEME["fonts"][face]
    path = Path(name) if Path(name).is_absolute() else FONTS / name
    if not path.is_file() and (Path.cwd() / name).is_file():     # brand fonts, e.g. "brand/fonts/X.ttf"
        path = Path.cwd() / name
    return ImageFont.truetype(str(path), int(size))


# ---------------------------------------------------------------- timing

def clamp(x, lo=0.0, hi=1.0):
    return min(max(x, lo), hi)


def bezier(x1, y1, x2, y2):
    def f(t):
        t = clamp(t)
        lo, hi = 0.0, 1.0
        for _ in range(30):
            m = (lo + hi) / 2
            bx = 3 * (1 - m) ** 2 * m * x1 + 3 * (1 - m) * m * m * x2 + m ** 3
            lo, hi = (m, hi) if bx < t else (lo, m)
        m = (lo + hi) / 2
        return 3 * (1 - m) ** 2 * m * y1 + 3 * (1 - m) * m * m * y2 + m ** 3
    return f


EASE = bezier(0.16, 1, 0.3, 1)      # screen-in
SNAPPY = bezier(0.7, 0, 0.2, 1)     # push between tabs
IN_OUT = bezier(0.65, 0, 0.35, 1)


def spring(tau, k=14.0, w=22.0):
    """0 -> 1 with ~14% overshoot, settles in ~0.3 s."""
    if tau <= 0:
        return 0.0
    return 1.0 if tau > 0.6 else 1 - math.exp(-k * tau) * math.cos(w * tau)


# ---------------------------------------------------------------- layers

def layer(w, h):
    return Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))


def arr(im):
    return np.asarray(im, dtype=np.float32)


def paste(frame, a, x, y, alpha=1.0):
    """Alpha-composite RGBA array `a` onto uint8 RGB `frame` at (x, y), in place."""
    if a is None or alpha <= 0:
        return
    h, w = a.shape[:2]
    x, y = int(round(x)), int(round(y))
    H, W = frame.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1:
        return
    src = a[y0 - y:y1 - y, x0 - x:x1 - x]
    k = src[..., 3:4] * (alpha / 255.0)
    roi = frame[y0:y1, x0:x1].astype(np.float32)
    frame[y0:y1, x0:x1] = (src[..., :3] * k + roi * (1 - k)).astype(np.uint8)


def scaled(a, s):
    if abs(s - 1) < 1e-3:
        return a
    import cv2
    h, w = a.shape[:2]
    return cv2.resize(a, (max(int(w * s), 1), max(int(h * s), 1)), interpolation=cv2.INTER_LINEAR)


def screen_in(a, p, rise=24, blur=8):
    """Blur + fade + rise entrance. Returns (array, dy)."""
    import cv2
    e = EASE(p)
    if e >= 0.99:
        return a, 0
    if e <= 0:
        return None, 0
    out = cv2.GaussianBlur(a, (0, 0), blur * (1 - e)) if blur * (1 - e) > 0.3 else a.copy()
    out[..., 3] *= e
    return out, int(round(rise * (1 - e)))


def rounded_mask(w, h, r):
    m = Image.new("L", (int(w), int(h)), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, int(w) - 1, int(h) - 1), radius=int(r), fill=255)
    return np.asarray(m, dtype=np.float32)[..., None] / 255.0


def text_size(text, f):
    l, t, r, b = f.getbbox(text)
    return r - l, b - t


def wrap(text, f, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + ([cur] if cur else [])


def card(w, h, fill=WHITE, radius=24, alpha=255):
    im = layer(w, h)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=tuple(fill) + (alpha,))
    return im


def mix(a, b, k):
    """Color between b (k=0) and a (k=1). Use instead of alpha when drawing on an opaque card."""
    k = clamp(k)
    return tuple(int(round(y + (x - y) * k)) for x, y in zip(a, b))


def ink_for(fill):
    """Text color with the best contrast on a solid fill."""
    lum = 0.2126 * fill[0] + 0.7152 * fill[1] + 0.0722 * fill[2]
    return NEAR if lum > 140 else WHITE
