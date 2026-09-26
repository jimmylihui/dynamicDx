"""The model's own description of the sign, separated from its differential.

Two parts of the paper start from what the model said it saw rather than from the video:
the Own words condition (Section 3.4), which hands the model its own phenomenology description in
place of the frames, and retrieval (Section 3.5.2), whose query is built from the predicted
phenomenology and never from the diagnoses the model proposed. Both read the file written here.

The Stage 1 answer is free prose ("Describe what you see, then give your primary guess of the
disease", Appendix H). DeepSeek-V4.1-Flash copies out the descriptive part and drops every
diagnosis, cause or disease category; it does not paraphrase, add findings, or see the case record.
An answer that describes nothing abnormal is kept as NONE, and the consultation harness skips it.

usage: stage1_description.py ROOT [K]      Stage 1 run under results/ROOT (default K=32)
env:   ORKEY, JUDGE (default deepseek/deepseek-v4.1-flash), JPROVIDER, OUT
out:   {video: description} for the chosen K (the SELFFILE of eval/part2_full.py) and, in the
       same file, {"<clip>__k<K>": description} for every budget (the DESCFILE of
       eval/retrieval/hpo_normalize.py)
"""
import glob
import json
import os
import re
import sys
import threading
import time
import urllib.request

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORKEY = os.environ["ORKEY"]
JUDGE = os.environ.get("JUDGE", "deepseek/deepseek-v4.1-flash")
JPROV = os.environ.get("JPROVIDER", "")
ROOT = sys.argv[1]
KSEL = int(sys.argv[2]) if len(sys.argv) > 2 else 32
OUT = os.environ.get("OUT", "%s/results/self_description_%s.json" % (B, ROOT))

P = """A model was shown frames from a video of one patient and asked to describe what it saw
and then name the disease. Its answer is below.

%s

Copy out only the part of the answer that describes what is visible in the video - the body part,
the movement or posture, its timing and side. Leave out every diagnosis, cause, disease name,
syndrome name used as a diagnosis, and any statement of what the patient might have. Keep the
model's own words; do not add, correct or summarise anything. If the answer describes nothing
abnormal, reply NONE.

Reply with the description only."""


def ask(text):
    body = json.dumps({"model": JUDGE, "temperature": 0, "max_tokens": 600,
                       "messages": [{"role": "user", "content": P % text[:12000]}],
                       **({"provider": {"order": [JPROV], "allow_fallbacks": False, "sort": "price"}}
                          if JPROV else {}),
                       "reasoning": {"enabled": False}}).encode()
    for _ in range(4):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=120).read().decode())
            t = (r["choices"][0]["message"]["content"] or "").strip()
            if t:
                return t
        except Exception:                                          # noqa: BLE001
            time.sleep(3)
    return None


jobs = []
for f in sorted(glob.glob("%s/results/%s/*/*__k*.json" % (B, ROOT))):
    d = json.load(open(f))
    txt = d.get("ans") or d.get("raw") or ""
    if d.get("video") and txt.strip():
        jobs.append(("%s__k%d" % (d["video"].rsplit(".", 1)[0], d["k"]), d["video"], d["k"], txt))
out, lock = {}, threading.Lock()


def work():
    while True:
        with lock:
            if not jobs:
                return
            key, video, k, txt = jobs.pop()
        desc = ask(txt)
        if desc is None:
            continue                                   # an API failure is not recorded as NONE
        desc = re.sub(r"^\s*(description\s*:)\s*", "", desc, flags=re.I).strip()
        with lock:
            out[key] = desc
            if k == KSEL:
                out[video] = desc


ts = [threading.Thread(target=work) for _ in range(8)]
[t.start() for t in ts]
[t.join() for t in ts]
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
n = sum(1 for k in out if k.endswith(".mp4"))
print("%s: %d descriptions at K=%d, %d in total -> %s" % (ROOT, n, KSEL, len(out), OUT))
