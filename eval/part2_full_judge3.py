"""Grade the end-to-end diagnosis.

The same four grades as Part 1, so the number is comparable to the video-only figure: the whole
point of the consultation is how far it moves the diagnosis past what the frames alone gave.

  exact    - the disease entity and its cause, at the specificity of the true diagnosis
  core     - the right syndrome or the right cause, but not both, or named too vaguely
  category - the right family of disease only
  none     - anything else

Graded from the doctor's stated primary diagnosis. Alternatives are recorded but not credited:
a consultation that ends in "one of these four things" has not diagnosed the patient.
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
JUDGE = os.environ.get("JUDGE", "openai/gpt-5.6-luna")
ROOT = os.environ.get("ROOT", "part2_full_none")
cases = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}

P = """You are grading a doctor who watched a video of a patient, took a yes/no history, ordered
investigations, and then named a diagnosis.

GROUND TRUTH
  true diagnosis : %s
  count as CORRECT (the actual disease entity) : %s
  count as PARTIAL (right syndrome or category, not the cause) : %s

THE DOCTOR'S PRIMARY DIAGNOSIS
%s

Grade the primary diagnosis alone.
  exact    : the same disease entity as the truth or the CORRECT list, at comparable specificity
  core     : the right syndrome or the right cause but not both, or the correct entity named too
             vaguely to act on
  category : only the right broad family of disease
  none     : anything else

Reply with ONLY {"grade":"exact|core|category|none","reason":"<= 12 words"}"""

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
        p1 = c["part1_video_only"]
        v = ask(P % (c["true_diagnosis"], p1.get("accept_as_correct"), p1.get("accept_as_partial"),
                     d["dx"]))
        with lock:
            res[d["video"]] = dict(line=c["line"], dx=d["dx"], grade=(v or {}).get("grade"),
                                   reason=(v or {}).get("reason"),
                                   n_dec=d.get("n_decisive", 0),
                                   dec_served=len(d.get("decisive_served") or []),
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
g = {k: sum(1 for r in ok if r["grade"] == k) for k in ("exact", "core", "category", "none")}
print("cases              : %d" % n)
print("EXACT              : %.1f%% (%d)" % (100.0 * g["exact"] / n, g["exact"]))
print("EXACT + CORE       : %.1f%% (%d)" % (100.0 * (g["exact"] + g["core"]) / n,
                                            g["exact"] + g["core"]))
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
        print("   %s decisive -> exact %.1f%% (n=%d)"
              % ("with" if k else "without",
                 100.0 * sum(1 for r in sub if r["grade"] == "exact") / len(sub), len(sub)))
