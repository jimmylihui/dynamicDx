"""Map every model description onto the full HPO phenomenology space.

The point is not another accuracy number. It is to see what the models actually say - how many
distinct phenomenology concepts they name, how many of those fall outside the eleven lines this
dataset happens to contain, and therefore how much of the earlier "no match" was really "named
something specific that our table had no bucket for".
"""
import os
import glob
import json
import re
from collections import Counter, defaultdict

B = os.environ.get("DDX_ROOT", ".")
vocab = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/hpo_vocab.json"))
cases = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}

STOP = {"disease", "disorder", "syndrome", "abnormality", "abnormal", "impairment", "deficit"}
pats = []
for hp, v in vocab.items():
    for t in v["terms"]:
        if t in STOP or len(t) < 6:
            continue
        pats.append((re.compile(r"\b%s\b" % re.escape(t)), hp, v["label"]))
print("compiled %d surface forms" % len(pats))

# the eleven lines expressed as HPO concepts, for the "inside vs outside our taxonomy" split
LINE_HP = {
    "chorea": ["chorea", "choreoathetosis", "athetosis", "hemiballismus", "ballismus"],
    "dystonia": ["dystonia", "blepharospasm", "torticollis", "oromandibular dystonia"],
    "myoclonus": ["myoclonus", "myoclonic"],
    "tremor": ["tremor"],
    "ataxia": ["ataxia", "dysmetria", "dysdiadochokinesis"],
    "parkinsonism": ["parkinsonism", "bradykinesia", "rigidity", "hypokinesia", "akinesia"],
    "ptosis": ["ptosis", "ophthalmoparesis", "ophthalmoplegia"],
    "vertigo_central": ["nystagmus", "opsoclonus", "saccad", "ocular flutter"],
    "facialpalsy": ["facial palsy", "facial paresis", "facial nerve"],
    "paroxysmal": ["seizure", "epilep"],
    "functional": ["functional", "psychogenic"],
}
inside = set()
for words in LINE_HP.values():
    for hp, v in vocab.items():
        if any(w in v["label"].lower() for w in words):
            inside.add(hp)
print("HPO concepts that correspond to one of the eleven lines: %d of %d\n"
      % (len(inside), len(vocab)))

RUNS = [("gemma-4-31b", "part1_oldp_gemma"), ("gpt-5.6-luna", "part1_oldp_luna"),
        ("qwen3.7-plus", "part1_oldp_qwen"), ("mimo-v2.5", "part1_oldp_mimo"),
        ("minimax-m3", "part1_oldp_minimax")]

print("%-14s %6s %10s %12s %12s %12s"
      % ("model", "n", "0 concepts", "mean/answer", "distinct", "outside 11"))
outside_all = Counter()
for name, root in RUNS:
    n = 0
    empty = 0
    tot = 0
    distinct = set()
    outside_hits = 0
    for f in glob.glob("%s/results/%s/*/*.json" % (B, root)):
        d = json.load(open(f))
        t = (d.get("raw") or "").lower()
        found = {hp for rx, hp, _ in pats if rx.search(t)}
        n += 1
        if not found:
            empty += 1
        tot += len(found)
        distinct |= found
        out = found - inside
        if out:
            outside_hits += 1
            for hp in out:
                outside_all[vocab[hp]["label"]] += 1
    print("%-14s %6d %9.1f%% %11.1f %12d %11.1f%%"
          % (name, n, 100.0 * empty / n, tot / n, len(distinct), 100.0 * outside_hits / n))

print("\nthe 25 concepts most often named that are OUTSIDE the eleven lines")
for lab, c in outside_all.most_common(25):
    print("   %-46s %d" % (lab, c))
