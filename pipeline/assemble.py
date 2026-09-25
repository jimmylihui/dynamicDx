"""Concatenate the per-line case files into cases_all.json and check the invariants.

Run from the directory the per-line generators wrote into. The per-line generators write into whatever directory they are run from, so
this takes the freshly generated files as an argument rather than guessing.

Checks, all of which have been violated at some point:
  - every video in dataset/videos has exactly one case, and vice versa
  - the menu is identical across a line, so ordering a test cannot identify the case
  - no investigation key exists on only one case of its line
  - therapeutic trials are still gated behind explicit_only
"""
import json
import os
import sys
from collections import Counter

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = sys.argv[1] if len(sys.argv) > 1 else "gen"
LINES = ["ataxia", "chorea", "dystonia", "facialpalsy", "functional", "myoclonus",
         "parkinsonism", "paroxysmal", "ptosis", "tremor", "vertigo_central"]

allc = []
for ln in LINES:
    cs = json.load(open(os.path.join(SRC, "cases_%s.json" % ln)))
    menus = {frozenset(c["investigations"]) for c in cs}
    assert len(menus) == 1, "%s: %d menu variants" % (ln, len(menus))
    keys = Counter(k for c in cs for k in c["investigations"])
    uniq = [k for k, n in keys.items() if n == 1 and len(cs) > 1]
    assert not uniq, "%s: case-unique keys %s" % (ln, uniq)
    allc += cs
    print("%-16s %2d cases  menu %3d" % (ln, len(cs), len(cs[0]["investigations"])))

vids = {c["video"] for c in allc}
on_disk = {f for ln in LINES for f in os.listdir("%s/dataset/videos/%s" % (B, ln))
           if f.endswith(".mp4")}
assert vids == on_disk, ("cases without a clip: %s | clips without a case: %s"
                         % (sorted(vids - on_disk), sorted(on_disk - vids)))

rules = {c["investigation_rules"]["default_for_unlisted"] for c in allc}
assert rules == {"not performed / not available"}, rules
trials = [(c["video"], k) for c in allc for k, v in c["investigations"].items()
          if "trial" in k.lower() and "history" not in k.lower()
          and not v.get("explicit_only")]
assert not trials, trials[:5]

json.dump(allc, open("cases_all.json", "w"), indent=1, ensure_ascii=False)
print("\n%d cases -> cases_all.json" % len(allc))
print("menu size: mean %.1f" % (sum(len(c["investigations"]) for c in allc) / len(allc)))
print("decisive:  mean %.1f"
      % (sum(sum(1 for v in c["investigations"].values() if v.get("decisive")) for c in allc)
         / len(allc)))
