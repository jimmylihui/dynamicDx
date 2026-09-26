"""Mismatched retrieval: the length- and form-matched control of Section 3.5.2 and Appendix F.

For each case the list handed to the model is its own Stage 1 differential followed by
source-clean causes retrieved for a donor case from ANOTHER category, truncated so that the list
has the same length as the case's real source-clean list (own differential followed by its own
retrieved causes). The donor is drawn with a fixed per-clip seed. The list therefore matches the
real retrieval list in length and form but not in content.

usage: build_mismatched.py OWN_FILE CLEAN_FILE OUT_FILE
  OWN_FILE    {video: [own diagnoses]}                   (own_dx_<TAG>.json, build_union_space.py)
  CLEAN_FILE  {video: {"causes": [...], ...}}            source-clean retrieval (openspace.py,
                                                         CLEAN=clean), retrieved causes only
  OUT_FILE    {video: {"causes": [...], "donor": video, "n_own": n, "n_mismatched": n}}
              - pass it to eval/part2_full.py as the candidate file (SPACE/UNIONFILE)
"""
import json
import os
import random
import sys

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
own = json.load(open(sys.argv[1]))
clean = json.load(open(sys.argv[2]))
line = {c["video"]: c["line"] for c in json.load(open(B + "/data/cases.json"))}


def dedup(items):
    seen, out = set(), []
    for c in items:
        k = c.strip().lower()
        if k and k not in seen:
            seen.add(k)
            out.append(c)
    return out


def retrieved(v):
    x = clean.get(v) or {}
    return list(x.get("causes") or []) if isinstance(x, dict) else list(x)


out = {}
for v in sorted(line):
    mine = dedup(own.get(v) or [])
    real = dedup(mine + retrieved(v))                  # the list the Source-clean condition sees
    donors = sorted(u for u in line if line[u] != line[v] and retrieved(u))
    if not donors:
        continue
    donor = random.Random("mismatched|%s" % v).choice(donors)
    merged = dedup(mine + retrieved(donor))[:len(real)]
    out[v] = dict(line=line[v], causes=merged, donor=donor,
                  n_own=len(mine), n_mismatched=len(merged) - len(mine), n_real=len(real))

json.dump(out, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
n = len(out)
print("cases: %d   mean list length %.1f (real %.1f)   mean own %.1f"
      % (n, sum(len(x["causes"]) for x in out.values()) / max(n, 1),
         sum(x["n_real"] for x in out.values()) / max(n, 1),
         sum(x["n_own"] for x in out.values()) / max(n, 1)))
