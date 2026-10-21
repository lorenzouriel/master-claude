"""Where the speaker's face is, 10 times a second, smoothed: zoom anchor and caption safe zone.

YuNet (OpenCV zoo, MIT) runs on a half-size decode of the video. Gaps are filled from the
nearest detection; the path is smoothed so framing follows the person without jitter.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

MODEL = Path(__file__).resolve().parent / "assets" / "models" / "face_detection_yunet_2023mar.onnx"
RATE = 10
SCALE_W = 540


def _detector(w, h):
    import cv2
    if not MODEL.is_file():
        raise FileNotFoundError(f"face model missing: run `vedit.py assets` ({MODEL})")
    return cv2.FaceDetectorYN.create(str(MODEL), "", (w, h), 0.7, 0.3, 5000)


def track(video, width, height) -> dict:
    sw = SCALE_W
    sh = int(round(height * sw / width / 2) * 2)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={RATE},scale={sw}:{sh}",
                             "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    det = _detector(sw, sh)
    raw = []
    n = 0
    size = sw * sh * 3
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        frame = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
        _, faces = det.detect(frame)
        box = None
        if faces is not None and len(faces):
            f = max(faces, key=lambda r: r[2] * r[3] * r[14])   # biggest confident face
            box = [float(f[0] / sw), float(f[1] / sh), float(f[2] / sw), float(f[3] / sh), float(f[14])]
        raw.append(box)
        n += 1
    proc.wait()
    found = [i for i, b in enumerate(raw) if b]
    if not found:
        return {"rate": RATE, "found": 0, "frames": n, "path": [], "union": None}
    filled = []
    for i in range(n):
        j = min(found, key=lambda k: abs(k - i))
        filled.append(raw[j][:4])
    a = np.array(filled)
    # Smooth centers and size with a 0.7 s moving average: follows leans, ignores jitter.
    k = 7
    pad = np.pad(a, ((k // 2, k // 2), (0, 0)), mode="edge")
    sm = np.stack([np.convolve(pad[:, c], np.ones(k) / k, mode="valid") for c in range(4)], axis=1)
    path = [{"t": round(i / RATE, 2), "cx": round(x + w / 2, 4), "cy": round(y + h / 2, 4),
             "w": round(w, 4), "h": round(h, 4)} for i, (x, y, w, h) in enumerate(sm)]
    x0 = float(a[found, 0].min()); y0 = float(a[found, 1].min())
    x1 = float((a[found, 0] + a[found, 2]).max()); y1 = float((a[found, 1] + a[found, 3]).max())
    return {"rate": RATE, "found": len(found), "frames": n, "path": path,
            "union": [round(x0, 4), round(y0, 4), round(x1 - x0, 4), round(y1 - y0, 4)]}


class FacePath:
    """face(t) -> (cx, cy, h) in output pixels; falls back to the frame's upper center."""

    def __init__(self, data, width, height):
        self.w, self.h = width, height
        self.path = data.get("path", []) if data else []
        self.union = data.get("union") if data else None

    @classmethod
    def load(cls, path: Path, width, height):
        return cls(json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None, width, height)

    def at(self, t):
        if not self.path:
            return self.w * 0.5, self.h * 0.40, self.h * 0.18
        i = int(min(max(t * RATE, 0), len(self.path) - 1))
        p = self.path[i]
        return p["cx"] * self.w, p["cy"] * self.h, p["h"] * self.h

    def chin_y(self):
        """Lowest point the face reaches across the video, in pixels (caption must sit below it)."""
        if not self.union:
            return self.h * 0.55
        return (self.union[1] + self.union[3]) * self.h
