"""Render a plan: cut + geometry + burned captions, audio cut separately then two-pass loudnorm."""
from __future__ import annotations

import json
from pathlib import Path

from media import MediaError, run

TARGETS = {
    "reel": (1080, 1920),
    "short": (1080, 1920),
    "youtube": (1920, 1080),
    "source": None,
}
FADE = 0.008


def _sources(segments):
    return sorted({s["src"] for s in segments})


def _inputs(infos, segments):
    args, index = [], {}
    for n, src in enumerate(_sources(segments)):
        args += ["-i", infos[src]["path"]]
        index[src] = n
    return args, index


def _geometry(info, size, fit, crop_x):
    if size is None:
        return f"setsar=1"
    w, h = size
    same = abs(info["width"] / info["height"] - w / h) < 0.01
    if same or fit == "scale":
        return f"scale={w}:{h}:flags=lanczos,setsar=1"
    if fit == "pad":
        return (f"scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1")
    return (f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={w}:{h}:(iw-{w})*{crop_x:.3f}:(ih-{h})/2,setsar=1")


def render_audio(plan, infos, out_wav: Path, denoise="", gains=None):
    """Cut audio with 8 ms fades at every join, optional per-take gain and denoise filter, 48 kHz PCM."""
    segs = plan["segments"]
    args, index = _inputs(infos, segs)
    parts, concat = [], ""
    for i, s in enumerate(segs):
        d = s["end"] - s["start"]
        g = (gains or {}).get(i, 0.0)
        gain = f",volume={g}dB" if g else ""
        parts.append(f"[{index[s['src']]}:a:0]atrim={s['start']:.5f}:{s['end']:.5f},asetpts=PTS-STARTPTS,"
                     f"aresample=48000,aformat=channel_layouts=stereo{gain},"
                     f"afade=t=in:d={FADE},afade=t=out:st={max(0.0, d - FADE):.5f}:d={FADE}[a{i}]")
        concat += f"[a{i}]"
    tail = f",{denoise}" if denoise else ""
    parts.append(f"{concat}concat=n={len(segs)}:v=0:a=1{tail}[ac]")
    run(["ffmpeg", "-y", "-v", "error", *args, "-filter_complex", ";".join(parts),
         "-map", "[ac]", "-c:a", "pcm_s16le", out_wav])


def measure_loudness(wav: Path, target_i=-14.0, target_tp=-1.5):
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", wav, "-af",
               f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:print_format=json", "-f", "null", "-"]).stderr
    return json.loads(err[err.rindex("{"):err.rindex("}") + 1])


def render(plan, infos, work: Path, out: Path, target="reel", fit="crop", crop_x=0.5,
           captions_file="captions.ass", denoise="", target_i=-14.0, target_tp=-1.5,
           sample=None, crf=18, preset="slow", tonemap=False, gains=None):
    segs = plan["segments"]
    hdr = [infos[s]["name"] for s in _sources(segs) if infos[s]["hdr"]]
    if hdr and not tonemap:
        raise MediaError(f"HDR source ({', '.join(hdr)}): confirm SDR conversion and pass --tonemap")
    size = TARGETS[target]

    cut_wav = work / "cut_audio.wav"
    render_audio(plan, infos, cut_wav, denoise, gains)
    m = measure_loudness(cut_wav, target_i, target_tp)
    loud = (f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:measured_I={m['input_i']}:"
            f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
            f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")

    args, index = _inputs(infos, segs)
    audio_in = len(index)
    fps = infos[segs[0]["src"]]["fps"]
    parts, concat = [], ""
    for i, s in enumerate(segs):
        info = infos[s["src"]]
        pre = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
               "zscale=t=bt709:m=bt709:r=tv,format=yuv420p," if info["hdr"] else "")
        parts.append(f"[{index[s['src']]}:v:0]trim={s['start']:.5f}:{s['end']:.5f},setpts=PTS-STARTPTS,"
                     f"{pre}{_geometry(info, size, fit, crop_x)},fps={fps}[v{i}]")
        concat += f"[v{i}]"
    parts.append(f"{concat}concat=n={len(segs)}:v=1:a=0[vc]")
    burn = f",subtitles={captions_file}:fontsdir=fonts" if captions_file and (work / captions_file).exists() else ""
    parts.append(f"[vc]format=yuv420p{burn}[vo]")
    parts.append(f"[{audio_in}:a]{loud}[ao]")

    window = ["-ss", f"{sample[0]:.3f}", "-t", f"{sample[1] - sample[0]:.3f}"] if sample else []
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-v", "error", *args, "-i", cut_wav,
         "-filter_complex", ";".join(parts), "-map", "[vo]", "-map", "[ao]", *window,
         "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out.resolve()], cwd=work)
    return {"output": str(out.resolve()), "sourceLoudness": float(m["input_i"]),
            "sourceTruePeak": float(m["input_tp"]), "captions": bool(burn), "hdrConverted": bool(hdr)}
