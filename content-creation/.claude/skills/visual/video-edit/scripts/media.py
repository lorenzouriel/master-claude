"""FFmpeg/ffprobe wrappers shared by every vedit command."""
from __future__ import annotations

import json
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

HDR_TRANSFERS = {"smpte2084", "arib-std-b67"}


class MediaError(RuntimeError):
    pass


def run(args, cwd=None, check=True):
    result = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True,
                            text=True, encoding="utf-8", errors="replace")
    if check and result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-8:])
        raise MediaError(f"{Path(str(args[0])).name} failed ({result.returncode}): {tail}")
    return result


def require_tools():
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing:
        raise MediaError(f"not on PATH: {', '.join(missing)}")


def _fraction(value):
    try:
        f = Fraction(value)
        return f if f > 0 else None
    except (ValueError, ZeroDivisionError, TypeError):
        return None


def _rotation(stream):
    for side in stream.get("side_data_list", []):
        if "rotation" in side:
            return int(round(float(side["rotation"]))) % 360
    return int(stream.get("tags", {}).get("rotate", 0)) % 360


def probe(path) -> dict:
    """Facts about one source: geometry after rotation, rational fps, color, audio."""
    path = Path(path)
    if not path.is_file():
        raise MediaError(f"source not found: {path}")
    out = run(["ffprobe", "-v", "error", "-print_format", "json",
               "-show_format", "-show_streams", path]).stdout
    data = json.loads(out)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"
                  and not s.get("disposition", {}).get("attached_pic")), None)
    audio = [s for s in data["streams"] if s["codec_type"] == "audio"]
    if video is None:
        raise MediaError(f"no video stream: {path.name}")
    rot = _rotation(video)
    w, h = video["width"], video["height"]
    if rot in (90, 270):
        w, h = h, w
    r = _fraction(video.get("r_frame_rate"))
    avg = _fraction(video.get("avg_frame_rate"))
    fps = avg or r
    vfr = bool(r and avg and abs(float(r) - float(avg)) / float(r) > 0.01)
    transfer = video.get("color_transfer")
    return {
        "path": str(path.resolve()),
        "name": path.name,
        "duration": float(data["format"].get("duration") or video.get("duration") or 0),
        "width": w,
        "height": h,
        "rotation": rot,
        "fps": f"{fps.numerator}/{fps.denominator}" if fps else None,
        "fpsFloat": round(float(fps), 3) if fps else None,
        "vfr": vfr,
        "codec": video.get("codec_name"),
        "pixFmt": video.get("pix_fmt"),
        "color": {
            "range": video.get("color_range"),
            "space": video.get("color_space"),
            "transfer": transfer,
            "primaries": video.get("color_primaries"),
        },
        "hdr": transfer in HDR_TRANSFERS,
        "audioTracks": len(audio),
        "audio": [{"codec": a.get("codec_name"), "rate": int(a.get("sample_rate", 0)),
                   "channels": a.get("channels")} for a in audio],
        "sizeMB": round(path.stat().st_size / 1e6, 1),
    }


def fps_of(info) -> Fraction:
    return Fraction(info["fps"]) if info.get("fps") else Fraction(30)


def load_audio(path, sr=16000, start=None, duration=None):
    """Decode the first audio track to mono float32 at `sr` Hz."""
    import numpy as np
    args = ["ffmpeg", "-v", "error"]
    if start is not None:
        args += ["-ss", f"{start:.3f}"]
    if duration is not None:
        args += ["-t", f"{duration:.3f}"]
    args += ["-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    result = subprocess.run(args, capture_output=True)
    if result.returncode != 0:
        raise MediaError(f"audio decode failed: {result.stderr.decode('utf-8', 'replace')[-400:]}")
    return np.frombuffer(result.stdout, dtype=np.float32).copy()


def filters_available() -> set:
    out = run(["ffmpeg", "-hide_banner", "-filters"]).stdout
    names = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and len(parts[0]) in (2, 3):
            names.add(parts[1])
    return names


def encoders_available() -> set:
    out = run(["ffmpeg", "-hide_banner", "-encoders"]).stdout
    return {line.split()[1] for line in out.splitlines() if len(line.split()) >= 2 and line.startswith(" ")}


def unique_path(path: Path) -> Path:
    """Never overwrite: name-v001.mp4, name-v002.mp4, ..."""
    stem, suffix = path.stem, path.suffix
    n = 1
    while True:
        candidate = path.with_name(f"{stem}-v{n:03d}{suffix}")
        if not candidate.exists():
            return candidate
        n += 1
