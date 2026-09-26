"""Results by clinician-judged decidability (paper Appendix B, Tables 8 and 9).

The neurologist judged 22 clips unidentifiable from the video alone (data/decidability.json).
Table 8: Stage-1 sign recognition at K = 32 (sign graded "correct" by eval/part1_judge.py) and
Stage-2 accuracy in the video condition, decidable / undecidable, with a 10,000-resample bootstrap
interval of the gap. Table 9: Stage-2 accuracy with video, shuffled and single-frame input on the 49
decidable clips, with paired case-level bootstrap intervals; a clip's shuffled accuracy is the mean
over the three permutation runs.

usage: decidability.py      env DDX_ROOT (repository root, results/ underneath)
"""
import glob, json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runs                                                           # noqa: E402

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
D = json.load(open(B + "/data/decidability.json"))
DEC, UND = sorted(D["decidable"]), sorted(D["undecidable"])
ACCURATE = {"accurate", "exact"}
SYS = runs.MODELS
rng = random.Random(0)


def sign32(tag):
    out = {}
    for f in glob.glob("%s/results/part1_judge/%s__*__k32.json" % (B, tag)):
        d = json.load(open(f)); out[d["video"]] = 1.0 if (d.get("verdict") or {}).get("sign") == "correct" else 0.0
    return out


def acc(root):
    g = runs.grades(root)       # a missing run raises rather than reading as 0% accuracy
    return {v: 1.0 if (r.get("grade") in ACCURATE) else 0.0 for v, r in g.items()}


def acc_shuffled(tag):
    """per-clip mean over the three Shuffled permutations"""
    gs = [acc(r) for r in runs.shuffled(tag)]
    return {v: sum(g.get(v, 0.0) for g in gs) / len(gs) for v in DEC + UND}


def stage2(tag):
    return {"video": acc(runs.run(tag, "video")), "shuffled": acc_shuffled(tag),
            "single": acc(runs.run(tag, "single"))}


rate = lambda g, s: 100.0 * sum(g.get(v, 0.0) for v in s) / len(s)


def gap_ci(g, n=10000):
    bs = []
    for _ in range(n):
        a = [rng.choice(DEC) for _ in DEC]; b = [rng.choice(UND) for _ in UND]
        bs.append(rate(g, a) - rate(g, b))
    bs.sort(); return bs[int(0.025 * n)], bs[int(0.975 * n)]


def paired_ci(g1, g2, cases, n=10000):
    bs = []
    for _ in range(n):
        s = [rng.choice(cases) for _ in cases]
        bs.append(rate(g1, s) - rate(g2, s))
    bs.sort(); return bs[int(0.025 * n)], bs[int(0.975 * n)]


print("Table 8  (decidable n=%d / undecidable n=%d)" % (len(DEC), len(UND)))
for name, tag in SYS:
    s, a = sign32(tag), acc(runs.run(tag, "video"))
    (l1, h1), (l2, h2) = gap_ci(s), gap_ci(a)
    print("%-14s sign %5.1f / %5.1f  %+5.1f [%+.1f, %+.1f] | accuracy %5.1f / %5.1f  %+5.1f [%+.1f, %+.1f]" % (
        name, rate(s, DEC), rate(s, UND), rate(s, DEC) - rate(s, UND), l1, h1,
        rate(a, DEC), rate(a, UND), rate(a, DEC) - rate(a, UND), l2, h2))

print("\nTable 9  (49 decidable clips)")
for name, tag in SYS:
    g = stage2(tag)
    row = "%-14s video %5.1f shuffled %5.1f single %5.1f" % (name, rate(g["video"], DEC), rate(g["shuffled"], DEC), rate(g["single"], DEC))
    for a, b in (("video", "shuffled"), ("video", "single"), ("shuffled", "single")):
        lo, hi = paired_ci(g[a], g[b], DEC)
        row += " | %s-%s %+5.1f [%+.1f, %+.1f]" % (a, b, rate(g[a], DEC) - rate(g[b], DEC), lo, hi)
    print(row)
