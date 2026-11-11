"""Accuracy when the chart returns only entries reported in the source article (Appendix C.4).

Cells (replayed diagnosis turn on fixed trajectories, eval/controls/replay_reported.py): Bo/Br blind,
Vo/Vr video, Oo/Or oracle evidence; o = chart as served, r = derived entries withheld. Accuracy = share
graded exact over all paired cases (missing or failed = wrong). Paired case-level percentile bootstrap,
10,000 resamples. Reads results/stage2_part2_<tag>_rep_<cell>.json written by eval/part2_full_judge3.py.
"""
import json
import os
import random

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODELS = [("GPT-5.6-luna", "luna"), ("Gemma-4-31B", "gemma"), ("MiMo-v2.5", "mimo"),
          ("MiniMax-M3", "minimax"), ("Qwen3.8-flash", "qwen38")]
CELLS = ["Bo", "Br", "Vo", "Vr", "Oo", "Or"]
V = sorted(c["video"] for c in json.load(open(B + "/data/cases.json")))


def grades(tag, cell):
    p = "%s/results/stage2_part2_%s_rep_%s.json" % (B, tag, cell)
    if not os.path.exists(p):
        return None
    g = json.load(open(p))
    return {v: 1 if (g.get(v) or {}).get("grade") == "exact" else 0 for v in V}


A = {tag: {c: grades(tag, c) for c in CELLS} for _, tag in MODELS}


def present(tag, cell):
    p = "%s/results/stage2_part2_%s_rep_%s.json" % (B, tag, cell)
    return set(json.load(open(p))) if os.path.exists(p) else None


# missing = wrong, as in Table 2 (cases whose source consultation failed are absent from both cells of a pair).
# A case present in only one cell of an o/r pair (a replay skipped after repeated provider timeouts) would make
# that paired difference one-sided; drop such cases from every cell and model.
P = {t: {c: present(t, c) for c in CELLS} for _, t in MODELS}
DROP = sorted({v for t in P for a, b in (("Bo", "Br"), ("Vo", "Vr"), ("Oo", "Or"))
               if P[t][a] is not None and P[t][b] is not None for v in V if (v in P[t][a]) != (v in P[t][b])})
if DROP:
    print("dropped (replayed in only some cells):", DROP)
    V = [v for v in V if v not in DROP]
N = len(V)
print("%-14s" % "" + "".join("%7s" % c for c in CELLS))
for name, tag in MODELS:
    print("%-14s" % name + "".join("%7s" % ("--" if A[tag][c] is None else "%.1f" % (100 * sum(A[tag][c][v] for v in V) / N))
                                    for c in CELLS))

avail = [c for c in CELLS if all(A[t][c] is not None for _, t in MODELS)]
mean = {c: {v: sum(A[t][c][v] for _, t in MODELS) / 5 for v in V} for c in avail}
print("%-14s" % "mean of five" + "".join("%7s" % ("%.1f" % (100 * sum(mean[c].values()) / N) if c in mean else "--")
                                          for c in CELLS))

CON = [("video, reported-only - as served", lambda m, v: m["Vr"][v] - m["Vo"][v], ("Vr", "Vo")),
       ("oracle, reported-only - as served", lambda m, v: m["Or"][v] - m["Oo"][v], ("Or", "Oo")),
       ("blind, reported-only - as served", lambda m, v: m["Br"][v] - m["Bo"][v], ("Br", "Bo")),
       ("video - blind, as served", lambda m, v: m["Vo"][v] - m["Bo"][v], ("Vo", "Bo")),
       ("video - blind, reported-only", lambda m, v: m["Vr"][v] - m["Br"][v], ("Vr", "Br")),
       ("change in video - blind gap", lambda m, v: (m["Vr"][v] - m["Br"][v]) - (m["Vo"][v] - m["Bo"][v]),
        ("Vr", "Br", "Vo", "Bo")),
       ("oracle - video, as served", lambda m, v: m["Oo"][v] - m["Vo"][v], ("Oo", "Vo")),
       ("oracle - video, reported-only", lambda m, v: m["Or"][v] - m["Vr"][v], ("Or", "Vr"))]
rng = random.Random(0)
NB = 10000
print("\nPaired differences, mean of five systems (percentage points, 95% CI)")
for lab, f, need in CON:
    if not all(c in mean for c in need):
        print("  %-36s (cells missing)" % lab)
        continue
    d = [f(mean, v) for v in V]
    est = 100 * sum(d) / N
    bs = sorted(100 * sum(rng.choice(d) for _ in range(N)) / N for _ in range(NB))
    print("  %-36s %+6.1f [%+5.1f, %+5.1f]" % (lab, est, bs[int(0.025 * NB)], bs[int(0.975 * NB)]))
