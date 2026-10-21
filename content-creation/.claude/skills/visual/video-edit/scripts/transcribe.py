"""Local word-level transcription with faster-whisper, plus the take view Claude cuts from."""
from __future__ import annotations

import re

from media import load_audio

DEFAULT_MODEL = "large-v3-turbo"
SR = 16000


def _model(name, device, local_only):
    from faster_whisper import WhisperModel
    compute = "float16" if device == "cuda" else "int8"
    return WhisperModel(name, device=device, compute_type=compute, local_files_only=local_only)


def transcribe(path, language=None, model=DEFAULT_MODEL, prompt=None, device="cpu") -> dict:
    # Decode with FFmpeg ourselves: the bundled PyAV rejects some containers.
    audio = load_audio(path, SR)
    segments, info = _model(model, device, False).transcribe(
        audio, language=language, word_timestamps=True, initial_prompt=prompt,
        condition_on_previous_text=False, vad_filter=False)
    words = []
    for seg in segments:
        for w in seg.words or []:
            text = w.word.strip()
            if text:
                words.append({"w": text, "s": round(w.start, 3), "e": round(w.end, 3),
                              "p": round(w.probability, 3)})
    return {"language": info.language, "languageProbability": round(info.language_probability, 3),
            "duration": round(len(audio) / SR, 3), "model": model, "prompt": prompt, "words": words}


def sample_language(path, seconds=30, model=DEFAULT_MODEL):
    """Bounded, cache-only language sample for the settings card. None when the model isn't cached."""
    try:
        m = _model(model, "cpu", True)
    except Exception:
        return None
    audio = load_audio(path, SR, start=0, duration=seconds)
    if audio.size < SR:
        return None
    _, info = m.transcribe(audio, word_timestamps=False, condition_on_previous_text=False)
    return {"language": info.language, "probability": round(info.language_probability, 3),
            "sampledSeconds": round(audio.size / SR, 1)}


def takes(words, gap=0.5, low_conf=0.5):
    """Split words into lines at pauses so repeated takes and false starts are visible."""
    lines, cur = [], []
    for i, w in enumerate(words):
        if cur and (w["s"] - cur[-1]["e"] >= gap
                    or (re.search(r"[.?!]$", cur[-1]["w"]) and w["s"] - cur[-1]["e"] >= 0.3)):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    out = []
    prev_end = 0.0
    for idx, line in enumerate(lines):
        text = " ".join(w["w"] + ("[?]" if w["p"] < low_conf else "") for w in line)
        out.append({"n": idx + 1, "start": line[0]["s"], "end": line[-1]["e"],
                    "pauseBefore": round(line[0]["s"] - prev_end, 2), "text": text})
        prev_end = line[-1]["e"]
    return out


def takes_markdown(sources_words) -> str:
    rows = ["# Takes", "", "Times are source seconds. `[?]` = low-confidence word, listen before trusting it.", ""]
    for src, words in enumerate(sources_words):
        rows.append(f"## Source {src}")
        rows.append("")
        for t in takes(words):
            rows.append(f"- L{t['n']:03d} `{t['start']:8.2f} - {t['end']:8.2f}` "
                        f"(pause {t['pauseBefore']:.2f}) {t['text']}")
        rows.append("")
    return "\n".join(rows)
