import os
# -*- coding: utf-8 -*-
"""Order-selection ablation, replayed from a published Part-2 run.

The video, the history questions and the patient's yes/no/unknown answers are held
at what the published run produced - only the investigation turn changes:

  MODE=budget     the model re-orders under an itemised budget of K atomic
                  tests (no bundling, no category orders)
  MODE=checklist  the model does not choose: a fixed, case-independent
                  checklist is submitted on its behalf
  MODE=random     K test names drawn at random (seeded per clip) from the
                  pooled investigation vocabulary of every chart

Everything downstream (matching, chart release, diagnosis) is unchanged, so
the result is directly comparable with the released arms.

usage: part2_orders.py SRC_RUN OUT_JSON
env:   ORKEY, MODE, K, LIST, MODEL, PROVIDER, JUDGE (chart matcher), JPROVIDER, ROLE
"""
import base64, glob, json, os, re, shutil, subprocess, sys, tempfile, urllib.request

B = os.environ.get("DDX_ROOT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ORKEY = os.environ["ORKEY"]
MODEL = os.environ.get("MODEL", "openai/gpt-5.6-luna")
PROV = os.environ.get("PROVIDER", "OpenAI")
MODE = os.environ.get("MODE", "budget")
JUDGE = os.environ.get("JUDGE", "deepseek/deepseek-v4.1-flash")
JPROV = os.environ.get("JPROVIDER", "")
K = int(os.environ.get("K", "10"))
LIST = os.environ.get("LIST", "C10")
SRC, OUT = sys.argv[1], sys.argv[2]
FF = os.environ.get("FFMPEG", "ffmpeg")

src = open(B + "/eval/part2_full.py").read()
def grab(n):
    return re.search(r'^%s = """(.*?)"""' % n, src, re.S | re.M).group(1)
T1, T3, MATCH_I = grab("T1"), grab("T3"), grab("MATCH_I")
T1_NOVID = grab("T1_NOVID")
_OPENING = {"neurologist": "You are a neurologist seeing a new patient.",
            "doctor": "You are a doctor seeing a new patient."}[os.environ.get("ROLE", "doctor")]

T2_BUDGET = """The patient answered:

%s

You may now investigate. There is no fixed list to choose from - name whatever you would actually
order, in your own words: bedside examination manoeuvres, blood tests, imaging, electrophysiology,
invasive procedures, or a therapeutic trial. A therapeutic trial is returned only if you name that
specific trial; asking to "try treatment" returns nothing.

You have a budget of exactly %d investigations. Each numbered line must name ONE single test and
nothing else. Do not combine several tests on one line, do not join them with "and", "plus", "with"
or a comma-separated list, and do not write a category that stands for many tests, such as "routine
bloods", "metabolic screen" or "full neurological examination". Spend the budget on the tests most
likely to settle the diagnosis.

Exactly %d lines, numbered, one investigation per line. Name the test, not what you expect it to
show. Nothing else."""


MQ3 = """A doctor asked a patient these yes/no questions:

%s

The patient record documents these features as PRESENT:

%s

and these features as ABSENT:

%s

The record documents nothing else about this patient.

For each question reply:
- "yes"     if the record explicitly establishes the queried finding is present
- "no"      if the record explicitly establishes the queried finding is absent
- "unknown" if the record does not settle it
A finding that is in neither list is unreported: answer "unknown", never "no".
For a compound question answer "unknown" unless the record settles every part of it.

Reply with ONLY a JSON object: {"<question number>": "yes"|"no"|"unknown", ...}"""

CHECKLISTS = {
    # a generic, case-independent work-up for an undifferentiated movement disorder
    "C10": [
        "muscle tone examination",
        "limb strength (MRC) examination",
        "bedside eye-movement examination",
        "full blood count",
        "serum electrolytes, urea and creatinine",
        "liver function tests",
        "blood glucose and HbA1c",
        "TSH and free T4",
        "vitamin B12",
        "MRI brain with contrast",
    ],
    # the same, extended with the standard second-line neurological tests
    "C15": [
        "muscle tone examination",
        "limb strength (MRC) examination",
        "bedside eye-movement examination",
        "gait examination",
        "full blood count",
        "serum electrolytes, urea and creatinine",
        "liver function tests",
        "blood glucose and HbA1c",
        "TSH and free T4",
        "vitamin B12",
        "serum copper and caeruloplasmin",
        "MRI brain with contrast",
        "EEG",
        "nerve conduction studies and electromyography",
        "lumbar puncture with CSF analysis",
    ],
}

def post(model, messages, mx=4000, imgs=0):
    prov = JPROV if model == JUDGE and JUDGE != MODEL else PROV
    body = json.dumps({"model": model, "temperature": 0, "messages": messages,
                       "reasoning": {"enabled": True}, "max_tokens": mx,
                       **({"provider": {"order": [prov], "allow_fallbacks": False, "sort": "price"}} if prov else {})}).encode()
    err = None
    for _ in range(5):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=300).read().decode())
            return r["choices"][0]["message"]["content"] or ""
        except Exception as e:
            err = e
    raise RuntimeError(err)

def as_json(t):
    m = re.search(r"\{.*\}", t or "", re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except ValueError:
        return None

def numbered(t):
    out = []
    for line in (t or "").splitlines():
        if re.match(r"^\s*\d+[.)]", line):
            s = re.sub(r"^\s*\d+[.)]\s*", "", line).strip().strip("*").strip()
            if 3 < len(s) < 600:
                out.append(s)
    return out

cases = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}
VOCAB = sorted({k for c in cases.values() for k in c["investigations"]})

