"""Checks on the actual exported file. A check that could not run is `not_checked`, never `passed`."""
from __future__ import annotations

import re
from pathlib import Path

from media import probe, run


def _check(name, status, detail):
    return {"name": name, "status": status, "detail": detail}


def loudness(path):
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn",
               "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    summary = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+|-inf) LUFS", summary)
    tp = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS", summary)
    val = lambda m: float(m.group(1)) if m and m.group(1) != "-inf" else None
    return val(i), val(tp)


def contact_sheet(path, out: Path, duration, vertical, frames=12):
    cols, rows = (6, 2) if vertical else (4, 3)
    width = 180 if vertical else 320
    rate = frames / max(duration, 0.1)
    run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vf",
         f"fps={rate:.5f},scale={width}:-2,tile={cols}x{rows}:padding=4:color=white",
         "-frames:v", "1", "-q:v", "3", out])
    return out


def check(path, expected=None, work: Path | None = None, target_i=-14.0, max_tp=-1.0, caption_issues=None):
    """expected: {width, height, fps, duration} from the plan and target."""
    path = Path(path)
    checks = []
    info = probe(path)

    decode = run(["ffmpeg", "-v", "error", "-i", path, "-f", "null", "-"], check=False)
    errors = [l for l in decode.stderr.splitlines() if l.strip()]
    checks.append(_check("full decode", "passed" if decode.returncode == 0 and not errors else "failed",
                         "no errors" if not errors else errors[:3]))

    if expected:
        geo_ok = info["width"] == expected["width"] and info["height"] == expected["height"]
        checks.append(_check("size", "passed" if geo_ok else "failed", f"{info['width']}x{info['height']}"))
        fps_ok = expected.get("fps") is None or abs(info["fpsFloat"] - expected["fps"]) < 0.01
        checks.append(_check("frame rate", "passed" if fps_ok else "failed", info["fps"]))
        if expected.get("duration") is not None:
            dur_ok = abs(info["duration"] - expected["duration"]) <= 0.1
            checks.append(_check("duration", "passed" if dur_ok else "failed",
                                 f"{info['duration']:.2f}s vs plan {expected['duration']:.2f}s"))

    checks.append(_check("audio present", "passed" if info["audioTracks"] == 1 else "failed",
                         f"{info['audioTracks']} track(s)"))
    i, tp = loudness(path)
    if i is None:
        checks.append(_check("loudness", "failed", "silent or unmeasurable"))
    else:
        checks.append(_check("loudness", "passed" if abs(i - target_i) <= 1.0 else "failed", f"{i} LUFS"))
    checks.append(_check("true peak", "passed" if tp is not None and tp <= max_tp else "failed", f"{tp} dBTP"))

    if caption_issues is None:
        checks.append(_check("captions", "not_checked", "no captions in this render"))
    else:
        checks.append(_check("captions text", "passed" if not caption_issues else "failed",
                             caption_issues or "every spoken word shown, no em dash or emoji"))
        checks.append(_check("captions on frame (OCR)", "not_checked",
                             "no local OCR reader; inspect the contact sheet"))

    sheet = None
    if work:
        sheet = contact_sheet(path, work / f"{path.stem}-contact.jpg", info["duration"],
                              info["height"] > info["width"])
    ok = all(c["status"] == "passed" for c in checks if c["status"] != "not_checked")
    return {"file": str(path.resolve()), "ok": ok, "duration": info["duration"],
            "loudness": i, "truePeak": tp, "contactSheet": str(sheet) if sheet else None, "checks": checks}
