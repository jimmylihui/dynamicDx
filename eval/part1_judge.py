"""LLM judge for the part 1 sweep, replacing the string matcher.

The string matcher counts "cerebellar ataxia" as a hit on "spinocerebellar ataxia" because one is
a substring of the other, and 59% of its hits came from that direction - the model naming
something vaguer than the answer. A judge can tell "vaguer but pointing the right way" from
"correct", which is the distinction the benchmark actually needs.

Each answer is judged ALONE. The judge never sees the frame count and never sees the other seven
answers for the same clip, so it cannot anchor on k or mark one answer relative to another.

usage: part1_judge.py [PAR]
env:   ORKEY, JUDGE (default openai/gpt-5.6-luna), JUDGE_PROVIDER (default OpenAI), LIMIT
       SRCROOT  answers to judge,  default part1
       OUTROOT  where verdicts go, default <SRCROOT>_judge

When the judge and the model under test are the same model, every verdict records
self_judged=true. Judging your own output is self-preference, and the flag is there so nobody
reads those numbers later as a clean cross-model comparison.
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
PAR = int(sys.argv[1]) if len(sys.argv) > 1 else 6
ORKEY = os.environ["ORKEY"]
JUDGE = os.environ.get("JUDGE", "openai/gpt-5.6-luna")
JPROV = os.environ.get("JUDGE_PROVIDER", "OpenAI")
LIMIT = int(os.environ.get("LIMIT", "0"))
SRCROOT = os.environ.get("SRCROOT", "part1")
OUTROOT = os.environ.get("OUTROOT", SRCROOT + "_judge")
OUTDIR = B + "/results/" + OUTROOT

RUBRIC_PROSE = """You are grading a vision model that was shown a short clinical video of one
patient and asked, with NO history and NO test results, to describe what it saw and name the
disease. It answered in free prose, so read the whole answer and extract its position.

GROUND TRUTH
  true diagnosis : %(true)s
  the sign a competent viewer should name from the clip : %(gtsign)s
  answers to score as CORRECT (the actual disease entity) : %(ok)s
  answers to score as PARTIAL (right syndrome or category, but not the cause) : %(part)s

THE MODEL'S ANSWER (free prose)
%(prose)s

Grade on two axes, using the same standard you would apply to a structured answer.

SIGN - did it name the visible abnormality correctly?
  correct : names the same phenomenology as the ground-truth sign anywhere in the prose
            (synonyms count: "ataxic gait" for "unsteady wide-based walking")
  partial : describes the abnormality in the right body region but names the wrong
            phenomenology, or describes it only vaguely without naming a sign
  wrong   : names a different phenomenology, wrong body region, or says nothing abnormal is
            visible

DIAGNOSIS - the prose may list several. Treat the one it presents first or most confidently as
dx1, the next two as dx2 and dx3, and leave a slot "wrong" if it offered fewer.
  correct : the same disease entity as the true diagnosis or as one of the CORRECT list, at
            comparable specificity. A strictly vaguer answer is NOT correct.
  partial : matches the PARTIAL list, or is the right syndrome/category but not the cause, or is
            the correct entity named too vaguely.
  wrong   : anything else.

Reply with ONLY this JSON, no prose around it:
{"sign":"correct|partial|wrong",
 "dx1":"correct|partial|wrong",
 "dx2":"correct|partial|wrong",
 "dx3":"correct|partial|wrong",
 "best":"correct|partial|wrong",
 "reason":"<= 12 words"}"""

RUBRIC = """You are grading a vision model that was shown a short clinical video of one patient
and asked, with NO history and NO test results, to name the sign and the disease.

GROUND TRUTH
  true diagnosis : %(true)s
  the sign a competent viewer should name from the clip : %(gtsign)s
  answers to score as CORRECT (the actual disease entity) : %(ok)s
  answers to score as PARTIAL (right syndrome or category, but not the cause) : %(part)s

THE MODEL'S ANSWER
  sign it named    : %(sign)s
  movement it described : %(motion)s
  body region      : %(region)s
  first diagnosis  : %(dx1)s
  second           : %(dx2)s
  third            : %(dx3)s

Grade on two axes.

SIGN - did it name the visible abnormality correctly?
  correct : names the same phenomenology as the ground-truth sign (synonyms count: "ataxic gait"
            for "unsteady wide-based walking", "facial droop" for "facial weakness")
  partial : describes the abnormality in the right body region but names the wrong phenomenology,
            or describes it only vaguely without naming a sign
  wrong   : names a different phenomenology, wrong body region, or says nothing abnormal is visible

DIAGNOSIS - judge each of the three separately, then report the best.
  correct : the same disease entity as the true diagnosis or as one of the CORRECT list, at
            comparable specificity. A strictly vaguer answer is NOT correct - "epilepsy" is not
            correct for "sleep-related hypermotor epilepsy", "cerebellar ataxia" is not correct
            for "spinocerebellar ataxia type 8".
  partial : matches the PARTIAL list, or is the right syndrome/category but not the cause, or is
            the correct entity named too vaguely.
  wrong   : anything else.

A diagnosis that could not possibly be established from a silent video (a specific antibody, a
named gene, a drug exposure) should still be graded on what the model said, not on whether the
task was fair.

