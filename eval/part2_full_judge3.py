"""Grade the end-to-end diagnosis (paper Appendix H, Part 2).

Three grades, against the case's final-diagnosis acceptance lists (`final_diagnosis` in
data/cases.json):
  accurate - matches a case-specific accepted correct diagnosis, including an accepted broader
             disease or syndrome formulation
  partial  - matches the case-specific partial-credit criteria but not the correct-answer criteria
  none     - satisfies neither

Graded from the doctor's stated primary diagnosis. Alternatives are recorded but not credited:
a consultation that ends in "one of these four things" has not diagnosed the patient.
Accuracy is the ACCURATE rate with 71 as denominator.
"""
import glob
import json
import os
import re
import sys
import threading
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tau import acquired, DEC                                     # noqa: E402

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORKEY = os.environ["ORKEY"]
JUDGE = os.environ.get("JUDGE", "openai/gpt-5.6-luna")
ROOT = os.environ.get("ROOT", "part2_full_none")
cases = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}

P = """You are grading a doctor who watched a video of a patient, took a yes/no history,
ordered investigations, and then named a diagnosis.

GROUND TRUTH
  true diagnosis : %s
  count as accurate (the actual disease entity) : %s
  Accepted as partial: %s

THE DOCTOR'S PRIMARY DIAGNOSIS
%s

Grade the primary diagnosis alone.
  accurate : matches a case-specific accepted correct diagnosis,
             including an accepted broader disease or syndrome
             formulation; equivalent clinical terminology counts
  partial  : matches the case-specific partial-credit criteria,
             including a related syndrome, cause, or broad disease
             family, but does not satisfy the correct-answer criteria
  none     : satisfies neither the correct-answer criteria nor
             the partial-credit criteria

Reply with ONLY {"grade":"accurate|partial|none","reason":"<= 12 words"}"""

res, lock = {}, threading.Lock()
q = sorted(glob.glob("%s/results/%s/*/*.json" % (B, ROOT)))


def ask(p):
    body = json.dumps({"model": JUDGE, "temperature": 0,
                       "messages": [{"role": "user", "content": p}],
                       "provider": {"order": [os.environ.get("JUDGE_PROVIDER","OpenAI")], "allow_fallbacks": False,
                                    "sort": "price"},
                       "max_tokens": int(os.environ.get("MAXTOK", "8000")),
                       }).encode()
    for _ in range(4):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=120).read().decode())
            m = re.search(r"\{.*\}", r["choices"][0]["message"]["content"] or "", re.S)
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
            f = q.pop()
        d = json.load(open(f))
        if not d.get("video"):          # a case the source run failed on: nothing to grade
            continue
        c = cases.get(d["video"])
        if not c or not d.get("dx"):
            continue
        fd = c["final_diagnosis"]
        v = ask(P % (c["true_diagnosis"], fd.get("accept_as_accurate"), fd.get("accept_as_partial"),
                     d["dx"]))
        with lock:
            res[d["video"]] = dict(line=c["line"], dx=d["dx"], grade=(v or {}).get("grade"),
                                   reason=(v or {}).get("reason"),
                                   n_dec=len(DEC[d["video"]]),
                                   dec_served=len(acquired(d["video"], d.get("served"))),
                                   n_q=len(d.get("questions") or []),
                                   n_yes=d.get("n_yes_answers", 0),
                                   n_orders=len(d.get("orders") or []),
                                   n_served=len(d.get("served") or []))


ts = [threading.Thread(target=work) for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6)]
[t.start() for t in ts]
[t.join() for t in ts]
json.dump(res, open(B + "/results/stage2%s_%s.json" % (os.environ.get("OUTTAG", ""), ROOT), "w"), indent=1, ensure_ascii=False)

ok = [r for r in res.values() if r["grade"]]
n = len(ok)
g = {k: sum(1 for r in ok if r["grade"] == k) for k in ("accurate", "partial", "none")}
print("cases              : %d" % n)
print("ACCURATE (of 71)   : %.1f%% (%d)" % (100.0 * g["accurate"] / 71, g["accurate"]))
print("ACCURATE + PARTIAL : %.1f%% (%d)" % (100.0 * (g["accurate"] + g["partial"]) / 71,
                                            g["accurate"] + g["partial"]))
print("   breakdown       : %s" % g)
print("questions asked    : %.1f  (patient said yes to %.1f)"
      % (sum(r["n_q"] for r in ok) / n, sum(r["n_yes"] for r in ok) / n))
print("orders placed      : %.1f  (chart answered %.1f entries)"
      % (sum(r["n_orders"] for r in ok) / n, sum(r["n_served"] for r in ok) / n))
nd = sum(r["n_dec"] for r in ok)
print("decisive obtained  : %.1f%% (%d/%d)"
      % (100.0 * sum(r["dec_served"] for r in ok) / nd, sum(r["dec_served"] for r in ok), nd))
for k in (0, 1):
    sub = [r for r in ok if (r["dec_served"] > 0) == bool(k)]
    if sub:
        print("   %s decisive -> accurate %.1f%% (n=%d)"
              % ("with" if k else "without",
                 100.0 * sum(1 for r in sub if r["grade"] == "accurate") / len(sub), len(sub)))