d = json.load(open(SRC))
c = cases[d["video"]]
qs = d["questions"]
if os.environ.get("THREEVAL") == "1":
    st = c["part2_yes_no"]["symptom_table"]
    _yes = [k for k, v in st.items() if v == "yes"]
    _nos = [k for k, v in st.items() if v != "yes"]
    _r = as_json(post(JUDGE, [{"role": "user", "content": MQ3 % (
        "\n".join("%d. %s" % (i, q) for i, q in enumerate(qs, 1)),
        "\n".join("- " + y for y in _yes), "\n".join("- " + n for n in _nos))}], 6000)) or {}
    ans = {str(i): str(_r.get(str(i), "unknown")).lower() for i in range(1, len(qs) + 1)}
else:
    ans = {str(i): str(d["answers"].get(str(i), "unknown")).lower() for i in range(1, len(qs) + 1)}
qa = ["%d. %s  ->  %s" % (i, q, ans[str(i)]) for i, q in enumerate(qs, 1)]

tmp = tempfile.mkdtemp(prefix="ord_")
try:
    p = "%s/dataset/videos/%s/%s" % (B, c["line"], c["video"])
    o = subprocess.run([FF, "-i", p], capture_output=True, text=True).stderr
    mm = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", o)
    dur = int(mm.group(1)) * 3600 + int(mm.group(2)) * 60 + float(mm.group(3))
    subprocess.run([FF, "-y", "-i", p, "-vf", "fps=%.5f,scale=512:-1" % (32 / max(dur, .1)),
                    "-frames:v", "32", tmp + "/f_%03d.jpg"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    fs = sorted(glob.glob(tmp + "/*.jpg"))
    b64 = [base64.b64encode(open(f, "rb").read()).decode() for f in fs]
finally:
    shutil.rmtree(tmp, ignore_errors=True)

NOVID = bool(d.get("novideo"))
if NOVID:
    b64 = []
    content1 = [{"type": "text", "text": T1_NOVID}]
else:
    content1 = ([{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b}} for b in b64]
                + [{"type": "text", "text": T1 % (_OPENING, len(fs), "%.0f" % dur, "")}])
msgs = [{"role": "user", "content": content1},
        {"role": "assistant", "content": "\n".join("%d. %s" % (i, q) for i, q in enumerate(qs, 1))}]

if MODE in ("checklist", "random"):
    if MODE == "random":
        import random as _r
        # a deliberately unskilled strategy: K test names drawn uniformly from the vocabulary of
        # every chart in the benchmark, seeded by the clip so the draw is reproducible
        tests = _r.Random("%s|%d" % (d["video"], K)).sample(VOCAB, K)
    else:
        tests = list(CHECKLISTS[LIST])
    t_ord = "\n".join("%d. %s" % (i, t) for i, t in enumerate(tests, 1))
    msgs += [{"role": "user", "content": T2_BUDGET % ("\n".join(qa), len(tests), len(tests))},
             {"role": "assistant", "content": t_ord}]
else:
    msgs += [{"role": "user", "content": T2_BUDGET % ("\n".join(qa), K, K)}]
    t_ord = post(MODEL, msgs, imgs=len(b64))
    tests = [t.split("---", 1)[0].strip() for t in numbered(t_ord)][:K]
    if not tests:
        json.dump(dict(error="no orders", video=d["video"]), open(OUT, "w"))
        sys.exit(0)
    msgs += [{"role": "assistant", "content": t_ord}]

inv = c["investigations"]
menu = "\n".join("- %s%s" % (k, " [NAMED-ONLY]" if v.get("explicit_only") else "")
                 for k, v in inv.items())
cov = as_json(post(JUDGE, [{"role": "user", "content": MATCH_I % (
    "\n".join("%d. %s" % (i, t) for i, t in enumerate(tests, 1)), menu)}], 8000)) or {}
lines, served = [], []
for i, t in enumerate(tests, 1):
    got = [k for k in (cov.get(str(i)) or []) if k in inv]
    lines.append("%d. %s" % (i, t))
    if not got:
        lines.append("     not performed / not available")
        continue
    for k in got:
        served.append(k)
        lines.append("     %s: %s" % (k, inv[k]["v"]))

msgs += [{"role": "user", "content": T3 % "\n".join(lines)}]
t_dx = post(MODEL, msgs, 1500)
mo = re.search(r"DIAGNOS\w*\s*:\s*(.+)", t_dx)
served_u = sorted(set(served))
r = dict(video=d["video"], line=c["line"], mode=MODE, budget=(len(tests)),
         list=(LIST if MODE == "checklist" else MODE), questions=qs, answers=ans,
         orders=tests, served=served_u, results=lines, order_raw=t_ord,
         dx=(mo.group(1).strip() if mo else (t_dx.strip().splitlines() or [""])[0]), dx_raw=t_dx,
         decisive_served=[k for k in served_u if inv[k].get("decisive")],
         n_decisive=sum(1 for v in inv.values() if isinstance(v, dict) and v.get("decisive")),
         entries_per_order=round(len(served) / max(len(tests), 1), 2))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(r, open(OUT, "w"), indent=1, ensure_ascii=False)
print("%-46s %s n_ord=%2d ent=%2d e/o=%.2f dec=%d/%d" % (
    d["video"][:46], MODE[:4], len(tests), len(served_u), r["entries_per_order"],
    len(r["decisive_served"]), r["n_decisive"]))
