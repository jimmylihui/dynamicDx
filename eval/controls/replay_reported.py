"""Charts with reported entries only (Appendix C.4) and decisive entries by provenance (Appendix C.6).

Replays the final diagnosis turn of each consultation on its fixed trajectory (same frames, same
history questions and answers, same orders), changing only what the chart returns.

  CELL  Vo : video trajectory, results exactly as served in the original run
        Vr : video trajectory, every derived entry withheld -> only entries reported in the source
             article are returned; an order left with no entry reads "not performed / not available"
        Oo : oracle evidence on the video history, all decisive entries
        Or : oracle evidence on the video history, only the decisive entries that are reported
        Od : oracle evidence on the video history, only the decisive entries that are derived
             (cases with any)
        Bo / Br : as Vo / Vr on the blind consultation (no frames)

The conversation is rebuilt from the saved consultation: the model's turns are its parsed questions
and its raw order text. The source runs are results/part2_<tag>_vid and results/part2_<tag>_novid
(copy them from runs/ to replay the released consultations).

usage: python eval/controls/replay_reported.py TAG CELL [threads]     env ORKEY, FFMPEG, PROVIDER
       TAG in luna | gemma | mimo | minimax | qwen38
writes results/part2_<TAG>_rep_<CELL>/<category>/<clip>.json; grade it with eval/part2_full_judge3.py
and summarise the cells with eval/controls/replay_reported_ci.py
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
import threading
import time
import urllib.request

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FF = os.environ.get("FFMPEG", "ffmpeg")
# model, provider used for the paper's runs (override with PROVIDER), reasoning enabled
CFG = {"luna": ("openai/gpt-5.6-luna", "OpenAI", True),
       "gemma": ("google/gemma-4-31b-it", "CoreWeave", True),
       "mimo": ("xiaomi/mimo-v2.5", "Xiaomi", True),
       "minimax": ("minimax/minimax-m3", "Minimax", True),
       "qwen38": ("qwen/qwen3.8-flash", "Alibaba", False)}
TAG, CELL = sys.argv[1], sys.argv[2]
NT = int(sys.argv[3]) if len(sys.argv) > 3 else 6
assert CELL in ("Vo", "Vr", "Oo", "Or", "Od", "Bo", "Br")
MODEL, PROV, REA = CFG[TAG]
PROV = os.environ.get("PROVIDER", PROV)
SRCRUN = "%s/results/part2_%s_%s" % (B, TAG, "novid" if CELL[0] == "B" else "vid")
OUT = "%s/results/part2_%s_rep_%s%s" % (B, TAG, CELL, os.environ.get("SUFFIX", ""))

SRC = open(B + "/eval/part2_full.py").read()


def grab(name):
    return re.search(r'^%s = """(.*?)"""' % name, SRC, re.S | re.M).group(1)


T1, T2, T3, T3_ORACLE, T1_NOVID = grab("T1"), grab("T2"), grab("T3"), grab("T3_ORACLE"), grab("T1_NOVID")
OPENING = "You are a doctor seeing a new patient."     # ROLE=doctor, as in the released runs
NA = "     not performed / not available"
cases = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}


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


def post(messages, mx, imgs=0):
    """no max_tokens and a 900 s timeout, as in the original runs; mx is ignored"""
    body = json.dumps({"model": MODEL, "temperature": 0, "messages": messages,
                       "reasoning": {"enabled": REA}, "usage": {"include": True},
                       "provider": {"order": [PROV], "allow_fallbacks": False}}).encode()
    for attempt in range(5):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + os.environ["ORKEY"], "Content-Type": "application/json"}),
                timeout=900).read().decode())
            if "error" in r and not r.get("choices"):
                raise RuntimeError(str(r["error"])[:200])
            pt = (r.get("usage") or {}).get("prompt_tokens", 0) or 0
            if imgs and pt < 40 * imgs:
                raise RuntimeError("IMAGES_DROPPED")
            t = r["choices"][0]["message"]["content"] or ""
            if t:
                return t, r.get("usage") or {}
        except Exception:                                              # noqa: BLE001
            time.sleep(4 * (attempt + 1))
    return "", {}


def reported_only(lines, inv):
    """drop derived entries from the served result lines; an order left empty reads not available"""
    out, block, kept = [], [], 0

    def flush():
        nonlocal block
        if block:
            out.append(block[0])
            body = block[1:]
            out.extend(body if body else [NA])
        block = []

    skipping = False
    for l in lines:
        if re.match(r"^\d+\. ", l):
            flush(); block = [l]; skipping = False; continue
        s = l.strip()
        if s == NA.strip():
            block.append(l); skipping = False; continue
        key = next((k for k in sorted(inv, key=len, reverse=True) if s.startswith(k + ":")), None)
        if key is None:                      # continuation of a multi-line value
            if not skipping:
                block.append(l)
            continue
        skipping = inv[key].get("p") == "derived"
        if skipping:
            continue
        block.append(l); kept += 1
    flush()
    return out


def run(c, src):
    fs, b64, dur = [], [], 0.0
    if CELL[0] != "B":
        tmp = tempfile.mkdtemp(prefix="rr_")
        try:
            fs, dur = frames("%s/dataset/videos/%s/%s" % (B, c["line"], c["video"]), 32, tmp)
            b64 = [base64.b64encode(open(f, "rb").read()).decode() for f in fs]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    qs, ans = src["questions"], src.get("answers") or {}
    qa = ["%d. %s  ->  %s" % (i, q, str(ans.get(str(i), "no")).lower()) for i, q in enumerate(qs, 1)]
    first = ([{"type": "text", "text": T1_NOVID}] if CELL[0] == "B" else
             [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b}} for b in b64]
             + [{"type": "text", "text": T1 % (OPENING, len(fs), "%.0f" % dur, "")}])
    msgs = [{"role": "user", "content": first},
            {"role": "assistant", "content": "\n".join("%d. %s" % (i, q) for i, q in enumerate(qs, 1))}]
    inv = c["investigations"]
    if CELL[0] in "VB":
        lines = src["results"] if CELL[1] == "o" else reported_only(src["results"], inv)
        msgs += [{"role": "user", "content": T2 % "\n".join(qa)},
                 {"role": "assistant", "content": src.get("order_raw") or "\n".join(
                     "%d. %s" % (i, t) for i, t in enumerate(src["orders"], 1))},
                 {"role": "user", "content": T3 % "\n".join(lines)}]
        served = [k for k in src.get("served") or [] if CELL[1] == "o" or inv.get(k, {}).get("p") == "reported"]
    else:
        keep = {"Oo": ("reported", "derived"), "Or": ("reported",), "Od": ("derived",)}[CELL]
        dec = [k for k, v in inv.items() if v.get("decisive") and v.get("p") in keep]
        lines = ["%d. %s: %s" % (i, k, inv[k]["v"]) for i, k in enumerate(dec, 1)]
        msgs += [{"role": "user", "content": T3_ORACLE % ("\n".join(qa), "\n".join(lines) or "(none available)")}]
        served = dec
    t_dx, u = post(msgs, 1500, len(b64))
    m = re.search(r"DIAGNOS\w*\s*:\s*(.+)", t_dx)
    return dict(cell=CELL, questions=qs, answers=ans, orders=src.get("orders") or [], served=served,
                results=lines, dx_raw=t_dx,
                dx=(m.group(1).strip() if m else (t_dx.strip().splitlines() or [""])[0]),
                decisive_served=[k for k in served if inv.get(k, {}).get("decisive")],
                n_decisive=sum(1 for v in inv.values() if v.get("decisive")),
                n_frames=len(fs), usage=u, model=MODEL, provider=PROV, reasoning=REA)


todo = sorted(glob.glob(SRCRUN + "/*/*.json"))
if os.environ.get("LIMIT"):
    todo = todo[:int(os.environ["LIMIT"])]
lock = threading.Lock()


def work():
    while True:
        with lock:
            if not todo:
                return
            f = todo.pop()
        src = json.load(open(f))
        v = src.get("video")
        if not v or src.get("error") or v not in cases:
            continue
        if CELL == "Od" and not any(x.get("decisive") and x.get("p") == "derived" for x in cases[v]["investigations"].values()):
            continue
        c = cases[v]
        out = "%s/%s/%s.json" % (OUT, c["line"], v.rsplit(".", 1)[0])
        if os.path.exists(out):
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        try:
            r = run(c, src)
        except Exception as e:                                         # noqa: BLE001
            r = dict(error="%s: %s" % (type(e).__name__, e))
        r.update(video=v, line=c["line"])
        json.dump(r, open(out, "w"), indent=1, ensure_ascii=False)
        print("%-44s %s | %s" % (v[:44], CELL, (r.get("dx") or r.get("error", ""))[:70]), flush=True)


ts = [threading.Thread(target=work) for _ in range(NT)]
[t.start() for t in ts]
[t.join() for t in ts]
print("done", TAG, CELL)
