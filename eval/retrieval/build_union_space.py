"""Candidate list for the retrieval conditions (Section 3.5.2): the model's own video-only
differential followed by the retrieved causes.

The model's own hypotheses are extracted once from its K=32 Stage 1 answer by a DeepSeek prompt
that only lists what is there, and cached in own_dx_<TAG>.json (the Own candidates list), so that
Original, Source-clean and Strict no-answer all start from the same own differential.

usage: TAG=luna SPACEFILE=<openspace.py output> [ANSROOT=part1_luna] [OUTFILE=...] build_union_space.py
"""
import glob
import json
import os
import re
import sys
import threading
import time
import urllib.request

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ORKEY = os.environ["ORKEY"]
JUDGE = os.environ.get("JUDGE", "deepseek/deepseek-v4.1-flash")
JPROV = os.environ.get("JPROVIDER", "")
TAG = os.environ.get("TAG", "luna")

P = """A model was shown frames from a video of one patient and asked to describe what it saw and
name the disease.

%s

List every distinct diagnosis the answer offers, in the order it presents them. Copy the names it
uses; do not add, rename, or infer any diagnosis it did not state.

Reply with ONLY a JSON array of strings."""

SPACEFILE = os.environ.get("SPACEFILE", os.environ.get("DDX_WORK", "/tmp") + "/openspace_part1_%s_clean.json" % TAG)   # drive_decontam.sh output
OUTFILE = os.environ.get("OUTFILE", os.path.join(os.path.dirname(SPACEFILE),
                         "union_" + os.path.basename(SPACEFILE)))   # one file per filter
space = json.load(open(SPACEFILE))
answers = {}
ANSROOT = os.environ.get("ANSROOT", "part1_%s" % TAG)
for f in glob.glob("%s/results/%s/*/*.json" % (B, ANSROOT)):
    d = json.load(open(f))
    if d.get("k") == 32 and (d.get("ans") or d.get("raw")):
        answers[os.path.basename(f).split("__")[0] + ".mp4"] = d.get("ans") or d.get("raw")

OWNFILE = os.environ.get("OWNFILE", os.environ.get("DDX_WORK", "/tmp") + "/own_dx_%s.json" % TAG)
out, lock = {}, threading.Lock()
if os.path.exists(OWNFILE):                        # extracted once, reused by every filter
    out = json.load(open(OWNFILE))
q = [(v, a) for v, a in answers.items() if v not in out]
if not answers and not out:
    sys.exit("no Stage 1 answers under results/%s (set ANSROOT)" % ANSROOT)


def ask(p):
    body = json.dumps({"model": JUDGE, "temperature": 0, "max_tokens": 400,
                       "messages": [{"role": "user", "content": p}],
                       **({"provider": {"order": [JPROV], "allow_fallbacks": False, "sort": "price"}} if JPROV else {}),
                       "reasoning": {"enabled": False}}).encode()
    for _ in range(4):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=120).read().decode())
            m = re.search(r"\[.*\]", r["choices"][0]["message"]["content"] or "", re.S)
            if m:
                return json.loads(m.group(0))
        except Exception:                                          # noqa: BLE001
            time.sleep(3)
    return None


def work():
    while True:
        with lock:
            if not q:
                return
            vid, ans = q.pop()
        r = ask(P % ans[:6000])
        with lock:
            out[vid] = [str(x) for x in (r or []) if isinstance(x, (str,))][:12]


ts = [threading.Thread(target=work) for _ in range(8)]
[t.start() for t in ts]
[t.join() for t in ts]
json.dump(out, open(OWNFILE, "w"), indent=1, ensure_ascii=False)

union = {}
for vid, own in out.items():
    ret = (space.get(vid) or {}).get("causes") or []
    seen, merged = set(), []
    for c in list(own) + list(ret):                # the model's own hypotheses lead
        k = c.strip().lower()
        if k and k not in seen:
            seen.add(k)
            merged.append(c)
    if merged:
        union[vid] = dict(line=(space.get(vid) or {}).get("line"), causes=merged,
                          n_own=len(own), n_ret=len(ret))
json.dump(union, open(OUTFILE, "w"), indent=1, ensure_ascii=False)
n = max(len(union), 1)
print("cases with a union space : %d" % n)
print("own hypotheses per case  : %.1f" % (sum(v["n_own"] for v in union.values()) / n))
print("retrieved causes per case: %.1f" % (sum(v["n_ret"] for v in union.values()) / n))
print("union size per case      : %.1f" % (sum(len(v["causes"]) for v in union.values()) / n))
print("cases where retrieval was empty: %d" % sum(1 for v in union.values() if not v["n_ret"]))
