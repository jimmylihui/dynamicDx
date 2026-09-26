"""Re-check each proposed duplicate one pair at a time.

The list-against-list pass over-fires. On the tremor line it called "serum calcium, magnesium and
phosphate" a duplicate of "whole-blood manganese", and on paroxysmal it matched "serum
electrolytes, urea and creatinine" to "full blood count and biochemistry" - a component, not a
twin. Dropping those would delete coverage rather than a duplicate, so each pair is put to a
separate judge on its own, where there is no list to skim and nothing to pattern-match against.
"""
import json
import os
import re
import threading
import time
import urllib.request

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORKEY = os.environ["ORKEY"]
JUDGE = os.environ.get("JUDGE", "deepseek/deepseek-v4.1-flash")
JPROV = os.environ.get("JPROVIDER", "")
GEN = json.load(open(B + "/pipeline/generic_panel.json"))["entries"]
drop = json.load(open(B + "/pipeline/generic_drop.json"))
cases = json.load(open(B + "/data/cases.json"))
own = {}
for c in cases:
    own.setdefault(c["line"], [k for k in c["investigations"] if k not in GEN])

P = """Two entries from a hospital chart:

  A: %s
  B: %s

Is A the same investigation as B - so that a doctor ordering A is ordering exactly B, and reporting
both would report the same result twice?

Answer NO if one is merely a part of the other, or a related but different measurement, or the same
organ system tested a different way.

Reply with ONLY {"same": true} or {"same": false}."""

pairs = []
for ln, keys in drop.items():
    for k in keys:
        pairs.append((ln, k))
out, lock = {}, threading.Lock()
q = list(pairs)
srcmap = {}


def ask(p):
    body = json.dumps({"model": JUDGE, "temperature": 0, "max_tokens": 60,
                       "messages": [{"role": "user", "content": p}],
                       **({"provider": {"order": [JPROV], "allow_fallbacks": False, "sort": "price"}} if JPROV else {}),
                       "reasoning": {"enabled": False}}).encode()
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


TWIN = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/generic_twins.json"))


def work():
    while True:
        with lock:
            if not q:
                return
            ln, k = q.pop()
        b = TWIN.get(ln, {}).get(k)
        r = ask(P % (k, b)) if b else None
        with lock:
            if r and r.get("same") is True:
                out.setdefault(ln, []).append(k)
            else:
                print("  keep  %-14s %-46s (vs %s)" % (ln, k[:46], str(b)[:40]), flush=True)


ts = [threading.Thread(target=work) for _ in range(8)]
[t.start() for t in ts]
[t.join() for t in ts]
out = {k: sorted(v) for k, v in out.items()}
json.dump(out, open(B + "/pipeline/generic_drop.json", "w"), indent=1, ensure_ascii=False)
print("\nconfirmed duplicates %d of %d proposed" % (sum(len(v) for v in out.values()), len(pairs)))
for ln in sorted(out):
    print("   %-16s %d" % (ln, len(out[ln])))
