"""(A) availability of what the model asked for, per condition; (B) failure decomposition in the
video condition; (C) joint report at the 10-atomic-test budget: accuracy, tau, availability."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from tau import acquired                                           # noqa: E402
import runs                                                        # noqa: E402
import glob, json, collections, statistics as st
ACCURATE = {"accurate", "exact"}   # grade names: current grader / earlier result files
B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
C = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}
ND = lambda v: sum(1 for x in C[v]["investigations"].values() if x.get("decisive"))


def load(pattern):
    out = {}
    for f in glob.glob(pattern, recursive=True):
        d = json.load(open(f))
        if d.get("video") and not d.get("error"): out[d["video"]] = d
    return out


def avail(d):
    """orders, orders that returned nothing, chart entries released"""
    n_ord = len(d.get("orders") or [])
    if d.get("trace"):   # multi-turn runs record each order round's matches in the trace
        nothing = sum(1 for s in d["trace"] if s.get("kind") == "order"
                      for g in (s.get("result") or []) if not g)
    else:
        nothing = sum(1 for l in (d.get("results") or []) if "not performed / not available" in l)
    return n_ord, nothing, len(set(d.get("served") or []))       # distinct entries released


def unknown_share(d):
    """history questions answered 'unknown' (anything but yes/no), as a count"""
    return sum(1 for v in (d.get("answers") or {}).values() if str(v).lower() not in ("yes", "no"))


MODELS = runs.MODELS
# (condition label, run names); Shuffled pools its three permutation runs, which gives per-case
# means averaged over the three permutations
COND = [("blind", lambda t: [runs.run(t, "blind")]), ("single frame", lambda t: [runs.run(t, "single")]),
        ("shuffled", runs.shuffled), ("video", lambda t: [runs.run(t, "video")]),
        ("multi-turn", lambda t: [runs.run(t, "multiturn")]), ("reference", lambda t: [runs.run(t, "reference")])]
print("A. WHAT THE MODEL ASKED FOR, AND WHAT THE CHART COULD ANSWER  (per case means; %% of orders returning 'not performed / not available')")
print("%-14s %-13s %5s %6s %8s %8s %9s %7s %6s %7s" % ("system", "condition", "n", "quest.", "yes%", "unk%", "orders", "unav%", "entr.", "tau%"))
avail_tab = {}
for nm, tag in MODELS:
    for cond, names in COND:
        Rs = [load(B + "/results/" + r + "/*/*.json") for r in names(tag)]
        if not all(Rs): print("%-14s %-13s   --  (missing %s)" % (nm, cond, ", ".join(names(tag)))); continue
        R = {(i, v): d for i, x in enumerate(Rs) for v, d in x.items()}   # pooled over runs
        q = [len(d.get("questions") or []) for d in R.values()]
        yes = [d.get("n_yes_answers", 0) for d in R.values()]
        unk = [unknown_share(d) for d in R.values()]
        av = [avail(d) for d in R.values()]
        no = sum(a[0] for a in av); nn = sum(a[1] for a in av)
        tau = 100.0 * sum(len(acquired(v, d.get("served"))) for (_, v), d in R.items()) / (len(Rs) * sum(ND(v) for v in C))
        avail_tab[(nm, cond)] = (100.0 * nn / max(no, 1))
        print("%-14s %-13s %5d %6.1f %8.1f %8.1f %9.1f %7.1f %6.1f %7.1f" % (nm, cond, len(R) // len(Rs), st.mean(q), 100.0 * sum(yes) / max(sum(q), 1),
              100.0 * sum(unk) / max(sum(q), 1),
              st.mean(a[0] for a in av), 100.0 * nn / max(no, 1), st.mean(a[2] for a in av), tau))
    print()

print("B. WHY THE VIDEO-CONDITION DIAGNOSIS IS WRONG  (non-exact cases only)")
print("%-14s %6s %8s | %22s %22s %22s" % ("system", "wrong", "of 71", "decisive obtained,", "decisive missed,", "decisive missed,"))
print("%-14s %6s %8s | %22s %22s %22s" % ("", "", "", "still wrong", "some orders answered", "nothing answered"))
for nm, tag in MODELS:
    R = load(B + "/results/%s/*/*.json" % runs.run(tag, "video"))
    G = runs.grades(runs.run(tag, "video"))
    wrong = [v for v in C if G.get(v, {}).get("grade") not in ACCURATE]
    a = b = c = 0
    for v in wrong:
        d = R.get(v)
        if not d: c += 1; continue
        if acquired(v, d.get("served")): a += 1
        elif (d.get("served") or []): b += 1
        else: c += 1
    n = len(wrong)
    print("%-14s %6d %7.1f%% | %10d (%3.0f%%)      %10d (%3.0f%%)      %10d (%3.0f%%)" % (
        nm, n, 100.0 * n / 71, a, 100.0 * a / n, b, 100.0 * b / n, c, 100.0 * c / n))

print("\nC. JOINT REPORT AT A FIXED BUDGET OF 10 ATOMIC TESTS, GPT-5.6-luna, video condition")
ARMS = {"model-selected": runs.run("luna", "budget10"), "checklist (fixed 10)": runs.run("luna", "checklist10"),
        "random 10": runs.run("luna", "random10")}
print("%-22s %6s %6s %7s %7s" % ("strategy", "acc%", "tau%", "unav%", "entr."))
for arm, D in ARMS.items():
    R = load(B + "/results/%s/*/*.json" % D)
    G = runs.grades(D)
    acc = 100.0 * sum(1 for v in R if G.get(v, {}).get("grade") in ACCURATE) / 71
    tau = 100.0 * sum(len(acquired(v, d.get("served"))) for v, d in R.items()) / sum(ND(v) for v in C)
    av = [avail(d) for d in R.values()]; unav = 100.0 * sum(a[1] for a in av) / max(sum(a[0] for a in av), 1)
    entr = st.mean(a[2] for a in av)
    print("%-22s %6.1f %6.1f %7.1f %7.1f" % (arm, acc, tau, unav, entr))
R = load(B + "/results/%s/*/*.json" % runs.run("luna", "video")); G = runs.grades(runs.run("luna", "video"))
av = [avail(d) for d in R.values()]
print("%-22s %6.1f %6.1f %7.1f %7.1f | (free budget: %.1f orders/case)" % ("released (free)", 100.0 * sum(1 for v in R if G.get(v, {}).get("grade") in ACCURATE) / 71,
      100.0 * sum(len(acquired(v, d.get("served"))) for v, d in R.items()) / sum(ND(v) for v in C), 100.0 * sum(a[1] for a in av) / sum(a[0] for a in av), st.mean(a[2] for a in av), st.mean(a[0] for a in av)))
print("\nD. DOES OBTAINING A DECISIVE ENTRY TRACK THE DIAGNOSIS?  (10-test arms pooled)")
JG = {arm: runs.grades(D) for arm, D in ARMS.items()}
RR_ = {arm: load(B + "/results/%s/*/*.json" % D) for arm, D in ARMS.items()}
got = collections.defaultdict(list)
for arm in ARMS:
    for v, d in RR_[arm].items():
        got[bool(acquired(v, d.get("served")))].append(JG[arm].get(v, {}).get("grade") in ACCURATE)
print("  decisive obtained: accuracy %.1f%% (n=%d) | not obtained: accuracy %.1f%% (n=%d)" % (
    100.0 * st.mean(got[True]), len(got[True]), 100.0 * st.mean(got[False]), len(got[False])))
