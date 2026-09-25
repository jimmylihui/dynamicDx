"""Part 2 replayed with a lying patient, re-running the investigation turn as well.

The doctor's questions are held at what the original run asked - the patient has not yet spoken
when they are put, so a lie cannot change them. Everything downstream is re-run: a fixed fraction
of the yes/no/unknown replies is flipped, the doctor orders investigations against the corrupted
history, the chart answers those orders, and the doctor diagnoses. Every flip is a lie: yes->no
denies a documented feature, no->yes and unknown->yes assert one the record does not support
(paper Appendix G).

Output is written in the same schema as part2_full.py, so part2_full_judge3.py grades it unchanged.

usage: part2_lie2.py [NTHREADS]
env:   ORKEY, SRCRUN, RATIO (percent of answers flipped), OUTROOT, MODEL, PROVIDER, REASONING
"""
import base64
import glob
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

B = os.environ.get("DDX_ROOT", ".")
ORKEY = os.environ["ORKEY"]
MODEL = os.environ.get("MODEL", "openai/gpt-5.6-luna")
JUDGE = os.environ.get("JUDGE", "openai/gpt-5.6-luna")
PROVIDER = os.environ.get("PROVIDER", "OpenAI")
JPROVIDER = os.environ.get("JPROVIDER", "OpenAI")
REASONING = json.loads(os.environ.get("REASONING", '{"enabled": true}'))
K = int(os.environ.get("KFRAMES", "32"))
TIMEOUT = int(os.environ.get("TIMEOUT", "90"))
FF = os.environ.get("FFMPEG", os.environ.get("FFMPEG", "ffmpeg"))
SRCRUN = os.environ.get("SRCRUN", "part2_lunathink_vid_doctor")
RATIO = int(os.environ.get("RATIO", "40"))
SEED = int(os.environ.get("SEED", "0"))
OUTROOT = os.environ.get("OUTROOT", "part2_lie%d_luna" % RATIO)
ONLY = [x for x in os.environ.get("ONLY", "").split(",") if x]

_src = open(B + "/eval/part2_full.py").read()
T1 = re.search(r'\nT1 = """(.*?)"""', _src, re.S).group(1)
T2 = re.search(r'\nT2 = """(.*?)"""', _src, re.S).group(1)
T3 = re.search(r'\nT3 = """(.*?)"""', _src, re.S).group(1)
MATCH_I = re.search(r'\nMATCH_I = """(.*?)"""', _src, re.S).group(1)
_OPENING = "You are a doctor seeing a new patient."


def _prov(model):
    return JPROVIDER if model == JUDGE and JUDGE != MODEL else PROVIDER


def duration(p):
    o = subprocess.run([FF, "-i", p], capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", o)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 20.0


def frames(p, k, tmp):
    d = duration(p)
    subprocess.run([FF, "-y", "-i", p, "-vf", "fps=%.5f,scale=512:-1" % (k / max(d, 0.1)),
                    "-frames:v", str(k), tmp + "/f_%03d.jpg"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sorted(glob.glob(tmp + "/*.jpg")), d


def post(model, messages, mx=0, imgs=0, reasoning=None):
    payload = {"model": model, "temperature": 0, "messages": messages,
               "reasoning": REASONING if reasoning is None else reasoning,
               "usage": {"include": True},
               "provider": {"order": [_prov(model)], "allow_fallbacks": False, "sort": "price"}}
    if mx:
        payload["max_tokens"] = mx
    body = json.dumps(payload).encode()
    for attempt in range(5):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=TIMEOUT).read().decode())
            if "error" in r and not r.get("choices"):
                raise RuntimeError(str(r["error"])[:200])
            pt = (r.get("usage") or {}).get("prompt_tokens", 0) or 0
            if imgs and pt < 40 * imgs:
                raise RuntimeError("IMAGES_DROPPED %d/%d" % (pt, imgs))
            ch = r["choices"][0]
            t = ch["message"]["content"] or ""
            u = dict(r.get("usage") or {})
            u["finish_reason"] = ch.get("finish_reason")
            if t:
                return t, u
        except Exception:                                          # noqa: BLE001
            time.sleep(4 * (attempt + 1))
    return "", {}


def as_json(txt):
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except Exception:                                              # noqa: BLE001
        return None


def numbered(txt):
    out = []
    for line in txt.splitlines():
        if re.match(r"^\s*\d+[.)]", line):
            s = re.sub(r"^\s*\d+[.)]\s*", "", line).strip().strip("*").strip()
            if 3 < len(s) < 600:
                out.append(s)
    return out


cases = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}
todo = sorted(glob.glob("%s/results/%s/*/*.json" % (B, SRCRUN)))
if ONLY:
    todo = [f for f in todo if os.path.basename(f)[:-5] in ONLY]
print("RATIO=%d%% src=%s -> %d cases -> results/%s" % (RATIO, SRCRUN, len(todo), OUTROOT),
      flush=True)
