"""Measure the voice before choosing treatment: noise, clipping, and level differences between takes.

Noise: speech RMS vs the floor measured in this recording's own pauses (trimmed 60 ms from speech).
    >= 30 dB clean (no denoise) · 20-30 dB light · < 20 dB strong.
Clipping: samples crowded at the ceiling and flat-topped runs. Clipped speech can't be restored:
    report the times to listen and suggest another take.
Takes: speech-only RMS per cut segment against the speech-weighted median, as gains to even them.
"""
from __future__ import annotations

import numpy as np

from cutplan import HOP, SR, Envelope
from media import load_audio


def _speech_mask(env: Envelope, trim=0.06):
    speech = env.db >= env.speech
    pause = env.db < env.weak
    k = int(trim / HOP)
    if k:
        grown = np.convolve(speech.astype(float), np.ones(2 * k + 1), mode="same") > 0
        pause &= ~grown
    return speech, pause


def noise(audio, words) -> dict:
    env = Envelope(audio, words)
    speech, pause = _speech_mask(env)
    if pause.sum() * HOP < 0.1:                       # almost no pauses: quietest 50 ms windows + 3 dB
        floor = float(np.percentile(env.db, 5)) + 3
    else:
        floor = float(np.median(env.db[pause]))
    voice = float(np.median(env.db[speech])) if speech.any() else env.voice
    snr = voice - floor
    rec = "off" if snr >= 30 else "light" if snr >= 20 else "strong"
    return {"voiceDb": round(voice, 1), "floorDb": round(floor, 1), "snrDb": round(snr, 1),
            "denoise": rec, "pauseSeconds": round(float(pause.sum() * HOP), 2)}


def clipping(path) -> dict:
    x = load_audio(path, 48000)
    a = np.abs(x)
    ceil = float(a.max()) if a.size else 0.0
    if ceil < 0.5:
        return {"status": "none", "ceiling": round(ceil, 3), "times": []}
    near = a >= ceil * 0.995
    runs = np.diff(np.concatenate([[0], near.astype(int), [0]]))
    starts, ends = np.where(runs == 1)[0], np.where(runs == -1)[0]
    flat = [(s, e) for s, e in zip(starts, ends) if e - s >= 3]
    times = sorted({round(s / 48000, 1) for s, _ in flat})[:20]
    dense = near.mean() > 1e-4
    status = "definite" if ceil >= 0.999 and len(flat) >= 5 else "possible" if flat or dense else "none"
    return {"status": status, "ceiling": round(ceil, 3), "flatRuns": len(flat), "times": times}


def take_levels(plan, sources, words_by_src, max_gain=6.0) -> list:
    """Gain (dB) per segment to bring each take to the speech-weighted median level."""
    envs, rows = {}, []
    for k, seg in enumerate(plan["segments"]):
        src = seg["src"]
        if src not in envs:
            audio = load_audio(sources[src], SR)
            envs[src] = Envelope(audio, words_by_src[src])
        env = envs[src]
        i0, i1 = env.i(seg["start"]), env.i(seg["end"])
        db = env.db[i0:i1]
        sp = db[db >= env.speech]
        if sp.size < 10:
            rows.append({"segment": k, "speechSeconds": 0, "levelDb": None})
            continue
        level = 10 * np.log10(np.mean(10 ** (sp / 10)))
        rows.append({"segment": k, "speechSeconds": round(sp.size * HOP, 2), "levelDb": round(float(level), 1)})
    valid = [r for r in rows if r["levelDb"] is not None]
    if not valid:
        return rows
    order = sorted(valid, key=lambda r: r["levelDb"])
    half, acc, ref = sum(r["speechSeconds"] for r in valid) / 2, 0.0, order[-1]["levelDb"]
    for r in order:
        acc += r["speechSeconds"]
        if acc >= half:
            ref = r["levelDb"]
            break
    for r in rows:
        g = 0.0 if r["levelDb"] is None else ref - r["levelDb"]
        r["gainDb"] = round(max(-max_gain, min(max_gain, g)), 1) if abs(g) >= 1.5 else 0.0
    return rows


def denoise_filter(level, floor_db):
    """highpass 80 Hz + afftdn tuned to the measured floor. `light` keeps more room tone than `strong`."""
    if level in (None, "off"):
        return ""
    nf = max(-80, min(-20, round(floor_db)))
    nr = 12 if level == "light" else 24
    return f"highpass=f=80:poles=2,afftdn=nr={nr}:nf={nf}:tn=1"
