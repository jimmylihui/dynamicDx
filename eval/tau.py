"""Source-workup coverage tau as the paper defines it (Section 3.3).

For each case, the decisive entries T are the chart entries flagged `decisive`. A decisive entry
counts as acquired when it, or a verified equivalent entry of the same chart
(data/equivalent_entries.json), was returned in the consultation; acquired entries are deduplicated
within a case. Tau pools over the 71 cases: sum of acquired decisive entries over sum of decisive
entries, and a case without a usable consultation contributes zero acquired entries.

usage: tau.py <run> [<run> ...]      runs are directories under results/
"""
import glob
import json
import os
import sys

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}
EQ = json.load(open(B + "/data/equivalent_entries.json"))["equivalences"]
DEC = {v: {k for k, x in c["investigations"].items() if x.get("decisive")} for v, c in C.items()}


def acquired(video, served):
    s = set(served or [])
    got = s & DEC[video]
    for a in s:
        got |= set(EQ.get(video, {}).get(a, []))
    return got & DEC[video]


def tau(run):
    got = {}
    for f in glob.glob("%s/results/%s/*/*.json" % (B, run)):
        d = json.load(open(f))
        if d.get("video") in C and not d.get("error"):
            got[d["video"]] = len(acquired(d["video"], d.get("served")))
    return 100.0 * sum(got.values()) / sum(len(DEC[v]) for v in C), len(got)


if __name__ == "__main__":
    for r in sys.argv[1:]:
        t, n = tau(r)
        print("%-40s tau %5.1f%%  (%d usable consultations of %d)" % (r, t, n, len(C)))
