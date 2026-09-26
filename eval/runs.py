"""One naming scheme for the result folders every analysis script reads.

A run is written by the harness to results/<run>/<category>/<clip>.json (OUTROOT=<run>) and graded
by eval/part2_full_judge3.py (ROOT=<run>) into results/stage2_<run>.json. Runs are named
part2_<model tag>_<condition>; the Shuffled condition has three runs, one per permutation seed.
"""
import json
import os

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODELS = [("GPT-5.6-luna", "luna"), ("Gemma-4-31B", "gemma"), ("MiMo-v2.5", "mimo"),
          ("MiniMax-M3", "minimax"), ("Qwen3.8-flash", "qwen38")]

# condition -> run suffix (and the harness flags that produce it, see README)
SUFFIX = {
    "blind": "novid",                  # NOVIDEO=1
    "single": "frame1",                # KFRAMES=1
    "video": "vid",                    # (none)
    "own": "textself",                 # SIGNTEXT=self SELFFILE=...
    "reference": "textgt",             # SIGNTEXT=gt
    "oracle": "oracle",                # ORACLE=1 ORACLE_SRC=part2_<tag>_vid
    "multiturn": "seq",                # eval/part2_seq2.py
    "original": "lit_orig",            # SPACE=union_own UNIONFILE=<Original list>
    "source_clean": "lit_clean",       #                 ... <Source-clean list>
    "strict": "lit_strict",            #                 ... <Strict no-answer list>
    "own_candidates": "own",           #                 ... own_dx_<tag>.json
    "mismatched": "mismatched",        #                 ... build_mismatched.py output
    "lie40": "lie40",                  # eval/part2_lie2.py RATIO=40
    "lie80": "lie80",                  # eval/part2_lie2.py RATIO=80
    "budget10": "budget10",            # eval/controls/part2_orders.py MODE=budget K=10
    "checklist10": "chk10",            # MODE=checklist LIST=C10
    "checklist15": "chk15",            # MODE=checklist LIST=C15
    "random10": "rand10",              # MODE=random K=10
    "atomic_named": "atomic_named",    # MODE=atomic_named LIST=C10
    "atomic_matched": "atomic_matched",  # MODE=atomic_matched LIST=C10
    "budget_single": "budget_single",  # MODE=budget_single
}
SHUFFLE_SEEDS = (0, 1, 2)


def run(tag, cond):
    return "part2_%s_%s" % (tag, SUFFIX[cond])


def shuffled(tag):
    """the three Shuffled runs (SHUFFLE=1 SHUFFLE_SEED=0,1,2)"""
    return ["part2_%s_shuf%d" % (tag, s) for s in SHUFFLE_SEEDS]


def grades(root, required=True):
    """{video: {"grade": ...}} for a run"""
    for p in ("%s/results/stage2_%s.json" % (B, root), "%s/results/judge/fulljudge_%s.json" % (B, root)):
        if os.path.exists(p):
            return json.load(open(p))
    if required:
        raise FileNotFoundError("no grades for run %s (run eval/part2_full_judge3.py ROOT=%s)" % (root, root))
    return None
