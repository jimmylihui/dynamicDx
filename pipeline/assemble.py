"""Concatenate the per-line case files into cases_all.json and check the invariants.

Run from the directory the per-line generators wrote into (they write cases_<line>.json into the
current directory), or pass that directory as the argument.

Checks, all of which have been violated at some point:
  - every video in dataset/videos has exactly one case, and vice versa
  - every chart entry was read from the source article (p = "reported")
  - every case keeps at least one decisive entry
  - therapeutic trials are still gated behind explicit_only
"""
import json
import os
import sys

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = sys.argv[1] if len(sys.argv) > 1 else "."
LINES = ["ataxia", "chorea", "dystonia", "facialpalsy", "functional", "myoclonus",
         "parkinsonism", "paroxysmal", "ptosis", "tremor", "vertigo_central"]

allc = []
for ln in LINES:
    cs = json.load(open(os.path.join(SRC, "cases_%s.json" % ln)))
    bad = [(c["video"], k) for c in cs for k, v in c["investigations"].items()
           if v.get("p") != "reported"]
    assert not bad, "%s: entries not read from the source %s" % (ln, bad[:5])
    nodec = [c["video"] for c in cs if not any(v.get("decisive") for v in c["investigations"].values())]
    assert not nodec, "%s: cases without a decisive entry %s" % (ln, nodec)
    allc += cs
    print("%-16s %2d cases  %3d chart entries" % (ln, len(cs), sum(len(c["investigations"]) for c in cs)))

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
print("chart entries: mean %.1f" % (sum(len(c["investigations"]) for c in allc) / len(allc)))
print("decisive:  mean %.1f"
      % (sum(sum(1 for v in c["investigations"].values() if v.get("decisive")) for c in allc)
         / len(allc)))
