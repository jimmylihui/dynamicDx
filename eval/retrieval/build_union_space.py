"""Build the candidate space the deployed system would actually have.

Section 5.2 showed the model's own differential and literature retrieval recover different
patients: they agree on 5-7 clips and retrieval adds 5-11 the model never proposed, so the union
covers 7-16 points more than either alone. The Part 2 model arm was given only the retrieved half,
and gained nothing. This builds the union - the diagnoses the model itself offered from the video,
followed by the causes retrieved for the sign it described - so the consultation can be run on the
candidate set that actually has the better coverage.

The model's own hypotheses are extracted from its K=32 free-prose answer by a judge that only
lists what is there.
"""
import glob
import json
import os
import re
import threading
import time
import urllib.request

B = os.environ.get("DDX_ROOT", ".")
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

SPACEFILE = os.environ.get("SPACEFILE", os.environ.get("DDX_WORK", "/tmp") + "/openspace_part1_oldp_%s.json" % TAG)
OUTFILE = os.environ.get("OUTFILE", os.environ.get("DDX_WORK", "/tmp") + "/openspace_union.json")
space = json.load(open(SPACEFILE))
answers = {}
ANSROOT = os.environ.get("ANSROOT", "part1_oldp_%s" % TAG)
for f in glob.glob("%s/results/%s/*/*.json" % (B, ANSROOT)):
    d = json.load(open(f))
    if d.get("k") == 32 and (d.get("ans") or d.get("raw")):
        answers[os.path.basename(f).split("__")[0] + ".mp4"] = d.get("ans") or d.get("raw")

out, lock = {}, threading.Lock()
q = list(answers.items())


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
json.dump(out, open(os.environ.get("DDX_WORK", "/tmp") + "/own_dx_%s.json" % TAG, "w"), indent=1, ensure_ascii=False)

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
n = len(union)
print("cases with a union space : %d" % n)
print("own hypotheses per case  : %.1f" % (sum(v["n_own"] for v in union.values()) / n))
print("retrieved causes per case: %.1f" % (sum(v["n_ret"] for v in union.values()) / n))
print("union size per case      : %.1f" % (sum(len(v["causes"]) for v in union.values()) / n))
print("cases where retrieval was empty: %d" % sum(1 for v in union.values() if not v["n_ret"]))
