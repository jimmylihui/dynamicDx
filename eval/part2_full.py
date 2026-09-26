"""Part 2 end to end: watch, ask, examine, order, diagnose.

Five turns per case. The doctor sees 32 frames and, in the candidate arms, the Part 1 literature
list. It asks yes/no questions; the patient answers. It orders investigations; the chart answers.
It then names a diagnosis.

Neither the patient nor the chart is improvised. The judge is used ONLY to match free text to the
case file - which symptom a question is asking about, which menu entries an order covers - and
every value handed back to the doctor is read out of cases_all.json by this script. A judge that
also wrote the answers could invent a finding that settles the case, and the run would measure the
judge rather than the doctor.

Three rules are enforced against the doctor:
  - the patient answers yes / no only for features the record documents as present / absent, and
    unknown otherwise: a feature the record does not mention is never answered no
  - the chart holds the case's fixed entries: results the source article reports (p: reported)
    and, on the shared line menu, values expected for the presentation (p: derived); an
    investigation it does not hold returns "not performed / not available"
  - a therapeutic trial is returned only when named specifically, never for a blanket request

usage: part2_full.py [NTHREADS]
env:   ORKEY, SPACE (none|model|oracle), KFRAMES, OUTROOT, MODEL, JUDGE, NOVIDEO, SHUFFLE, SHUFFLE_SEED, SIGNTEXT,
       ORACLE
"""
import base64
import glob
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORKEY = os.environ["ORKEY"]
MODEL = os.environ.get("MODEL", "openai/gpt-5.6-luna")
JUDGE = os.environ.get("JUDGE", "deepseek/deepseek-v4.1-flash")
PROVIDER = os.environ.get("PROVIDER", "OpenAI")
JPROVIDER = os.environ.get("JPROVIDER", "")
REASONING = json.loads(os.environ.get("REASONING", '{"enabled": false}'))
# 0 = send no max_tokens at all and let the provider decide
MAXTOK = int(os.environ.get("MAXTOK", "-1"))
TIMEOUT = int(os.environ.get("TIMEOUT", "300"))


def _prov(model):
    """The judge keeps its own pin: it is the same model in every run, the doctor is not."""
    return JPROVIDER if model == JUDGE and JUDGE != MODEL else PROVIDER
SPACE = os.environ.get("SPACE", "none")
ORDERSTYLE = os.environ.get("ORDERSTYLE", "open")
NOVIDEO = os.environ.get("NOVIDEO", "0") == "1"
# the arm that separates the modality from the information it carries: the clip is withheld but
# the phenomenology is handed over in words. "gt" uses the clinician-written reference sign.
SIGNTEXT = os.environ.get("SIGNTEXT", "")
# hand the decisive evidence over instead of letting the model choose what to order: the gap
# between this arm and the ordinary consultation is what acquisition costs
ORACLE = os.environ.get("ORACLE", "0") == "1"
# "self" hands back the model's own Part 1 description, stripped of its differential
SELFFILE = os.environ.get("SELFFILE", "")
selfsign = json.load(open(SELFFILE)) if SELFFILE else {}
ROLE = os.environ.get("ROLE", "doctor")
_OPENING = {"neurologist": "You are a neurologist seeing a new patient.",
            "doctor": "You are a doctor seeing a new patient."}[ROLE]
