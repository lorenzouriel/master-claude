"""Sound plan + final mix: voice, effects peaked on visual events, music solved below the voice.

- Each effect's anchor (its full-strength instant) lands on the event frame.
- Events closer than `spacing` collapse to the stronger one; the same kind never repeats within 0.25 s.
- Music gain is solved from measured loudness so it sits `below` LU under the voice, ducked by a
  voice sidechain, faded in/out, and allowed to rise on the end card. Final: two-pass loudnorm.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import sfx
from media import run


def plan(events, spacing=0.12, same_kind=0.25, max_level=-6):
    out = []
    for e in sorted(events, key=lambda e: e["t"]):
        lvl = e.get("level", -12)
        if out and e["t"] - out[-1]["t"] < spacing:
            if lvl > out[-1]["level"]:
                out[-1] = {**e, "level": lvl}
            continue
        if any(o["kind"] == e["kind"] and e["t"] - o["t"] < same_kind for o in out[-3:]):
            continue
        out.append({**e, "level": min(lvl, max_level)})
    counts = {}
    for e in out:                                    # rotate variants so repeats don't sound copied
        e["variant"] = counts.get(e["kind"], 0) % 3
        counts[e["kind"]] = counts.get(e["kind"], 0) + 1
    return out


def loudness(path, start=None, dur=None, stream="0:a:0"):
    args = ["ffmpeg", "-hide_banner", "-nostats"]
    if start is not None:
        args += ["-ss", f"{start:.3f}"]
    if dur is not None:
        args += ["-t", f"{dur:.3f}"]
    err = run(args + ["-i", path, "-map", stream, "-af", "ebur128", "-f", "null", "-"]).stderr
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):])
    return float(m.group(1)) if m else None


def mix(work: Path, out: Path, total: float, music=None, music_start=0.0, below=18.0,
        end_card_at=None, effects=True, target_i=-14.0, target_tp=-1.5):
    picture, voice = work / "picture.mp4", work / "base.mp4"
    events = json.loads((work / "events.json").read_text(encoding="utf-8")) if effects else []
    sp = plan(events)
    (work / "sound_plan.json").write_text(json.dumps(sp, indent=1), encoding="utf-8")

    inputs = ["-i", str(picture), "-i", str(voice)]
    parts = [f"[1:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{total:.4f},asplit=2[voice][key]"]
    labels = ["[voice]"]
    n_in = 2
    report = {"effects": len(sp), "music": None}
    if music:
        voice_i = loudness(str(voice)) or -14.0
        music_i = loudness(str(music), music_start, total) or -14.0
        g = (voice_i - below) - music_i
        lift = 9.0 if end_card_at else 0.0
        e0 = end_card_at or total
        vol = (f"volume='{10 ** (g / 20):.5f}*if(lt(t,{e0:.3f}),1,1+({10 ** (lift / 20):.4f}-1)*min((t-{e0:.3f})/0.4,1))'"
               f":eval=frame")
        fade = min(0.9, total / 3)
        inputs += ["-ss", f"{music_start:.3f}", "-t", f"{total:.4f}", "-i", str(music)]
        parts.append(f"[{n_in}:a]aresample=48000,aformat=channel_layouts=stereo,{vol},"
                     f"afade=t=in:d=0.4,afade=t=out:st={total - fade:.3f}:d={fade:.3f}[mus]")
        parts.append("[mus][key]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=350[bed]")
        labels.append("[bed]")
        n_in += 1
        report["music"] = {"file": Path(music).name, "voiceLUFS": voice_i, "musicLUFS": music_i,
                           "gainDb": round(g, 1), "belowVoiceLU": below}
    else:
        parts.append("[key]anullsink")
    for k, e in enumerate(sp):
        path, anchor = sfx.write(e["kind"], e["variant"])
        ms = max(int(round((e["t"] - anchor) * 1000)), 0)
        inputs += ["-i", str(path)]
        parts.append(f"[{n_in}:a]volume={e['level']}dB,adelay={ms}:all=1[e{k}]")
        labels.append(f"[e{k}]")
        n_in += 1
    parts.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0,"
                 f"atrim=0:{total:.4f}[mix]")
    graph = ";".join(parts)
    meas = run(["ffmpeg", "-hide_banner", "-nostats", *inputs, "-filter_complex",
                graph + f";[mix]loudnorm=I={target_i}:TP={target_tp}:LRA=11:print_format=json[o]",
                "-map", "[o]", "-f", "null", "-"]).stderr
    m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    ln = (f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
          "linear=true,aresample=48000")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph + f";[mix]{ln}[o]",
         "-map", "0:v", "-map", "[o]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", str(out)])
    report["preNormLUFS"] = float(m["input_i"])
    return report
