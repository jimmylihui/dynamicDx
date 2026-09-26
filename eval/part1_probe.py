"""Part 1 of the benchmark: what can a model read off the video ALONE, as a function of how many
frames it is shown.

No history, no transcript, no investigations - just K frames sampled evenly across the clip and
the question the case file already defines in part1_video_only. The point of the sweep is that
these clips carry the diagnosis in MOVEMENT, so a single frame should be near-useless and the
score should climb with K until the sampling rate stops mattering.

usage: part1_probe.py VIDEO K OUT.json
env:   BACKEND  or | ollama          (default or)
       ORKEY    OpenRouter API key   (required when BACKEND=or)
       MODEL    default google/gemma-4-31b-it on the API, gemma4:31b on Ollama
       PROVIDER pinned OpenRouter provider, default CoreWeave
       PROMPT   new | old (default old, the prompt reported in the paper). The old prompt is the one the earlier open-probe runs
                used, recovered from the session log: free prose, no output schema, no list of
                example signs, no cap on the number of diagnoses. The new prompt names seven
                example signs - chorea, dystonia, ataxic gait, ptosis, facial weakness, freezing
                of gait, resting tremor - which between them cover most of the disease lines, so
                any sign-recognition rate measured with it is inflated by the prompt. Running
                both is the only way to separate the model from the wording.
       MAXTOK   completion budget, default 700. The old prompt asks for prose, and a model that
                also emits a reasoning trace can spend the whole budget before answering - raise
                it for those.
       PROVIDER=auto skips the pin entirely, for models whose cheapest endpoints cannot see
                images.
       REASONING  off | on (default off, as the Stage 2 harness). gemma-4-31b-it emits no reasoning tokens at all, so a
                  comparison against a reasoning model confounds the model with the presence of
                  a reasoning trace; REASONING=off matches the conditions. Note that turning it
                  off does NOT make the model reproducible - three repeats at temperature 0 still
                  differ, with or without reasoning.
       OLLAMA   default http://localhost:11434
       FFMPEG

The API path carries the images-dropped guard the other OpenRouter scripts use. Some providers
silently strip images and answer from the text alone, which scores as a blind model rather than
as a failure; a reply whose prompt_tokens are far too low for the number of images sent is
rejected and retried rather than recorded.

The provider is PINNED with fallbacks off. OpenRouter serves this model from 18 endpoints whose
quantisation runs from fp4 to bf16, and it round-robins between them - three consecutive test
calls landed on Together, OpenInference and Friendli. A frame-count curve measured across mixed
quantisations is not measuring frame count. CoreWeave is the default because it is bf16 at the
lowest bf16 price.
"""
import base64
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

VIDEO, K, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
BACKEND = os.environ.get("BACKEND", "or")
MODEL = os.environ.get("MODEL",
                       "gemma4:31b" if BACKEND == "ollama" else "google/gemma-4-31b-it")
HOST = os.environ.get("OLLAMA", "http://localhost:11434")
ORKEY = os.environ.get("ORKEY")
PROVIDER = os.environ.get("PROVIDER", "CoreWeave")
REASONING = os.environ.get("REASONING", "off")   # as the Stage 2 harness
MAXTOK = int(os.environ.get("MAXTOK", "700"))
FF = os.environ.get("FFMPEG", "ffmpeg")

PROMPT = os.environ.get("PROMPT", "old")

ASK_OLD = (
    "You are a doctor. Below are %d frame(s) sampled in order across a ~%s second video of a "
    "patient.\n\n"
    "Describe what you see, then give your primary guess of the disease. "
    "You may list several possible diagnoses.\n"
)

ASK = (
    "You are a neurologist. Above are %d still frames sampled evenly across a %s-second clinical "
    "video of ONE patient, in chronological order. Read them as the video.\n\n"
    "You have NO history, NO examination findings and NO test results. Judge from the frames "
    "alone.\n\n"
    "Reply with ONLY a JSON object, no prose around it, with these keys:\n"
    '  "motion": what movement or postural abnormality you can actually see (one sentence; write '
    '"none visible" if the frames show no abnormal movement)\n'
    '  "sign": the named clinical sign, if you can name one (e.g. chorea, dystonia, ataxic gait, '
    'ptosis, facial weakness, freezing of gait, resting tremor); "uncertain" if not\n'
    '  "body_region": where it is (face / eyes / one arm / both legs / trunk / whole body)\n'
    '  "dx1": your single most likely disease\n'
    '  "dx2": second possibility\n'
    '  "dx3": third possibility\n'
    '  "confidence": low | moderate | high\n'
)