K = int(os.environ.get("KFRAMES", "32"))
# Two rungs between "knows nothing" and "sees the whole clip". SHUFFLE keeps the frames and their
# count and destroys only their order, which separates what the frames contain from the motion
# their sequence carries; the permutation is seeded per clip so the arm is reproducible. CHIEF
# gives no frames at all, only what a referral letter would carry - age, sex, and the complaint the
# patient presents with - which is the non-visual context the blind arm withholds along with the
# video. The complaint is the first affirmative entry of the case's own symptom table, so it is
# patient-reported and taken from the record rather than written for this experiment.
SHUFFLE = os.environ.get("SHUFFLE", "0") == "1"
SHUFFLE_SEED = int(os.environ.get("SHUFFLE_SEED", "0"))   # paper: three permutations, seeds 0, 1, 2
CHIEF = os.environ.get("CHIEF", "0") == "1"
OUTROOT = os.environ.get("OUTROOT", "part2_full_" + SPACE)
FF = os.environ.get("FFMPEG", "ffmpeg")
SRC = {"model": os.environ.get("DDX_WORK", "/tmp") + "/openspace_part1_oldp_luna.json",
       "oracle": os.environ.get("DDX_WORK", "/tmp") + "/openspace_oracle.json",
       # the model own hypotheses followed by the retrieved causes: the two recover different
       # patients, so their union is what a deployed system would actually hold
       "union": os.environ.get("DDX_WORK", "/tmp") + "/openspace_union.json",
       "union_old": os.environ.get("DDX_WORK", "/tmp") + "/openspace_union_old.json",
       "union_own": os.environ.get("UNIONFILE", "")}.get(SPACE)

CAND = """A literature search on the signs visible in this video returned the following reported causes.
The list is not guaranteed to contain this patient's cause, and most entries in it are wrong for
this patient:

%s

"""

T1 = """%s Above are %d frames sampled across a
%s-second video of the consultation, in order.

%sYou may now take a history, but under one constraint: **Ask yes/no questions. The environment
returns yes, no, or unknown when the record does not establish the answer**, and the patient will
answer only yes, no, or unknown. Anything you do not ask, you do not learn.

Ask as many or as few questions as you judge this patient needs. Stop when you believe another
question would not change what you think is wrong. Put them in the order you would ask them - most
informative first.

One question per line, numbered. Nothing else."""

T1_CHIEF = """You are a doctor. A new patient has been referred to you and you have not yet seen
or examined them. All you have been told is this:

  %s

You may now take a history, but under one constraint: **Ask yes/no questions. The environment
returns yes, no, or unknown when the record does not establish the answer**, and the patient will
answer only yes, no, or unknown. Anything you do not ask, you do not learn.

Ask as many or as few questions as you judge this patient needs. Stop when you believe another
question would not change what you think is wrong. Put them in the order you would ask them - most
informative first.

One question per line, numbered. Nothing else."""

T1_TEXT = """You are a doctor. A new patient has been referred to you. You have not seen or
examined them yourself, but a colleague who did records the following:

%s

You may now take a history, but under one constraint: **Ask yes/no questions. The environment
returns yes, no, or unknown when the record does not establish the answer**, and the patient will
answer only yes, no, or unknown. Anything you do not ask, you do not learn.

Ask as many or as few questions as you judge this patient needs. Stop when you believe another
question would not change what you think is wrong. Put them in the order you would ask them - most
informative first.

One question per line, numbered. Nothing else."""

T1_NOVID = """You are a doctor. A new patient has been referred to you and you have not yet seen
or examined them. You know nothing about them at all.

You may now take a history, but under one constraint: **Ask yes/no questions. The environment
returns yes, no, or unknown when the record does not establish the answer**, and the patient will
answer only yes, no, or unknown. Anything you do not ask, you do not learn.

Ask as many or as few questions as you judge this patient needs. Stop when you believe another
question would not change what you think is wrong. Put them in the order you would ask them - most
informative first.

One question per line, numbered. Nothing else."""


T2 = """The patient answered:

%s

You may now investigate. There is no fixed list to choose from.
Name whatever you would actually order, in your own words:
bedside examination manoeuvres, blood tests, imaging,
electrophysiology, invasive procedures, or a therapeutic trial.
A therapeutic trial is returned only if you name that specific
trial. Asking to "try treatment" returns nothing.

Order as many or as few investigations as you judge this patient
needs. Stop when another test would not change what you think is
wrong. Put the investigations most likely to settle the diagnosis
first.

One investigation per line, numbered. Name the test, not what you expect it to show. Nothing else."""

T2_HYPO = """The patient answered:

%s

Before investigating, state the diagnosis you currently think most likely, and up to three
alternatives you would want to exclude.

Then order investigations. For each one, name the test and the hypothesis it is meant to confirm or
exclude. Order only tests whose result would change what you think; do not order a test whose
result you can already predict. A therapeutic trial is returned only if you name that specific
trial.

Reply in exactly this format, nothing else:
LEADING: <one line>
ALTERNATIVES: <up to three, one per line>
1. <test> --- <the hypothesis it discriminates>
2. <test> --- <the hypothesis it discriminates>
..."""