lock = threading.Lock()


def run(src):
    d = json.load(open(src))
    c = cases[d["video"]]
    qs = d["questions"]
    truth = [str(d["answers"].get(str(i), "unknown")).lower() for i in range(1, len(qs) + 1)]
    truth = [t if t in ("yes", "no") else "unknown" for t in truth]

    nflip = int(round(len(qs) * RATIO / 100.0))
    rng = random.Random(hash((d["video"], RATIO, SEED)) & 0xFFFFFFFF)
    idx = sorted(rng.sample(range(len(qs)), nflip))
    a = list(truth)
    for i in idx:
        a[i] = "no" if a[i] == "yes" else "yes"      # yes->no; no->yes; unknown->yes

    tmp = tempfile.mkdtemp(prefix="lie2_")
    try:
        fs, dur = frames("%s/dataset/videos/%s/%s" % (B, c["line"], c["video"]), K, tmp)
        b64 = [base64.b64encode(open(f, "rb").read()).decode() for f in fs]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    content1 = ([{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b}}
                 for b in b64]
                + [{"type": "text", "text": T1 % (_OPENING, len(fs), "%.0f" % dur, "")}])
    qa = ["%d. %s  ->  %s" % (i + 1, q, a[i]) for i, q in enumerate(qs)]
    msgs = [{"role": "user", "content": content1},
            {"role": "assistant",
             "content": "\n".join("%d. %s" % (i, q) for i, q in enumerate(qs, 1))},
            {"role": "user", "content": T2 % "\n".join(qa)}]
    t_ord, u2 = post(MODEL, msgs, imgs=len(b64))
    tests = [t.split("---", 1)[0].strip() for t in numbered(t_ord)]
    if not tests:
        return dict(error="no orders")

    inv = c["investigations"]
    menu = "\n".join("- %s%s" % (k, " [NAMED-ONLY]" if v.get("explicit_only") else "")
                     for k, v in inv.items())
    t_cov, u_cov = post(JUDGE, [{"role": "user", "content": MATCH_I % (
        "\n".join("%d. %s" % (i, t) for i, t in enumerate(tests, 1)), menu)}])
    cov = as_json(t_cov) or {}
    lines, served = [], []
    for i, t in enumerate(tests, 1):
        got = [k for k in (cov.get(str(i)) or []) if k in inv]
        lines.append("%d. %s" % (i, t))
        if not got:
            lines.append("     not performed / not available")
            continue
        for k in got:
            served.append(k)
            lines.append("     %s: %s" % (k, inv[k]["v"]))

    msgs += [{"role": "assistant", "content": t_ord},
             {"role": "user", "content": T3 % "\n".join(lines)}]
    t_dx, u3 = post(MODEL, msgs)
    m = re.search(r"DIAGNOS\w*\s*:\s*(.+)", t_dx)
    return dict(questions=qs, answers={str(i + 1): v for i, v in enumerate(a)},
                truthful_answers={str(i + 1): v for i, v in enumerate(truth)},
                flipped=[i + 1 for i in idx], ratio=RATIO,
                n_fabricated=sum(1 for i in idx if truth[i] != "yes"),
                n_denied=sum(1 for i in idx if truth[i] == "yes"),
                n_yes_answers=sum(1 for v in a if v == "yes"),
                orders=tests, served=served, results=lines, dx_raw=t_dx,
                order_raw=t_ord, order_style="open", novideo=False, role="doctor",
                dx=(m.group(1).strip() if m else (t_dx.strip().splitlines() or [""])[0]),
                decisive_served=[k for k in served if inv[k].get("decisive")],
                n_decisive=sum(1 for v in inv.values() if v.get("decisive")),
                orig_orders=d["orders"], orig_served=d["served"],
                orig_decisive_served=d["decisive_served"], orig_dx=d["dx"],
                usage=dict(order=u2, dx=u3, cov=u_cov), n_frames=len(fs), duration_s=round(dur, 1),
                video=d["video"], line=c["line"], model=MODEL, reasoning=REASONING)


def work():
    while True:
        with lock:
            if not todo:
                return
            src = todo.pop()
        out = "%s/results/%s/%s/%s" % (B, OUTROOT, src.split("/")[-2], os.path.basename(src))
        if os.path.exists(out):
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        t0 = time.time()
        try:
            r = run(src)
        except Exception as e:                                     # noqa: BLE001
            r = dict(error=str(e)[:200])
        r["elapsed_s"] = round(time.time() - t0, 1)
        json.dump(r, open(out, "w"), indent=1, ensure_ascii=False)
        print("%-52s %-9s %s" % (os.path.basename(src)[:-5], r.get("error", "ok"),
                                 (r.get("dx") or "")[:70]), flush=True)


ts = [threading.Thread(target=work) for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6)]
[t.start() for t in ts]
[t.join() for t in ts]