def duration(path):
    out = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 20.0


def sample(path, k, tmp):
    """k frames evenly across the clip. k=1 takes the middle frame, not the first - the first
    frame of a clinical video is often the patient still at rest."""
    dur = duration(path)
    if k == 1:
        subprocess.run([FF, "-y", "-ss", "%.3f" % (dur / 2), "-i", path, "-frames:v", "1",
                        "-vf", "scale=512:-1", tmp + "/f_001.jpg"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run([FF, "-y", "-i", path, "-vf",
                        "fps=%.5f,scale=512:-1" % (k / max(dur, 0.1)),
                        "-frames:v", str(k), tmp + "/f_%03d.jpg"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sorted(glob.glob(tmp + "/*.jpg")), dur


def call_ollama(images, ask):
    body = json.dumps({
        "model": MODEL, "stream": False,
        "options": {"temperature": 0, "num_ctx": 16384},
        "messages": [{"role": "user", "content": ask, "images": images}],
    }).encode()
    req = urllib.request.Request(HOST + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=1800).read().decode())
    return r.get("message", {}).get("content", ""), {}, "ollama"


def call_or(images, ask):
    """The prompt ("Below are <K> frame(s) ...") comes first and the frames follow it (Appendix H)."""
    content = ([{"type": "text", "text": ask}]
               + [{"type": "image_url",
                   "image_url": {"url": "data:image/jpeg;base64," + b}} for b in images])
    payload = {"model": MODEL, "temperature": 0, "max_tokens": MAXTOK,
               "messages": [{"role": "user", "content": content}],
               "usage": {"include": True}}
    if PROVIDER != "auto":
        payload["provider"] = {"order": [PROVIDER], "allow_fallbacks": False, "sort": "price"}
    if REASONING == "off":
        payload["reasoning"] = {"enabled": False}
    body = json.dumps(payload).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                                 headers={"Authorization": "Bearer " + ORKEY,
                                          "Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=900).read().decode())
    if "error" in r and not r.get("choices"):
        raise RuntimeError(str(r["error"])[:200])
    usage = r.get("usage", {}) or {}
    prov = r.get("provider", "?")
    pt = usage.get("prompt_tokens", 0) or 0
    if images and pt < 40 * len(images):
        raise RuntimeError("IMAGES_DROPPED by %s (prompt_tokens=%d for %d images)"
                           % (prov, pt, len(images)))
    usage["finish_reason"] = r.get("choices", [{}])[0].get("finish_reason")
    return r.get("choices", [{}])[0].get("message", {}).get("content", ""), usage, prov


def call(images, ask):
    return call_ollama(images, ask) if BACKEND == "ollama" else call_or(images, ask)


tmp = tempfile.mkdtemp(prefix="part1_")
try:
    frames, dur = sample(VIDEO, K, tmp)
    if not frames:
        raise SystemExit("no frames extracted from " + VIDEO)
    b64 = [base64.b64encode(open(f, "rb").read()).decode() for f in frames]
    ask = (ASK_OLD if PROMPT == "old" else ASK) % (len(frames), "%.0f" % dur)

    txt, err, usage, prov, t0 = None, None, {}, None, time.time()
    for attempt in range(5):
        try:
            txt, usage, prov = call(b64, ask)
            if txt:
                break
        except Exception as e:                                    # noqa: BLE001
            err = "%s: %s" % (type(e).__name__, e)
            time.sleep(5 * (attempt + 1))
    elapsed = round(time.time() - t0, 1)

    parsed, raw = None, txt or ""
    if txt and PROMPT != "old":            # the old prompt asks for prose; there is nothing to parse
        m = re.search(r"\{.*\}", txt, re.S)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception:                                     # noqa: BLE001
                parsed = None

    json.dump(dict(video=os.path.basename(VIDEO), k=K, n_frames=len(frames),
                   duration_s=round(dur, 1), model=MODEL, backend=BACKEND, provider=prov,
                   reasoning=REASONING, prompt=PROMPT,
                   elapsed_s=elapsed, usage=usage, parsed=parsed, raw=raw,
                   error=None if txt else err),
              open(OUT, "w"), indent=1, ensure_ascii=False)
    shown = ((parsed or {}).get("dx1") if PROMPT != "old"
             else " ".join(raw.split())[:60]) or ("PARSE_FAIL" if txt else "NO_REPLY")
    print("%-52s k=%-3d frames=%-3d %6.1fs %s"
          % (os.path.basename(VIDEO), K, len(frames), elapsed, shown))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