T3_ORACLE = """The patient answered:

%s

The investigations that established this patient's diagnosis have been carried out for you. Their
results are:

%s

Now give your diagnosis. State the single diagnosis you believe is correct - the disease entity
and its cause, as specifically as the evidence allows - then, on separate lines, up to three
alternatives you would still consider.

Begin with "DIAGNOSIS:" followed by the single answer on one line."""

T3 = """The results are:

%s

For orders marked "not performed / not available", no documented result is available in this
environment. Do not infer a result.

Now give your diagnosis. State the single diagnosis you believe is correct - the disease entity
and its cause, as specifically as the evidence allows - then, on separate lines, up to three
alternatives you would still consider.

Begin with "DIAGNOSIS:" followed by the single answer on one line."""

MATCH_Q = """A doctor asked a patient these yes/no questions:

%s

The patient's documented features are:

%s

Answer each question using only the documented features above.

Use exactly one of the following responses:
- "yes" if the documented features explicitly establish that the complete statement is true;
- "no" if the documented features explicitly establish that the complete statement is false;
- "unknown" if the documented features do not provide enough information to determine whether
  the complete statement is true or false.

Do not infer unreported features. Absence from the documented feature table does not imply
absence of the clinical finding and must not by itself produce a "no" response.

For compound questions, return yes or no only when the documented evidence determines the truth
of the complete statement. Otherwise, return unknown.

Reply with ONLY a JSON object: {"<question number>": "yes"|"no"|"unknown", ...}"""


def symptom_table(c):
    """The record as the matcher sees it: every documented feature with its documented value."""
    return "\n".join("- %s: %s" % (k, v) for k, v in c["part2_yes_no"]["symptom_table"].items())


def three_valued(a):
    a = str(a).strip().lower()
    return a if a in ("yes", "no") else "unknown"


MATCH_I = """A doctor ordered these investigations. A numbered line may bundle several tests.

%s

This chart holds results for exactly these entries:

%s

For each numbered order, list the chart entries it covers - matching on what the test is, not on
wording. An order covers an entry only if it genuinely asks for that test. Entries marked
[NAMED-ONLY] are therapeutic trials: list one only if that specific trial is named, never for a
general request to try treatment.

Reply with ONLY a JSON object mapping each order number to a list of chart entry names, exactly
as written above: {"1": ["..."], "2": [], ...}"""


