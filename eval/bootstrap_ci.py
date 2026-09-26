"""Paired case-level bootstrap for the consultation-level results.

Every contrast in this paper is measured on the same 71 patients under two protocols, so the two
arms are not independent samples and an interval built separately for each would overstate the
uncertainty of their difference. Cases are therefore resampled with replacement, both arms of a
resampled case travel together, and the difference is recomputed; the interval is the 2.5th and
97.5th percentile over 10,000 resamples.

usage: bootstrap_ci.py [NBOOT]
"""
import glob
import json
import os
import random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tau import acquired, DEC                                     # noqa: E402
import runs                                                        # noqa: E402
ACCURATE = {"accurate", "exact"}   # grade names: current grader / earlier result files

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NB = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
rng = random.Random(0)

MODELS = [(name, tag, tag) for name, tag in runs.MODELS]


def judge(root):
    return runs.grades(root, required=False)


def load(root):
    """per case: (accurate 0/1, decisive obtained, decisive available), over all 71 cases.

    A case without a usable, graded consultation counts as not accurate and contributes zero
    acquired decisive entries, as in the paper, so every arm has the same 71-case denominator."""
    j = judge(root)
    if j is None:
        return None
    out = {v: (0, 0, len(DEC[v])) for v in DEC}
    for f in glob.glob("%s/results/%s/*/*.json" % (B, root)):
        d = json.load(open(f))
        v = d.get("video")
        if v not in out or d.get("error") or not (j.get(v) or {}).get("grade"):
            continue
        out[v] = (1 if j[v]["grade"] in ACCURATE else 0,
                  len(acquired(v, d.get("served"))), len(DEC[v]))
    return out


def ci(vals):
    vals = sorted(vals)
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals))]


def boot(A, Bb, ks, fn):
    """fn(sample of (a,b) tuples) -> statistic"""
    pts = [(A[k], Bb[k]) for k in ks]
    n = len(pts)
    out = []
    for _ in range(NB):
        s = [pts[rng.randrange(n)] for _ in range(n)]
        out.append(fn(s))
    return ci(out)


def d_exact(s):
    return 100.0 * (sum(b[0] for a, b in s) - sum(a[0] for a, b in s)) / len(s)


def d_dec(s):
    na = sum(a[2] for a, b in s) or 1
    nb = sum(b[2] for a, b in s) or 1
    return 100.0 * sum(b[1] for a, b in s) / nb - 100.0 * sum(a[1] for a, b in s) / na


def acc_ci(A, ks):
    pts = [A[k][0] for k in ks]
    n = len(pts)
    return ci([100.0 * sum(pts[rng.randrange(n)] for _ in range(n)) / n for _ in range(NB)])


print("=" * 96)
print("FOUR-ARM CONSULTATION  (paired within model; %d bootstrap resamples)" % NB)
print("=" * 96)
print("%-13s %4s  %-18s %-18s %-18s %-18s" % ("model", "n", "blind", "video", "own words", "reference"))
rows = {}
for name, tag, _ in MODELS:
    arms = {a: load(runs.run(tag, c))
            for a, c in (("blind", "blind"), ("video", "video"),
                         ("own", "own"), ("ref", "reference"))}
    if any(v is None for v in arms.values()):
        print("%-13s  (incomplete)" % name)
        continue
    ks = sorted(set.intersection(*[set(v) for v in arms.values()]))
    rows[name] = (arms, ks)
    cells = []
    for a in ("blind", "video", "own", "ref"):
        p = 100.0 * sum(arms[a][k][0] for k in ks) / len(ks)
        lo, hi = acc_ci(arms[a], ks)
        cells.append("%5.1f [%4.1f,%5.1f]" % (p, lo, hi))
    print("%-13s %4d  %s" % (name, len(ks), " ".join(cells)))

print()
print("%-13s %-24s %-24s %-24s" % ("model", "video - blind", "own - video (modality)",
                                   "ref - own (perception)"))
for name, _, _ in MODELS:
    if name not in rows:
        continue
    arms, ks = rows[name]
    out = []
    for a, b in (("blind", "video"), ("video", "own"), ("own", "ref")):
        d = 100.0 * (sum(arms[b][k][0] for k in ks) - sum(arms[a][k][0] for k in ks)) / len(ks)
        lo, hi = boot(arms[a], arms[b], ks, d_exact)
        out.append("%+5.1f [%+5.1f,%+5.1f]" % (d, lo, hi))
    print("%-13s %-24s %-24s %-24s" % ((name,) + tuple(out)))

print()
print("=" * 96)
print("RETRIEVAL   lit - base, paired on the same 71 cases")
print("=" * 96)
for name, tag, _ in MODELS:
    base = load(runs.run(tag, "video"))
    lit = load(runs.run(tag, "source_clean"))
    if base is None or lit is None:
        continue
    ks = sorted(set(base) & set(lit))
    d = 100.0 * (sum(lit[k][0] for k in ks) - sum(base[k][0] for k in ks)) / len(ks)
    lo, hi = boot(base, lit, ks, d_exact)
    dd = d_dec([(base[k], lit[k]) for k in ks])
    dlo, dhi = boot(base, lit, ks, d_dec)
    print("%-13s n=%-3d  accurate %+5.1f [%+5.1f,%+5.1f]   decisive %+5.1f [%+5.1f,%+5.1f]"
          % (name, len(ks), d, lo, hi, dd, dlo, dhi))

print()
print("=" * 96)
print("CORRUPTION  80% of answers flipped - truthful, paired")
print("=" * 96)
for name, tag, short in MODELS:
    base = load(runs.run(tag, "video"))
    lie = load(runs.run(tag, "lie80"))
    if base is None or lie is None:
        continue
    ks = sorted(set(base) & set(lie))
    d = 100.0 * (sum(lie[k][0] for k in ks) - sum(base[k][0] for k in ks)) / len(ks)
    lo, hi = boot(base, lie, ks, d_exact)
    dd = d_dec([(base[k], lie[k]) for k in ks])
    dlo, dhi = boot(base, lie, ks, d_dec)
    print("%-13s n=%-3d  accurate %+5.1f [%+5.1f,%+5.1f]   decisive %+5.1f [%+5.1f,%+5.1f]"
          % (name, len(ks), d, lo, hi, dd, dlo, dhi))
