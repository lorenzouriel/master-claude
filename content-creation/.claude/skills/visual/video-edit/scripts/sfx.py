"""Procedural sound effects, synthesized with numpy from fixed seeds (same call, same file).

Each effect knows its anchor: the instant of full strength that lands on the visual event.
Kinds: whoosh, swish, pop, click, tick, type, riser, impact, success, notification.
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SR = 48000
CACHE = Path(__file__).resolve().parent / "assets" / "sfx"


def _env(n, attack, decay_shape=4.0):
    a = max(int(n * attack), 1)
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a) ** 2
    e[a:] = np.exp(-decay_shape * np.linspace(0, 1, n - a))
    return e


def _sweep_noise(rng, dur, f0, f1, width=0.5, pan=(-0.6, 0.6)):
    """Noise through a band-pass whose center sweeps f0 -> f1 (short-time FFT shaping)."""
    n = int(SR * dur)
    x = rng.standard_normal(n + 2048)
    hop, win = 256, 1024
    w = np.hanning(win)
    out = np.zeros(n + 2048)
    freqs = np.fft.rfftfreq(win, 1 / SR)
    frames = (n + 2048 - win) // hop
    for k in range(frames):
        p = min(k * hop / n, 1.0)
        fc = f0 * (f1 / f0) ** p
        band = np.exp(-0.5 * (np.log(np.maximum(freqs, 1) / fc) / width) ** 2)
        seg = np.fft.irfft(np.fft.rfft(x[k * hop:k * hop + win] * w) * band)
        out[k * hop:k * hop + win] += seg * w
    out = out[:n]
    out /= np.max(np.abs(out)) + 1e-9
    pos = np.linspace(pan[0], pan[1], n)
    return np.stack([out * np.sqrt((1 - pos) / 2), out * np.sqrt((1 + pos) / 2)], axis=1)


def _tone(dur, f0, f1=None, shape="sine"):
    n = int(SR * dur)
    f = np.linspace(f0, f1 or f0, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if shape == "sine" else np.sign(np.sin(ph)) * 0.6


def _mono(x):
    return np.stack([x, x], axis=1)


def make(kind, variant=0):
    rng = np.random.default_rng(1000 + variant * 97 + sum(map(ord, kind)))
    if kind == "whoosh":
        dur = 0.75 + 0.15 * variant
        x = _sweep_noise(rng, dur, 300, 3200 + 600 * variant, 0.6)
        env = np.concatenate([np.linspace(0, 1, int(SR * dur * 0.65)) ** 2.2,
                              np.exp(-6 * np.linspace(0, 1, int(SR * dur) - int(SR * dur * 0.65)))])
        x = x * env[:, None]
        anchor = dur * 0.65
    elif kind == "swish":
        dur = 0.28
        x = _sweep_noise(rng, dur, 1500, 6500 + 800 * variant, 0.45, (0.4, -0.4) if variant % 2 else (-0.4, 0.4))
        x = x * _env(len(x), 0.45, 5)[:, None]
        anchor = dur * 0.45
    elif kind == "pop":
        dur = 0.14
        x = _tone(dur, 900 + 120 * variant, 260) * _env(int(SR * dur), 0.02, 9)
        x[:int(SR * 0.003)] += rng.standard_normal(int(SR * 0.003)) * 0.4
        x = _mono(x)
        anchor = 0.004
    elif kind in ("click", "tick", "type"):
        dur = {"click": 0.05, "tick": 0.03, "type": 0.04}[kind]
        n = int(SR * dur)
        burst = rng.standard_normal(n) * np.exp(-60 * np.linspace(0, 1, n) * (3 if kind == "tick" else 1))
        body = _tone(dur, {"click": 2400, "tick": 3800, "type": 1800}[kind] + 150 * variant) * _env(n, 0.01, 30)
        x = _mono(0.6 * burst + 0.5 * body)
        anchor = 0.002
    elif kind == "riser":
        dur = 1.1
        noise = _sweep_noise(rng, dur, 400, 5000, 0.7, (0, 0))
        t = _mono(_tone(dur, 180, 720) * 0.4)
        env = np.linspace(0, 1, int(SR * dur)) ** 2.5
        x = (noise + t) * env[:, None]
        anchor = dur * 0.98
    elif kind == "impact":
        dur = 0.6
        n = int(SR * dur)
        sub = _tone(dur, 110, 38) * np.exp(-7 * np.linspace(0, 1, n))
        hit = rng.standard_normal(n) * np.exp(-40 * np.linspace(0, 1, n))
        x = _mono(0.9 * sub + 0.35 * hit)
        anchor = 0.005
    elif kind == "success":
        parts = []
        for f, d in ((880, 0.12), (1318.5, 0.32)):
            n = int(SR * d)
            parts.append((_tone(d, f) + 0.3 * _tone(d, f * 2)) * _env(n, 0.02, 5))
        x = _mono(np.concatenate(parts) * 0.7)
        anchor = 0.12
    elif kind == "notification":
        parts = []
        for f in (1046.5, 1568):
            n = int(SR * 0.16)
            parts.append((_tone(0.16, f) + 0.2 * _tone(0.16, f * 3)) * _env(n, 0.02, 6))
        x = _mono(np.concatenate(parts) * 0.7)
        anchor = 0.004
    else:
        raise ValueError(f"unknown effect {kind!r}")
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89                 # -1 dBFS peak before gain
    return x.astype(np.float32), anchor


def write(kind, variant=0) -> tuple[Path, float]:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{kind}-{variant}.wav"
    x, anchor = make(kind, variant)
    if not path.exists():
        pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
    return path, anchor


KINDS = ["whoosh", "swish", "pop", "click", "tick", "type", "riser", "impact", "success", "notification"]
