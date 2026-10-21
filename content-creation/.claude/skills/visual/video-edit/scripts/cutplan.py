"""Turn a Claude-written EDL into frame-exact segments measured against the waveform.

Technique (after editonny's tighten-cut): a 10 ms RMS envelope, thresholds set
relative to this speaker's own voice level and room floor, boundaries pushed
through quiet sound to keep consonants and word tails, then padded and snapped
to the frame grid. Internal pauses longer than `maxPause` are removed.
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np

SR = 16000
HOP = 0.01
PAD_AFTER = 0.06    # kept after the last measured sound of a word
PAD_BEFORE = 0.07   # kept before the first measured sound of the next word
REACH = 0.12        # how far weak sound can extend a boundary
SEARCH = 0.25       # how far a Whisper word edge may be off
FORWARD = 0.6       # a start Whisper places inside a pause can be this early (measured: 0.47 s)


class Envelope:
    def __init__(self, audio: np.ndarray, words):
        hop, frame = int(SR * HOP), int(SR * 0.02)
        padded = np.pad(audio, (frame // 2, frame))
        n = max(1, len(audio) // hop)
        idx = np.arange(n)[:, None] * hop + np.arange(frame)[None, :]
        rms = np.sqrt(np.mean(padded[idx] ** 2, axis=1)) + 1e-9
        self.db = 20 * np.log10(rms)
        self.duration = len(audio) / SR
        floor = float(np.percentile(self.db, 10))
        centers = [self.db[self.i((w["s"] + w["e"]) / 2)] for w in words] or [float(np.percentile(self.db, 90))]
        voice = float(np.percentile(centers, 60))
        span = max(voice - floor, 6.0)
        self.floor, self.voice = floor, voice
        self.speech = floor + 0.40 * span
        self.weak = floor + 0.15 * span

    def i(self, t):
        return int(min(max(t / HOP, 0), len(self.db) - 1))

    def t(self, i):
        return i * HOP

    def onset(self, t, limit):
        """First real sound of a word Whisper says starts near t, never before `limit`."""
        i = self.i(t)
        lo = self.i(max(limit, t - SEARCH))
        hi = self.i(t + FORWARD)
        if self.db[i] < self.speech:
            j = next((k for k in range(i, hi + 1) if self.db[k] >= self.speech), None)
            if j is None:   # Whisper edge was late: look backwards
                j = next((k for k in range(i, lo - 1, -1) if self.db[k] >= self.speech), i)
            i = j
        else:
            while i > lo and self.db[i - 1] >= self.speech:
                i -= 1
        reach = self.i(self.t(i) - REACH)
        while i > max(lo, reach) and self.db[i - 1] >= self.weak:
            i -= 1
        return max(limit, self.t(i) - PAD_BEFORE)

    def offset(self, t, limit):
        """Last real sound of a word Whisper says ends near t, never after `limit`."""
        i = self.i(t)
        lo = self.i(t - SEARCH)
        hi = self.i(min(limit, t + SEARCH))
        if self.db[i] < self.speech:
            j = next((k for k in range(i, lo - 1, -1) if self.db[k] >= self.speech), None)
            if j is None:
                j = next((k for k in range(i, hi + 1) if self.db[k] >= self.speech), i)
            i = j
        else:
            while i < hi and self.db[i + 1] >= self.speech:
                i += 1
        reach = self.i(self.t(i) + REACH)
        while i < min(hi, reach) and self.db[i + 1] >= self.weak:
            i += 1
        return min(limit, self.t(i) + HOP + PAD_AFTER)


def _words_in(words, a, b):
    return [w for w in words if a <= (w["s"] + w["e"]) / 2 <= b]


def _protected(t0, t1, protect):
    return any(p0 < t1 and t0 < p1 for p0, p1 in protect)


def plan(edl: dict, infos: list, words_by_src: list, audio_by_src: list) -> dict:
    max_pause = float(edl.get("maxPause", 0.35))
    join_gap = float(edl.get("joinGap", 0.25))
    tighten = bool(edl.get("tighten", True))
    protect = [tuple(p) for p in edl.get("protect", [])]

    keep = edl["keep"]
    if keep == "all":
        keep = [{"src": s, "from": w[0]["s"], "to": w[-1]["e"], "why": "whole source"}
                for s, w in enumerate(words_by_src) if w]

    envs = {}
    raw = []
    for k in keep:
        src = int(k.get("src", 0))
        if src not in envs:
            envs[src] = Envelope(audio_by_src[src], words_by_src[src])
        env = envs[src]
        words = _words_in(words_by_src[src], float(k["from"]), float(k["to"]))
        if not words:
            raise ValueError(f"keep range {k['from']}-{k['to']} on source {src} contains no words")
        start = env.onset(words[0]["s"], 0.0)
        end = env.offset(words[-1]["e"], env.duration)
        # Never clip into a protected interval that the range touches.
        for p0, p1 in protect:
            if p0 < end and start < p1:
                start, end = min(start, p0), max(end, p1)
        pieces = [[start, end]]
        if tighten:
            extra = max(0.0, (join_gap - PAD_AFTER - PAD_BEFORE) / 2)
            for a, b in zip(words, words[1:]):
                e = env.offset(a["e"], b["s"] + SEARCH)
                s = env.onset(b["s"], a["e"] - SEARCH)
                silence = (s + PAD_BEFORE) - (e - PAD_AFTER)
                if silence > max_pause and silence - join_gap > 0.05 and not _protected(e, s, protect):
                    pieces[-1][1] = min(e + extra, s)
                    pieces.append([max(s - extra, e), end])
        for a, b in pieces:
            raw.append({"src": src, "start": a, "end": b, "why": k.get("why", "")})

    segments = []
    for seg in raw:
        fps = Fraction(infos[seg["src"]]["fps"] or "30")
        f0 = math.floor(seg["start"] * fps)
        f1 = math.ceil(seg["end"] * fps)
        if f1 <= f0:
            continue
        prev = segments[-1] if segments else None
        if prev and prev["src"] == seg["src"] and f0 <= prev["f1"] + 1 and f0 >= prev["f0"]:
            prev["f1"] = max(prev["f1"], f1)   # touching or overlapping: one segment
            continue
        segments.append({"src": seg["src"], "f0": f0, "f1": f1, "why": seg["why"]})

    out_t = 0.0
    for seg in segments:
        fps = Fraction(infos[seg["src"]]["fps"] or "30")
        seg["start"] = float(seg["f0"] / fps)
        seg["end"] = float(seg["f1"] / fps)
        seg["outStart"] = round(out_t, 4)
        out_t += seg["end"] - seg["start"]
        seg["outEnd"] = round(out_t, 4)

    used = sorted({s["src"] for s in segments})
    source_total = sum(infos[s]["duration"] for s in used)
    return {
        "segments": segments,
        "sourceDuration": round(source_total, 3),
        "cutDuration": round(out_t, 3),
        "removed": round(source_total - out_t, 3),
        "joins": max(0, len(segments) - 1),
        "params": {"maxPause": max_pause, "joinGap": join_gap, "tighten": tighten, "protect": protect},
        "levels": {str(s): {"floorDb": round(e.floor, 1), "voiceDb": round(e.voice, 1)} for s, e in envs.items()},
    }


def remap_words(segments, words_by_src):
    """Words that survive the cut, in output time. Whisper edges drift past measured joins, so a word
    belongs to the segment it overlaps most, if that covers at least 40% of it."""
    out = []
    for k, seg in enumerate(segments):
        shift = seg["outStart"] - seg["start"]
        for w in words_by_src[seg["src"]]:
            dur = max(w["e"] - w["s"], 0.01)
            ov = [(min(w["e"], s["end"]) - max(w["s"], s["start"]), j)
                  for j, s in enumerate(segments) if s["src"] == seg["src"]]
            best, j = max(ov)
            if j != k or best / dur < 0.4:
                continue
            out.append({**w, "s": round(max(w["s"], seg["start"]) + shift, 3),
                        "e": round(min(w["e"], seg["end"]) + shift, 3)})
    return out