def duration(p):
    o = subprocess.run([FF, "-i", p], capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", o)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 20.0


def frames(p, k, tmp):
    d = duration(p)
    subprocess.run([FF, "-y", "-i", p, "-vf", "fps=%.5f,scale=512:-1" % (k / max(d, 0.1)),
                    "-frames:v", str(k), tmp + "/f_%03d.jpg"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sorted(glob.glob(tmp + "/*.jpg")), d


def post(model, messages, mx, imgs=0):
    payload = {"model": model, "temperature": 0, "messages": messages,
               "reasoning": REASONING, "usage": {"include": True},
               **({"provider": {"order": [_prov(model)], "allow_fallbacks": False, "sort": "price"}} if _prov(model) else {})}
    cap = mx if MAXTOK < 0 else MAXTOK
    if cap:
        payload["max_tokens"] = cap
    body = json.dumps(payload).encode()
    for attempt in range(5):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=TIMEOUT).read().decode())
            if "error" in r and not r.get("choices"):
                raise RuntimeError(str(r["error"])[:200])
            pt = (r.get("usage") or {}).get("prompt_tokens", 0) or 0
            if imgs and pt < 40 * imgs:
                raise RuntimeError("IMAGES_DROPPED %d/%d" % (pt, imgs))
            ch = r["choices"][0]
            t = ch["message"]["content"] or ""
            u = dict(r.get("usage") or {})
            u["finish_reason"] = ch.get("finish_reason")
            if t:
                return t, u
        except Exception:                                          # noqa: BLE001
            time.sleep(4 * (attempt + 1))
    return "", {}


def as_json(txt):
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except Exception:                                              # noqa: BLE001
        return None


def numbered(txt):
    out = []
    for line in txt.splitlines():
        if re.match(r"^\s*\d+[.)]", line):
            s = re.sub(r"^\s*\d+[.)]\s*", "", line).strip().strip("*").strip()
            if 3 < len(s) < 600:
                out.append(s)
    return out


space = json.load(open(SRC)) if SRC else {}
cases = json.load(open(B + "/data/cases.json"))
todo = [c for c in cases if not SRC or space.get(c["video"], {}).get("causes")]
print("SPACE=%s -> %d cases -> results/%s" % (SPACE, len(todo), OUTROOT), flush=True)
lock = threading.Lock()


def run(c):
    tmp = tempfile.mkdtemp(prefix="p2f_")
    try:
        fs, dur = frames("%s/dataset/videos/%s/%s" % (B, c["line"], c["video"]), K, tmp)
        b64 = [base64.b64encode(open(f, "rb").read()).decode() for f in fs]
        if SHUFFLE:
            random.Random(c["video"] if SHUFFLE_SEED == 0 else "%s#%d" % (c["video"], SHUFFLE_SEED)).shuffle(b64)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    cands = space.get(c["video"], {}).get("causes") if SRC else None
    head = CAND % "; ".join(cands) if cands else ""

    if SIGNTEXT:
        b64 = []
        sign = (selfsign.get(c["video"]) if SIGNTEXT == "self"
                else c["part1_video_only"]["visible_sign"])
        if not sign or sign.strip().upper() == "NONE":
            return dict(error="no self description")
        body = T1_TEXT % sign
        content1 = [{"type": "text", "text": (head + body) if head else body}]
    elif CHIEF:
        b64 = []
        ys = [k for k, v in c["part2_yes_no"]["symptom_table"].items() if v == "yes"]
        d = c["part2_yes_no"].get("demographics") or {}
        ref = "A %s-year-old %s presenting with %s." % (d.get("age", "?"), d.get("sex", "patient"),
                                                        ys[0] if ys else "a neurological complaint")
        body = T1_CHIEF % ref
        content1 = [{"type": "text", "text": (head + body) if head else body}]
    elif NOVIDEO:
        b64 = []
        content1 = [{"type": "text", "text": (head + T1_NOVID) if head else T1_NOVID}]
    else:
        content1 = ([{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b}}
                     for b in b64]
                    + [{"type": "text", "text": T1 % (_OPENING, len(fs), "%.0f" % dur, head)}])
    msgs = [{"role": "user", "content": content1}]
    t_ask, u1 = post(MODEL, msgs, 4000, len(b64))
    qs = numbered(t_ask)
    if not qs:
        return dict(error="no questions")

    ans = as_json(post(JUDGE, [{"role": "user", "content": MATCH_Q % (
        "\n".join("%d. %s" % (i, q) for i, q in enumerate(qs, 1)),
        symptom_table(c))}], 1500)[0]) or {}
    qa = ["%d. %s  ->  %s" % (i, q, three_valued(ans.get(str(i), "unknown")))
          for i, q in enumerate(qs, 1)]

    if ORACLE:
        inv = c["investigations"]
        dec = [k for k, v in inv.items() if v.get("decisive")]
        lines = ["%d. %s: %s" % (i, k, inv[k]["v"]) for i, k in enumerate(dec, 1)]
        msgs += [{"role": "assistant", "content": t_ask},
                 {"role": "user", "content": T3_ORACLE % ("\n".join(qa), "\n".join(lines))}]
        t_dx, u3 = post(MODEL, msgs, 1500)
        m = re.search(r"DIAGNOS\w*\s*:\s*(.+)", t_dx)
        return dict(questions=qs, answers=ans, n_yes_answers=sum(
            1 for v in ans.values() if str(v).lower() == "yes"),
            orders=[], served=dec, results=lines, dx_raw=t_dx, order_style="oracle",
            novideo=NOVIDEO, signtext=SIGNTEXT, role=ROLE, shuffled=SHUFFLE, shuffle_seed=SHUFFLE_SEED if SHUFFLE else None, chief=CHIEF, order_raw="", rationale=[],
            leading=None,
            dx=(m.group(1).strip() if m else (t_dx.strip().splitlines() or [""])[0]),
            decisive_served=dec, n_decisive=len(dec),
            usage=dict(ask=u1, order={}, dx=u3), n_frames=len(fs), duration_s=round(dur, 1))

    prompt2 = (T2_HYPO if ORDERSTYLE == "hypothesis" else T2) % "\n".join(qa)
    msgs += [{"role": "assistant", "content": t_ask},
             {"role": "user", "content": prompt2}]
    t_ord, u2 = post(MODEL, msgs, 4000)
    raw_orders = numbered(t_ord)
    rationale = [t.split("---", 1)[1].strip() if "---" in t else None for t in raw_orders]
    tests = [t.split("---", 1)[0].strip() for t in raw_orders]
    m_lead = re.search(r"LEADING:\s*(.+)", t_ord)
    leading = m_lead.group(1).strip() if m_lead else None
    if not tests:
        return dict(error="no orders", questions=qs, answers=ans)

    inv = c["investigations"]
    menu = "\n".join("- %s%s" % (k, " [NAMED-ONLY]" if v.get("explicit_only") else "")
                     for k, v in inv.items())
    cov = as_json(post(JUDGE, [{"role": "user", "content": MATCH_I % (
        "\n".join("%d. %s" % (i, t) for i, t in enumerate(tests, 1)), menu)}], 2500)[0]) or {}

    # one block per order, not one line per matched entry - a bundled order can cover a dozen
    # chart entries and repeating its text before each result buries the results in the prompt
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

    msgs += [{"role": "assistant", "content": t_ord},
             {"role": "user", "content": T3 % "\n".join(lines)}]
    t_dx, u3 = post(MODEL, msgs, 1500)
    # mimo-v2.5 with reasoning on misspells the header (DIAGNOSON, DIAGNOPS, DIAGNOS)
    m = re.search(r"DIAGNOS\w*\s*:\s*(.+)", t_dx)
    return dict(questions=qs, answers=ans, n_yes_answers=sum(
        1 for v in ans.values() if str(v).lower() == "yes"),
        orders=tests, served=served, results=lines, dx_raw=t_dx, order_style=ORDERSTYLE, novideo=NOVIDEO, signtext=SIGNTEXT, role=ROLE, shuffled=SHUFFLE, chief=CHIEF,
        leading=leading, order_raw=t_ord, rationale=rationale,
        dx=(m.group(1).strip() if m else (t_dx.strip().splitlines() or [""])[0]),
        decisive_served=[k for k in served if inv[k].get("decisive")],
        n_decisive=sum(1 for v in inv.values() if v.get("decisive")),
        usage=dict(ask=u1, order=u2, dx=u3), n_frames=len(fs), duration_s=round(dur, 1))


def work():
    while True:
        with lock:
            if not todo:
                return
            c = todo.pop()
        out = "%s/results/%s/%s/%s.json" % (B, OUTROOT, c["line"], c["video"].rsplit(".", 1)[0])
        if os.path.exists(out):
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        t0 = time.time()
        try:
            r = run(c)
        except Exception as e:                                     # noqa: BLE001
            r = dict(error="%s: %s" % (type(e).__name__, e))
        r.update(video=c["video"], line=c["line"], space=SPACE, model=MODEL, reasoning=REASONING,
                 elapsed_s=round(time.time() - t0, 1))
        json.dump(r, open(out, "w"), indent=1, ensure_ascii=False)
        print("%-46s %2dq %2do dec %d/%d | %s" % (
            c["video"][:46], len(r.get("questions") or []), len(r.get("orders") or []),
            len(r.get("decisive_served") or []), r.get("n_decisive", 0),
            (r.get("dx") or r.get("error", ""))[:60]), flush=True)


t0 = time.time()
ts = [threading.Thread(target=work) for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6)]
[t.start() for t in ts]
[t.join() for t in ts]
print("done in %.1f min" % ((time.time() - t0) / 60))