Reply with ONLY this JSON, no prose:
{"sign":"correct|partial|wrong",
 "dx1":"correct|partial|wrong",
 "dx2":"correct|partial|wrong",
 "dx3":"correct|partial|wrong",
 "best":"correct|partial|wrong",
 "reason":"<= 20 words"}"""


def ask(prompt):
    # 300 was too small. The judge writes its reason last, so a long answer pushed the closing
    # brace past the limit and the verdict was discarded as NO_JSON_IN_REPLY - 26% of the
    # free-prose run, and the loss was directional: more frames -> longer answer -> more truncation.
    body = json.dumps({"model": JUDGE, "temperature": 0, "max_tokens": 1000,
                       "messages": [{"role": "user", "content": prompt}],
                       "provider": {"order": [JPROV], "allow_fallbacks": False,
                                    "sort": "price"},
                       "usage": {"include": True}}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                                 headers={"Authorization": "Bearer " + ORKEY,
                                          "Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=300).read().decode())
    if "error" in r and not r.get("choices"):
        raise RuntimeError(str(r["error"])[:200])
    return (r.get("choices", [{}])[0].get("message", {}).get("content", ""),
            (r.get("usage") or {}).get("cost", 0))


cases = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}
jobs = []
for f in sorted(glob.glob(B + "/results/" + SRCROOT + "/*/*__k*.json")):
    out = OUTDIR + "/" + os.path.basename(f)
    if os.path.exists(out) and os.path.getsize(out) > 20:
        continue
    jobs.append((f, out))
os.makedirs(OUTDIR, exist_ok=True)
if LIMIT:
    # spread the sample across frame counts and lines rather than taking the first N alphabetically
    jobs = jobs[:: max(1, len(jobs) // LIMIT)][:LIMIT]
print("%d answers to judge with %s (%s, cheapest tier), %d parallel"
      % (len(jobs), JUDGE, JPROV, PAR), flush=True)

lock = threading.Lock()
state = {"n": 0, "cost": 0.0}
t0 = time.time()


def worker(q):
    while True:
        with lock:
            if not q:
                return
            src, out = q.pop(0)
        d = json.load(open(src))
        c = cases[d["video"]]
        p1 = c["part1_video_only"]
        g = d.get("parsed") or {}
        if d.get("prompt") == "old" or not g:
            prompt = RUBRIC_PROSE % dict(
                true=c["true_diagnosis"], gtsign=p1["visible_sign"],
                ok="; ".join(p1["accept_as_correct"]),
                part="; ".join(p1["accept_as_partial"]),
                prose=(d.get("raw") or "(no answer)")[:20000])
        else:
            prompt = RUBRIC % dict(
                true=c["true_diagnosis"], gtsign=p1["visible_sign"],
                ok="; ".join(p1["accept_as_correct"]),
                part="; ".join(p1["accept_as_partial"]),
                sign=g.get("sign", "(no answer)"), motion=g.get("motion", "(no answer)"),
                region=g.get("body_region", "(no answer)"), dx1=g.get("dx1", "(no answer)"),
                dx2=g.get("dx2", "(no answer)"), dx3=g.get("dx3", "(no answer)"))
        verdict, cost, err, last = None, 0, None, None
        for attempt in range(6):
            try:
                txt, cost = ask(prompt)
                last = txt
                m = re.search(r"\{.*\}", txt or "", re.S)
                if not m:
                    # a reply cut off mid-"reason" still carries every graded field; close it
                    # rather than discard a usable verdict
                    frag = re.search(r'\{.*"best"\s*:\s*"(correct|partial|wrong)"',
                                     txt or "", re.S)
                    if frag:
                        verdict = json.loads(frag.group(0) + ', "reason": "(truncated)"}')
                        err = None
                        break
                    err = "NO_JSON_IN_REPLY"
                    time.sleep(3 * (attempt + 1))
                    continue
                verdict = json.loads(m.group(0))
                err = None
                break
            except json.JSONDecodeError as e:
                err = "BAD_JSON: %s" % e
                time.sleep(3 * (attempt + 1))
            except Exception as e:                                # noqa: BLE001
                err = "API_%s: %s" % (type(e).__name__, e)
                time.sleep(4 * (attempt + 1))
        json.dump(dict(video=d["video"], line=c["line"], k=d["k"], judge=JUDGE,
                       subject=d.get("model"), prompt=d.get("prompt", "new"),
                       self_judged=(d.get("model") == JUDGE),
                       verdict=verdict, error=err,
                       raw=None if verdict else (last or "")[:600]),
                  open(out, "w"), indent=1, ensure_ascii=False)
        with lock:
            state["n"] += 1
            state["cost"] += cost or 0
            if state["n"] % 25 == 0 or state["n"] == len(jobs):
                el = time.time() - t0
                print("[%3d/%3d] %4.0fs  $%.3f  eta %3.0fs"
                      % (state["n"], len(jobs), el, state["cost"],
                         (len(jobs) - state["n"]) * el / state["n"]), flush=True)


q = list(jobs)
ts = [threading.Thread(target=worker, args=(q,)) for _ in range(PAR)]
for t in ts:
    t.start()
for t in ts:
    t.join()
print("judging done in %.1f min, $%.3f" % ((time.time() - t0) / 60, state["cost"]), flush=True)
