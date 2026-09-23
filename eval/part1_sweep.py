"""Run part1_probe over every clip in dataset/videos at each frame count.

Resumable: one JSON per (video, k), and an existing non-empty file is skipped, so the sweep can
be killed and relaunched without losing work.

usage: part1_sweep.py [K,K,K] [PAR]
env:   OUTROOT  results subdirectory, default part1 - give each model under test its own,
                since answers from different models must never be pooled
       MODEL, PROVIDER, BACKEND, ORKEY  passed through to part1_probe.py
"""
import os
import subprocess
import sys
import threading
import time

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTROOT = os.environ.get("OUTROOT", "part1")
KS = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "1,2,4,8,16,32,64,128").split(",")]
PAR = int(sys.argv[2]) if len(sys.argv) > 2 else 2

vids = []
for line in sorted(os.listdir(B + "/dataset/videos")):
    d = B + "/dataset/videos/" + line
    if not os.path.isdir(d):
        continue
    for v in sorted(os.listdir(d)):
        if v.endswith(".mp4"):
            vids.append((line, v, d + "/" + v))

jobs = []
for k in KS:
    for line, v, path in vids:
        out = "%s/results/%s/%s/%s__k%d.json" % (B, OUTROOT, line, v[:-4], k)
        if os.path.exists(out) and os.path.getsize(out) > 40:
            continue
        jobs.append((k, line, v, path, out))

print("%d clips, k=%s -> %d jobs, %d parallel, model=%s -> results/%s"
      % (len(vids), KS, len(jobs), PAR, os.environ.get("MODEL", "(default)"), OUTROOT), flush=True)
lock = threading.Lock()
done = [0]
t0 = time.time()


def worker(q):
    while True:
        with lock:
            if not q:
                return
            k, line, v, path, out = q.pop(0)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        r = subprocess.run([sys.executable, B + "/eval/part1_probe.py", path, str(k), out],
                           capture_output=True, text=True)
        with lock:
            done[0] += 1
            el = time.time() - t0
            rate = el / max(done[0], 1)
            print("[%3d/%3d] %5.0fs elapsed, eta %5.0fmin | %s"
                  % (done[0], len(jobs), el, (len(jobs) - done[0]) * rate / 60,
                     (r.stdout or r.stderr).strip()[:150]), flush=True)


q = list(jobs)
ts = [threading.Thread(target=worker, args=(q,)) for _ in range(PAR)]
for t in ts:
    t.start()
for t in ts:
    t.join()
print("sweep finished in %.1f min" % ((time.time() - t0) / 60), flush=True)
