"""Verify the duplicate candidates that split the decisive flag, one pair at a time.

Reuses the pairwise question of verify_dupes.py: a list-against-list pass over-fires, so each pair
is judged alone. Only pairs confirmed as the same investigation are a defect; the rest are
different tests that happen to share words.
"""
import json
import os
import re
import threading
import time
import urllib.request
from collections import defaultdict
from itertools import combinations

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORKEY = os.environ["ORKEY"]
REASONING = json.loads(os.environ.get("REASONING", '{"enabled": false}'))
JUDGE = os.environ.get("JUDGE", "deepseek/deepseek-v4.1-flash")
JPROV = os.environ.get("JPROVIDER", "")
cases = json.load(open(B + "/data/cases.json"))

STOP = set("and or of the with for a an in on to test testing examination assessment level levels "
           "serum blood study studies panel screen".split())


def toks(k):
    return {w for w in re.findall(r"[a-z0-9]+", k.lower()) if w not in STOP and len(w) > 2}


pairs = defaultdict(list)
for c in cases:
    inv = c["investigations"]
    for a, b in combinations(inv, 2):
        ta, tb = toks(a), toks(b)
        if not ta or not tb:
            continue
        j = len(ta & tb) / len(ta | tb)
        va, vb = str(inv[a]["v"]).lower(), str(inv[b]["v"]).lower()
        vt = len(set(re.findall(r"[a-z0-9]+", va)) & set(re.findall(r"[a-z0-9]+", vb)))
        if j >= 0.45 or (j >= 0.3 and vt >= 4):
            pairs[(a, b)].append((c["video"], bool(inv[a].get("decisive")),
                                  bool(inv[b].get("decisive"))))

split = [(p, v) for p, v in pairs.items() if any(x[1] != x[2] for x in v)]
P = """Two entries from a hospital chart:

  A: %s
  B: %s

Is A the same investigation as B - so that a doctor ordering A is ordering exactly B, and reporting
both would report the same result twice?

Answer NO if one is merely a part of the other, or a related but different measurement, or the same
organ system tested a different way.

Reply with ONLY {"same": true} or {"same": false}."""

out, lock = {}, threading.Lock()
q = list(split)


def ask(p):
    body = json.dumps({"model": JUDGE, "temperature": 0, "max_tokens": 60,
                       "messages": [{"role": "user", "content": p}],
                       **({"provider": {"order": [JPROV], "allow_fallbacks": False}} if JPROV else {}),
                       "reasoning": REASONING}).encode()
    for _ in range(4):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=90).read().decode())
            m = re.search(r"\{.*\}", r["choices"][0]["message"]["content"] or "", re.S)
            if m:
                return json.loads(m.group(0)).get("same")
        except Exception:                                          # noqa: BLE001
            time.sleep(3)
    return None


def work():
    while True:
        with lock:
            if not q:
                return
            (a, b), v = q.pop()
        out[(a, b)] = (ask(P % (a, b)), v)


ts = [threading.Thread(target=work) for _ in range(6)]
[t.start() for t in ts]
[t.join() for t in ts]

conf = {k: v for k, v in out.items() if v[0] is True}
print("split candidates judged : %d" % len(out))
print("confirmed same test     : %d" % len(conf))
print()
aff = set()
nsplit = 0
for (a, b), (_, v) in conf.items():
    s = sum(1 for x in v if x[1] != x[2])
    nsplit += s
    for vid, da, db in v:
        if da != db:
            aff.add(vid)
    print("  %-46s | %-42s  split in %d/%d" % (a[:46], b[:42], s, len(v)))
print()
print("case-level splits caused by a confirmed duplicate: %d" % nsplit)
print("cases affected: %d/%d" % (len(aff), len(cases)))
json.dump({"%s || %s" % k: v[1] for k, v in conf.items()},
          open(os.environ.get("DDX_WORK", "/tmp") + "/confirmed_split_dupes.json", "w"), indent=1, ensure_ascii=False)
