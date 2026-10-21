"""Brand captions as ASS (burned in) and SRT/VTT sidecars, from words already in output time."""
from __future__ import annotations

import re

# Inter for speech, JetBrains Mono for code, commands and tool names (brand/design-guide.md).
LAYOUTS = {
    # PlayRes, font size, box padding, anchor. Vertical anchor keeps text inside
    # x 140-940, y 230-1530 and out of the bottom 20% that Reels/TikTok UI covers.
    "vertical": {"w": 1080, "h": 1920, "size": 68, "pad": 16, "x": 540, "y": 1330, "chars": 22},
    "horizontal": {"w": 1920, "h": 1080, "size": 54, "pad": 12, "x": 960, "y": 950, "chars": 40},
}
CODE = re.compile(r"[_/\\(){}\[\]<>=`]|[A-Za-z]\.[A-Za-z]|^-{1,2}[a-z]|[a-z][A-Z]")
FORBIDDEN = re.compile("[—–]|[\U0001F300-\U0001FAFF☀-➿]")


def layout_for(width, height):
    return LAYOUTS["vertical" if height > width else "horizontal"]


def _clean(token):
    return re.sub(r"[,.;:]+$", "", token)


def _apply_corrections(words, corrections):
    if not corrections:
        return words
    out = []
    for w in words:
        text = w["w"]
        for wrong, right in corrections.items():
            text = re.sub(rf"(?<!\w){re.escape(wrong)}(?!\w)", right, text)
        out.append({**w, "w": text})
    return out


def group(words, max_words=3, max_chars=22, gap=0.4):
    groups, cur = [], []
    for w in words:
        if cur:
            text_len = len(" ".join(x["w"] for x in cur + [w]))
            if (len(cur) >= max_words or text_len > max_chars or w["s"] - cur[-1]["e"] > gap
                    or re.search(r"[,.?!;:]$", cur[-1]["w"])):
                groups.append(cur)
                cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    return groups


def cues(words, max_words=3, max_chars=22, corrections=None, hold=0.15, min_dur=0.3):
    groups = group(_apply_corrections(words, corrections), max_words, max_chars)
    out = []
    for i, g in enumerate(groups):
        start, end = g[0]["s"], g[-1]["e"] + hold
        nxt = groups[i + 1][0]["s"] if i + 1 < len(groups) else None
        if nxt is not None:
            end = min(end, nxt)
        if end - start < min_dur:
            end = start + min_dur if nxt is None else min(start + min_dur, nxt)
        out.append({"start": round(start, 3), "end": round(end, 3),
                    "tokens": [_clean(w["w"]) for w in g if _clean(w["w"])]})
    return out


def _is_code(token, mono_terms):
    return bool(CODE.search(token)) or token.lower() in mono_terms


def _ts_ass(t):
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def _ts_srt(t, sep=","):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}"


def _ass_escape(text):
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def to_ass(cue_list, layout, mono_terms=()):
    mono = {word.lower() for term in mono_terms for word in term.split()}
    L = layout
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {L['w']}
PlayResY: {L['h']}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter,{L['size']},&H00FFFFFF,&H00FFFFFF,&H001A1A1A,&H001A1A1A,0,0,0,0,100,100,0,0,3,{L['pad']},0,5,140,140,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for c in cue_list:
        parts = []
        for tok in c["tokens"]:
            t = _ass_escape(tok)
            parts.append(f"{{\\fnJetBrains Mono Medium}}{t}{{\\fnInter}}" if _is_code(tok, mono) else t)
        lines.append(f"Dialogue: 0,{_ts_ass(c['start'])},{_ts_ass(c['end'])},Cap,,0,0,0,,"
                     f"{{\\pos({L['x']},{L['y']})}}{' '.join(parts)}")
    return head + "\n".join(lines) + "\n"


def to_srt(cue_list):
    blocks = [f"{i}\n{_ts_srt(c['start'])} --> {_ts_srt(c['end'])}\n{' '.join(c['tokens'])}\n"
              for i, c in enumerate(cue_list, 1)]
    return "\n".join(blocks)


def to_vtt(cue_list):
    blocks = [f"{_ts_srt(c['start'], '.')} --> {_ts_srt(c['end'], '.')}\n{' '.join(c['tokens'])}\n"
              for c in cue_list]
    return "WEBVTT\n\n" + "\n".join(blocks)


def lint(cue_list, words):
    """Text-level checks that stand in for OCR: coverage and brand rules."""
    issues = []
    spoken = sum(1 for w in words if _clean(w["w"]))
    shown = sum(len(c["tokens"]) for c in cue_list)
    if shown != spoken:
        issues.append(f"caption words {shown} != spoken words {spoken}")
    for c in cue_list:
        text = " ".join(c["tokens"])
        if FORBIDDEN.search(text):
            issues.append(f"em dash or emoji at {c['start']:.2f}s: {text}")
        if "[?]" in text:
            issues.append(f"unresolved word at {c['start']:.2f}s: {text}")
    return issues
