"""Shuffled condition: the mean over three permutations (Section 3.4).

The Shuffled condition is run three times per model with SHUFFLE_SEED=0, 1, 2 (eval/part2_full.py).
A case's Shuffled accuracy and acquired decisive entries are the means over its three runs, and the
Video - Shuffled contrast is a paired case-level bootstrap over the 71 cases on those per-case means.
A missing or failed run counts as not accurate with zero acquired entries.

usage: shuffle_mean.py VIDEO_RUN SHUF_RUN_0 SHUF_RUN_1 SHUF_RUN_2 [NBOOT]
       runs are directories under results/ with grades in results/stage2_<run>.json
       (or results/judge/fulljudge_<run>.json)
"""
import glob
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from tau import acquired, DEC                                       # noqa: E402

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ACCURATE = {"accurate", "exact"}
video, shufs = sys.argv[1], sys.argv[2:5]
NB = int(sys.argv[5]) if len(sys.argv) > 5 else 10000
if len(shufs) != 3:
    sys.exit(__doc__)


def grades(run):
    for p in ("%s/results/judge/fulljudge_%s.json" % (B, run), "%s/results/stage2_%s.json" % (B, run)):
        if os.path.exists(p):
            return json.load(open(p))
    raise FileNotFoundError("no grades for %s" % run)


def per_case(run):
    """{video: (accurate 0/1, acquired decisive entries)} over all 71 cases"""
    g = grades(run)
    out = {v: (0.0, 0.0) for v in DEC}
    for f in glob.glob("%s/results/%s/*/*.json" % (B, run)):
        d = json.load(open(f))
        v = d.get("video")
        if v in out and not d.get("error") and (g.get(v) or {}).get("grade"):
            out[v] = (1.0 if g[v]["grade"] in ACCURATE else 0.0,
                      float(len(acquired(v, d.get("served")))))
    return out


V = per_case(video)
S = [per_case(r) for r in shufs]
M = {v: (sum(s[v][0] for s in S) / 3.0, sum(s[v][1] for s in S) / 3.0) for v in DEC}
ks = sorted(DEC)
nd = sum(len(DEC[v]) for v in ks)


def acc(X, sample):
    return 100.0 * sum(X[v][0] for v in sample) / len(sample)


def tau(X, sample):
    return 100.0 * sum(X[v][1] for v in sample) / sum(len(DEC[v]) for v in sample)


rng = random.Random(0)
bs_a, bs_t = [], []
for _ in range(NB):
    s = [ks[rng.randrange(len(ks))] for _ in ks]
    bs_a.append(acc(V, s) - acc(M, s))
    bs_t.append(tau(V, s) - tau(M, s))
bs_a.sort()
bs_t.sort()
lo, hi = int(0.025 * NB), int(0.975 * NB)
print("per-permutation Shuffled accuracy : %s" % ", ".join("%.1f" % acc(s, ks) for s in S))
print("Shuffled (mean of 3)  accuracy %.1f%%   tau %.1f%%" % (acc(M, ks), tau(M, ks)))
print("Video                 accuracy %.1f%%   tau %.1f%%" % (acc(V, ks), tau(V, ks)))
print("Video - Shuffled      accuracy %+.1f [%+.1f, %+.1f]   tau %+.1f [%+.1f, %+.1f]"
      % (acc(V, ks) - acc(M, ks), bs_a[lo], bs_a[hi], tau(V, ks) - tau(M, ks), bs_t[lo], bs_t[hi]))
