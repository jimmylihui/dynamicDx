"""Shared pieces of teacher-guided temporal-window training (paper Section 3.5.1, Appendix I).

Frames, folds, instructions and target parsing live here so that the teacher, the student's
training loop and its two-pass inference cannot drift apart.
"""
import io
import json
import os
import random
import re
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FF = os.environ.get("FFMPEG", "ffmpeg")
CASES = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}
CLIPS = {c["video"]: c for c in json.load(open(B + "/data/clips.json"))}
N_SURVEY = 32
BUDGETS = (8, 16, 32)

# pass 1: at most one within-shot window, or a no-window answer; no diagnosis, explanation, crop,
# zoom or frame rate (Appendix I, "Text targets and instructions")
WINDOW_INSTRUCTION = """These {n} frames are sampled evenly across a silent {duration}-second patient clip; the time
in seconds is stamped on each frame.{shots}

Say which stretch of this clip a viewer should watch more closely to see the abnormality: at most
one window, inside one shot, given by its start time and span in seconds. If these frames already
show it, answer "sufficient"; if no stretch of the recording could show it at this framing,
answer "unobtainable". Do not name a disease, explain, or ask for a crop, zoom or frame rate.

Reply with ONLY one JSON object:
{{"mode": "request", "start": SECONDS, "span": SECONDS}} or {{"mode": "sufficient"}} or {{"mode": "unobtainable"}}"""

# pass 2 (Appendix I, verbatim): N = K for a valid window, N = 32 for a fallback
RECOGNITION_INSTRUCTION = """These {N} frames are sampled from a silent patient clip. In one sentence,
say what a clinician would see - the abnormality itself, in plain physical
words. Name no disease."""


def video_path(video):
    c = CASES[video]
    return "%s/dataset/videos/%s/%s" % (B, c["line"], video)


def duration(video):
    return float(CLIPS[video]["technical"]["duration_s"])


def native_fps(video):
    return float(CLIPS[video]["technical"].get("fps") or 25.0)


def shots(video):
    """[(start, end), ...] in seconds, from the scene cuts recorded in data/clips.json"""
    d = duration(video)
    cuts = [float(t) for t in CLIPS[video]["technical"].get("cut_times") or [] if 0 < float(t) < d]
    edges = [0.0] + sorted(cuts) + [d]
    return list(zip(edges[:-1], edges[1:]))


def shots_block(video):
    s = shots(video)
    if len(s) < 2:
        return ""
    return "\nThe clip has %d shots: %s." % (len(s), "; ".join(
        "shot %d %.2f-%.2f s" % (i, a, b) for i, (a, b) in enumerate(s, 1)))


def grab(video, times, width, stamp):
    """frames at the given times (seconds), `width` px wide, JPEG q85; optional burnt-in timestamp"""
    out = []
    with tempfile.TemporaryDirectory(prefix="win_") as tmp:
        for i, t in enumerate(times):
            f = "%s/f_%03d.jpg" % (tmp, i)
            subprocess.run([FF, "-y", "-v", "error", "-ss", "%.3f" % max(t, 0.0), "-i", video_path(video),
                            "-frames:v", "1", "-vf", "scale=%d:-2" % width, "-q:v", "2", f],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if not os.path.exists(f):
                continue
            im = Image.open(f).convert("RGB")
            if stamp:
                im = burn(im, t)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=85)
            out.append(Image.open(io.BytesIO(buf.getvalue())).convert("RGB"))
    return out


def burn(im, t):
    """top-left timestamp over an opaque patch, seconds from clip start to two decimals"""
    d = ImageDraw.Draw(im)
    txt = "%.2f s" % t
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", max(12, im.width // 24))
    except OSError:
        font = ImageFont.load_default()
    x0, y0, x1, y1 = d.textbbox((0, 0), txt, font=font)
    d.rectangle([0, 0, x1 - x0 + 8, y1 - y0 + 8], fill=(0, 0, 0))
    d.text((4 - x0, 4 - y0), txt, fill=(255, 255, 255), font=font)
    return im


