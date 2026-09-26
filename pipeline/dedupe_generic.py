"""Find generic entries that duplicate a test a line already had, and drop them.

Adding 53 shared entries to every line created collisions: the ataxia menu now carries both
"serum thiamine (vitamin B1)" - reported, decisive - and the generic "serum vitamin B1
(thiamine)". A doctor ordering serum thiamine matches whichever the judge picks, so a decisive
test can be served without being counted, and the same result is reported twice under two names.

The menu only has to be identical WITHIN a line, so a colliding generic entry can be dropped for
that line alone. The case's own entry always wins - it is the one the article reported and the one
that may be marked decisive.

Writes pipeline/generic_drop.json: {line: [generic keys to omit]}
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
cases = json.load(open(B + "/data/cases.json"))

P = """Below are two lists of investigations from one patient chart.

LIST A (added generically):
%s

LIST B (the chart's own entries):
%s

Find every entry in list A that names the SAME test as some entry in list B - the same specimen
and the same measurement, however differently worded ("serum thiamine (vitamin B1)" and "serum
vitamin B1 (thiamine)" are the same test; "MRI brain with gadolinium" and "brain MRI" are the same
study; "CSF protein" and "lumbar puncture" are NOT, one is a component of the other).

Reply with ONLY a JSON object mapping each duplicated list-A entry to its list-B twin:
{"<list A entry>": "<list B entry>", ...}   Use {} if there are none."""

lines = {}
for c in cases:
    lines.setdefault(c["line"], c)
out, lock = {}, threading.Lock()
q = list(lines.items())


def ask(p):
    body = json.dumps({"model": JUDGE, "temperature": 0, "max_tokens": 1500,
                       "messages": [{"role": "user", "content": p}],
                       **({"provider": {"order": [JPROV], "allow_fallbacks": False, "sort": "price"}} if JPROV else {}),
                       "reasoning": {"enabled": False}}).encode()
    for _ in range(4):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=240).read().decode())
            m = re.search(r"\{.*\}", r["choices"][0]["message"]["content"] or "", re.S)
            if m:
                return json.loads(m.group(0))
        except Exception:                                          # noqa: BLE001
            time.sleep(4)
    return None


def work():
    while True:
        with lock:
            if not q:
                return
            ln, c = q.pop()
        own = [k for k in c["investigations"] if k not in GEN]
        r = ask(P % ("\n".join("- " + k for k in GEN), "\n".join("- " + k for k in own))) or {}
        r = {k: v for k, v in r.items() if k in GEN and v in own}
        with lock:
            out[ln] = r
            print("%-16s %2d duplicates: %s" % (ln, len(r),
                                                "; ".join("%s = %s" % (a, b)
                                                          for a, b in list(r.items())[:3])),
                  flush=True)


ts = [threading.Thread(target=work) for _ in range(6)]
[t.start() for t in ts]
[t.join() for t in ts]
json.dump(out, open(os.environ.get("DDX_WORK", "/tmp") + "/generic_twins.json", "w"), indent=1, ensure_ascii=False)
json.dump({k: sorted(v) for k, v in out.items()},
          open(B + "/pipeline/generic_drop.json", "w"), indent=1, ensure_ascii=False)
print("\ntotal dropped: %d" % sum(len(v) for v in out.values()))
