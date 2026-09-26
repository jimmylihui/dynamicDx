"""Blinded comparison of two describers' sentences against the reference (Appendix D,
"Independent recognition of the student's sentences").

For each clip the judge sees the reference phenomenology sentence and two anonymous candidate
sentences (A and B, order randomised per clip with a fixed seed). It rates each candidate on the
components of the reference - body part, laterality (only when the reference states a side),
movement character, activation condition - and says which sentence is closer overall, or a tie.
The judge never sees the diagnosis, the video, or which model wrote which sentence.

Only clips with a usable teacher record are judged (TEACHER, default results/window/teacher.json).

usage: python window/judge_sentences.py FIRST_JSON SECOND_JSON [OUT_JSON]
       inputs are infer_student.py outputs ({video: {"sentence": ...}}) or {video: sentence}
env:   ORKEY, JUDGE (default deepseek/deepseek-v4.1-flash), JPROVIDER
"""
import json
import os
import random
import re
import sys
import threading
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as W                                                    # noqa: E402

ORKEY = os.environ["ORKEY"]
JUDGE = os.environ.get("JUDGE", "deepseek/deepseek-v4.1-flash")
JPROV = os.environ.get("JPROVIDER", "")
A_FILE, B_FILE = sys.argv[1], sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else W.B + "/results/window/sentence_judgement.json"

P = """A clinician described the visible abnormality in a short patient video as:

REFERENCE: %s

Two other descriptions of the same video:

A: %s
B: %s

For each of A and B, judge each component of the REFERENCE:
- body_part: does it name the same body part?
- laterality: does it name the same side? Use "na" if the REFERENCE states no side.
- movement_character: does it describe the same kind of movement or posture (e.g. jerky,
  flowing, rhythmic, sustained, absent)?
- activation: does it name the same activation condition (at rest, on action, while walking,
  on a task)? Use "na" if the REFERENCE states none.
Then say which description is closer to the REFERENCE overall, or "tie".

Reply with ONLY this JSON:
{"A": {"body_part": "yes|no", "laterality": "yes|no|na", "movement_character": "yes|no",
       "activation": "yes|no|na"},
 "B": {"body_part": "yes|no", "laterality": "yes|no|na", "movement_character": "yes|no",
       "activation": "yes|no|na"},
 "closer": "A|B|tie"}"""


def sentences(path):
    d = json.load(open(path))
    return {v: (r["sentence"] if isinstance(r, dict) else r) for v, r in d.items()}


def ask(p):
    body = json.dumps({"model": JUDGE, "temperature": 0, "max_tokens": 400,
                       "messages": [{"role": "user", "content": p}],
                       **({"provider": {"order": [JPROV], "allow_fallbacks": False}} if JPROV else {}),
                       "reasoning": {"enabled": False}}).encode()
    for _ in range(4):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY, "Content-Type": "application/json"}),
                timeout=120).read().decode())
            j = W.last_json(r["choices"][0]["message"]["content"] or "")
            if isinstance(j, dict) and "closer" in j:
                return j
        except Exception:                                              # noqa: BLE001
            time.sleep(3)
    return None


first, second = sentences(A_FILE), sentences(B_FILE)
# the clips with a usable teacher record (68 of 71 in the paper), as in Appendix D
usable = set(W.load_targets(os.environ.get("TEACHER", W.B + "/results/window/teacher.json")))
todo = sorted(set(first) & set(second) & usable)
out, lock = {}, threading.Lock()


def work():
    while True:
        with lock:
            if not todo:
                return
            v = todo.pop()
        swap = random.Random("judge|%s" % v).random() < 0.5          # blinded, fixed per clip
        a, b = (second[v], first[v]) if swap else (first[v], second[v])
        j = ask(P % (W.reference_sign(v), a, b))
        if not j:
            continue
        fa, fb = (j.get("B"), j.get("A")) if swap else (j.get("A"), j.get("B"))
        c = str(j.get("closer", "tie")).upper()
        winner = "tie" if c not in ("A", "B") else (("second" if c == "A" else "first") if swap
                                                    else ("first" if c == "A" else "second"))
        with lock:
            out[v] = dict(first=fa, second=fb, closer=winner)


ts = [threading.Thread(target=work) for _ in range(8)]
[t.start() for t in ts]
[t.join() for t in ts]
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
n = len(out)
for comp in ("body_part", "laterality", "movement_character", "activation"):
    for side in ("first", "second"):
        rated = [r[side].get(comp) for r in out.values() if isinstance(r.get(side), dict)
                 and r[side].get(comp) in ("yes", "no")]
        if rated:
            print("%-19s %-6s %5.1f%% of %d" % (comp, side, 100.0 * rated.count("yes") / len(rated), len(rated)))
print("closer: first %d, second %d, tie %d (of %d)" % tuple(
    [sum(1 for r in out.values() if r["closer"] == k) for k in ("first", "second", "tie")] + [n]))