def even_times(start, end, n):
    """n evenly spaced sample times in [start, end) (frame centres)"""
    span = max(end - start, 1e-3)
    return [start + (i + 0.5) * span / n for i in range(n)]


def survey(video):
    """pass-1 survey: 32 uniform frames, 380 px, timestamp burnt in"""
    return grab(video, even_times(0.0, duration(video), N_SURVEY), 380, stamp=True)


def window_frames(video, start, span, k):
    """pass-2 evidence: k frames evenly within the window, 384 px, no timestamp. A short window may
    repeat source frames when k exceeds the frames available at the native recording rate."""
    return grab(video, even_times(start, start + span, k), 384, stamp=False)


def spread_frames(video, n):
    """the sign-only adapter's input: n frames evenly over the whole clip, 384 px, no timestamp"""
    return grab(video, even_times(0.0, duration(video), n), 384, stamp=False)


def window_prompt(video):
    return WINDOW_INSTRUCTION.format(n=N_SURVEY, duration="%.1f" % duration(video),
                                     shots=shots_block(video))


def last_json(text):
    """the last JSON object in a reply (teacher and student alike)"""
    for m in reversed(list(re.finditer(r"\{", text or ""))):
        depth = 0
        for j in range(m.start(), len(text)):
            depth += text[j] == "{"
            depth -= text[j] == "}"
            if depth == 0:
                try:
                    return json.loads(text[m.start():j + 1])
                except ValueError:
                    break
    return None


def parse_window(text, video):
    """student pass-1 reply -> ("request", start, span) | ("sufficient",) | ("unobtainable",) | None.
    A request is valid only if it lies inside one shot of the clip."""
    j = last_json(text)
    if not isinstance(j, dict):
        return None
    mode = str(j.get("mode", "")).lower()
    if mode in ("sufficient", "unobtainable"):
        return (mode,)
    if mode != "request":
        return None
    try:
        start, span = float(j["start"]), float(j["span"])
    except (KeyError, TypeError, ValueError):
        return None
    if span <= 0:
        return None
    for a, b in shots(video):
        if a - 1e-3 <= start and start + span <= b + 1e-3:
            return ("request", start, span)
    return None


def target_text(w):
    if w[0] == "request":
        return json.dumps({"mode": "request", "start": round(w[1], 2), "span": round(w[2], 2)})
    return json.dumps({"mode": w[0]})


def random_window(video, span, seed=0):
    """the Random arm: same duration as the predicted window, position drawn uniformly within the
    clip (seeded per clip)"""
    d = duration(video)
    span = min(span, d)
    return ("request", random.Random("random|%s|%d" % (video, seed)).uniform(0.0, d - span), span)


def folds(k=5):
    """five folds grouped by source article, fixed once and reused across budgets"""
    arts = sorted({c["source"]["pmcid"] for c in CASES.values()})
    random.Random(0).shuffle(arts)
    size = {a: sum(1 for c in CASES.values() if c["source"]["pmcid"] == a) for a in arts}
    load, assign = [0] * k, {}
    for a in sorted(arts, key=lambda a: -size[a]):            # largest articles first, stable
        f = min(range(k), key=lambda i: (load[i], i))
        assign[a] = f
        load[f] += size[a]
    return {v: assign[c["source"]["pmcid"]] for v, c in CASES.items()}


def load_targets(path):
    """teacher targets: {video: {"mode": ..., "start": .., "span": ..}}; invalid records excluded"""
    t = json.load(open(path))
    out = {}
    for v, r in t.items():
        tg = r.get("target") if isinstance(r, dict) else None
        if not tg:
            continue
        out[v] = (("request", tg["start"], tg["span"]) if tg["mode"] == "request" else (tg["mode"],))
    return out


def reference_sign(video):
    return CASES[video]["part1_video_only"]["visible_sign"]


def all_videos():
    return sorted(CASES)


def ensure_clips():
    missing = [v for v in CASES if not os.path.exists(video_path(v))]
    if missing:
        raise SystemExit("%d clips missing under dataset/videos/<line>/ (see scripts/fetch_videos.py), "
                         "e.g. %s" % (len(missing), missing[0]))

