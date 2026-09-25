"""Results by clinician-judged decidability (paper Appendix B, Tables 8 and 9).

The neurologist judged 22 clips unidentifiable from the video alone (data/decidability.json).
Table 8: Stage-1 sign recognition at K = 32 (sign graded "correct" by eval/part1_judge.py) and
Stage-2 accuracy in the video condition, decidable / undecidable, with a 10,000-resample bootstrap
interval of the gap. Table 9: Stage-2 accuracy with video, shuffled and single-frame input on the 49
decidable clips, with paired case-level bootstrap intervals.

usage: decidability.py      env DDX_ROOT (repository root, results/ underneath)
"""
import glob, json, os, random

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
D = json.load(open(B + "/data/decidability.json"))
DEC, UND = sorted(D["decidable"]), sorted(D["undecidable"])
ACCURATE = {"accurate", "exact"}
SYS = [("GPT-5.6-luna", "luna"), ("Gemma-4-31B", "gemma"), ("MiMo-v2.5", "mimo"), ("MiniMax-M3", "minimax"),
       ("Qwen3.8-flash", "qwen38")]
STAGE2 = {"video": "part2_%s_vid", "shuffled": "part2_%s_shuf32", "single": "part2_%s_frame1"}   # OUTROOT names
rng = random.Random(0)


def sign32(tag):
    out = {}
    for f in glob.glob("%s/results/part1_judge/%s__*__k32.json" % (B, tag)):
        d = json.load(open(f)); out[d["video"]] = 1.0 if (d.get("verdict") or {}).get("sign") == "correct" else 0.0
    return out


def acc(root):
    p = "%s/results/stage2_%s.json" % (B, root)
    g = json.load(open(p)) if os.path.exists(p) else {}
    return {v: 1.0 if (r.get("grade") in ACCURATE) else 0.0 for v, r in g.items()}


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
    s, a = sign32(tag), acc(STAGE2["video"] % tag)
    (l1, h1), (l2, h2) = gap_ci(s), gap_ci(a)
    print("%-14s sign %5.1f / %5.1f  %+5.1f [%+.1f, %+.1f] | accuracy %5.1f / %5.1f  %+5.1f [%+.1f, %+.1f]" % (
        name, rate(s, DEC), rate(s, UND), rate(s, DEC) - rate(s, UND), l1, h1,
        rate(a, DEC), rate(a, UND), rate(a, DEC) - rate(a, UND), l2, h2))

print("\nTable 9  (49 decidable clips)")
for name, tag in SYS:
    g = {k: acc(r % tag) for k, r in STAGE2.items()}
    row = "%-14s video %5.1f shuffled %5.1f single %5.1f" % (name, rate(g["video"], DEC), rate(g["shuffled"], DEC), rate(g["single"], DEC))
    for a, b in (("video", "shuffled"), ("video", "single"), ("shuffled", "single")):
        lo, hi = paired_ci(g[a], g[b], DEC)
        row += " | %s-%s %+5.1f [%+.1f, %+.1f]" % (a, b, rate(g[a], DEC) - rate(g[b], DEC), lo, hi)
    print(row)
