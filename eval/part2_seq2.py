"""Part 2 as agenuinely sequential consultation: one action per turn, adaptive, self-terminating.

The batch protocol of part2_full.py asks every question at once and orders every test at once.
This file keeps the same patient, the same chart, the same matchers and the same grading, and
changes only the interaction: at each turn the doctor issues exactly ONE of

    ASK: + numbered yes/no questions   -> the patient answers, from the case's symptom table
    ORDER: + numbered investigations   -> the chart answers, from the case's investigation menu
    DIAGNOSIS: <final>                 -> the consultation ends

and sees the results of that round before deciding what the next round should be. A round may
carry as many questions, or as many investigations, as the doctor wants - what the batch protocol
forbids is not the batching but the second round: there, the history is over before the first
result is read. It stops when it wants to, within MAXROUND rounds.

Every rule of the batch protocol is unchanged: the patient answers yes, no or unknown from the record, an
investigation not on the menu returns "not performed / not available", a therapeutic trial is
returned only when named specifically. The judge is used ONLY for matching, never to write a value.

usage: part2_seq2.py [NTHREADS]
env:   ORKEY, MODEL, JUDGE, PROVIDER, JPROVIDER, REASONING, KFRAMES, MAXROUND, OUTROOT
"""
import base64
import glob
import json
import os
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
REASONING = json.loads(os.environ.get("REASONING", '{"enabled": true}'))
MAXTOK = int(os.environ.get("MAXTOK", "-1"))
TIMEOUT = int(os.environ.get("TIMEOUT", "300"))
K = int(os.environ.get("KFRAMES", "32"))
MAXROUND = int(os.environ.get("MAXROUND", "10"))
ROLE = os.environ.get("ROLE", "doctor")
NOVIDEO = os.environ.get("NOVIDEO", "0") == "1"
OUTROOT = os.environ.get("OUTROOT", "part2_seq2_luna_vid")
FF = os.environ.get("FFMPEG", "ffmpeg")
_OPENING = {"neurologist": "You are a neurologist seeing a new patient.",
            "doctor": "You are a doctor seeing a new patient."}[ROLE]


def _prov(model):
    return JPROVIDER if model == JUDGE and JUDGE != MODEL else PROVIDER


T1 = """%s Above are %d frames sampled across a
%s-second video of the consultation, in order.

You will now work through this patient in rounds. In each round you may do exactly ONE of
these three things, and you will see its result before the next round:

  ASK:
  1. <a question the patient can answer with yes or no>
  2. <another one>
  ... as many or as few as you want in this round

  ORDER:
  1. <an investigation - a bedside examination manoeuvre, a blood test, imaging,
     electrophysiology, an invasive procedure, or a therapeutic trial>
  2. <another one>
  ... as many or as few as you want in this round

  DIAGNOSIS: <your final diagnosis, on one line>

The rules:
  - the patient answers only yes, no, or unknown - unknown when the record does not establish the
    answer - and anything you do not ask you do not learn
  - name the investigation you actually want; a vague request returns nothing, and a therapeutic
    trial is returned only if you name that specific trial
  - you may ask again after seeing results, and order again after asking again, in whatever
    order you like - let each round decide what the next one should be
  - you have at most %d rounds. Stop as soon as another round would not change what you think is
    wrong, and give DIAGNOSIS then - you do not have to use the rounds you do not need
  - in DIAGNOSIS, name the disease entity and its cause, as specifically as the evidence allows

Begin your reply with ASK:, ORDER: or DIAGNOSIS: and write nothing else."""

T1_NOVID = """You are a doctor. A new patient has been referred to you and you have not yet seen
or examined them. You know nothing about them at all.

You will now work through this patient in rounds. In each round you may do exactly ONE of
these three things, and you will see its result before the next round:

  ASK:
  1. <a question the patient can answer with yes or no>
  2. <another one>
  ... as many or as few as you want in this round

  ORDER:
  1. <an investigation - a bedside examination manoeuvre, a blood test, imaging,
     electrophysiology, an invasive procedure, or a therapeutic trial>
  2. <another one>
  ... as many or as few as you want in this round

  DIAGNOSIS: <your final diagnosis, on one line>

The rules:
  - the patient answers only yes, no, or unknown - unknown when the record does not establish the
    answer - and anything you do not ask you do not learn
  - name the investigation you actually want; a vague request returns nothing, and a therapeutic
    trial is returned only if you name that specific trial
  - you may ask again after seeing results, and order again after asking again, in whatever
    order you like - let each round decide what the next one should be
  - you have at most %d rounds. Stop as soon as another round would not change what you think is
    wrong, and give DIAGNOSIS then - you do not have to use the rounds you do not need
  - in DIAGNOSIS, name the disease entity and its cause, as specifically as the evidence allows

Begin your reply with ASK:, ORDER: or DIAGNOSIS: and write nothing else."""

NUDGE = """That was not one of the three allowed moves. The first line of your reply must be
exactly "ASK:", exactly "ORDER:", or "DIAGNOSIS: <diagnosis>". Write the word, then the items."""

LAST = """You have used all %d rounds. Give your diagnosis now. State the single diagnosis you
believe is correct - the disease entity and its cause, as specifically as the evidence allows.

Begin with "DIAGNOSIS:" followed by the single answer on one line."""

# the two matchers of part2_full.py, unchanged, applied to one item at a time
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


def framesof(p, k, tmp):
    d = duration(p)
    subprocess.run([FF, "-y", "-i", p, "-vf", "fps=%.5f,scale=512:-1" % (k / max(d, 0.1)),
                    "-frames:v", str(k), tmp + "/f_%03d.jpg"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sorted(glob.glob(tmp + "/*.jpg")), d


def post(model, messages, mx, imgs=0):
    payload = {"model": model, "temperature": 0, "messages": messages,
               "reasoning": REASONING, "usage": {"include": True}}
    # empty or "auto" = let OpenRouter route it: minimax's video endpoints are not all on one provider
    if _prov(model) not in ("", "auto"):
        payload["provider"] = {"order": [_prov(model)], "allow_fallbacks": False,
                               "sort": "price"}
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


HEAD = re.compile(r"^\s*\**\s*(ASK|ORDER|DIAGNOS\w*)\s*\**\s*:?\s*(.*)$", re.I)
NUM = re.compile(r"^\s*\d+[.)]\s*(.+)")


def parse_round(t):
    """One move per round: a block of questions, a block of orders, or the final diagnosis."""
    m = re.search(r"DIAGNOS\w*\s*:\s*(.+)", t, re.I)
    if m:
        return "DIAGNOSIS", [m.group(1).strip().strip("*").strip()]
    kind, items = None, []
    for ln in t.splitlines():
        h = HEAD.match(ln)
        if h:
            k = "ASK" if h.group(1).upper() == "ASK" else "ORDER"
            if kind is None:
                kind = k
                rest = h.group(2).strip().strip("*").strip()
                if 3 < len(rest) < 600:
                    items.append(rest)
            elif k != kind:
                break                      # a second block of the other kind: not this round
            continue
        if kind:
            n = NUM.match(ln)
            if n:
                v = n.group(1).strip().strip("*").strip()
                if 3 < len(v) < 600:
                    items.append(v)
    return (kind, items) if kind and items else (None, None)


def ask_patient(qs, c):
    a = as_json(post(JUDGE, [{"role": "user", "content": MATCH_Q % (
        "\n".join("%d. %s" % (i, q) for i, q in enumerate(qs, 1)),
        symptom_table(c))}], 1500)[0]) or {}
    return [three_valued(a.get(str(i), "unknown")) for i in range(1, len(qs) + 1)]


def run_chart(tests, inv, menu):
    cov = as_json(post(JUDGE, [{"role": "user", "content": MATCH_I % (
        "\n".join("%d. %s" % (i, x) for i, x in enumerate(tests, 1)), menu)}], 2500)[0]) or {}
    return [[k for k in (cov.get(str(i)) or []) if k in inv] for i in range(1, len(tests) + 1)]


cases = json.load(open(B + "/data/cases.json"))
todo = list(cases)
LIMIT = int(os.environ.get("LIMIT", "0"))
if LIMIT:
    todo = todo[:LIMIT]
if os.environ.get("REVERSE", "0") == "1":
    todo.reverse()
print("MODEL=%s MAXROUND=%d -> %d cases -> results/%s" % (MODEL, MAXROUND, len(todo), OUTROOT),
      flush=True)
lock = threading.Lock()


def run(c):
    tmp = tempfile.mkdtemp(prefix="p2s_")
    try:
        fs, dur = framesof("%s/dataset/videos/%s/%s" % (B, c["line"], c["video"]), K, tmp)
        b64 = [base64.b64encode(open(f, "rb").read()).decode() for f in fs]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if NOVIDEO:
        b64, fs = [], []
        content1 = [{"type": "text", "text": T1_NOVID % MAXROUND}]
    else:
        content1 = ([{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b}}
                     for b in b64]
                    + [{"type": "text",
                        "text": T1 % (_OPENING, len(fs), "%.0f" % dur, MAXROUND)}])
    msgs = [{"role": "user", "content": content1}]

    inv = c["investigations"]
    menu = "\n".join("- %s%s" % (k, " [NAMED-ONLY]" if v.get("explicit_only") else "")
                     for k, v in inv.items())

    qs, answers, orders, served, trace = [], {}, [], [], []
    cost, dx_raw, bad = 0.0, "", 0
    for rnd in range(1, MAXROUND + 1):
        t, u = post(MODEL, msgs, 4000, len(b64) if rnd == 1 else 0)
        cost += (u or {}).get("cost", 0) or 0
        kind, items = parse_round(t)
        if kind is None:
            bad += 1
            if bad > 2:
                break
            msgs += [{"role": "assistant", "content": t or "(empty)"},
                     {"role": "user", "content": NUDGE}]
            trace.append(dict(round=rnd, kind="invalid", text=(t or "")[:200]))
            continue
        if kind == "DIAGNOSIS":
            dx_raw = t
            trace.append(dict(round=rnd, kind="diagnosis", text=items[0]))
            break
        if kind == "ASK":
            a = ask_patient(items, c)
            for q, v in zip(items, a):
                qs.append(q)
                answers[str(len(qs))] = v
            qa = ["%d. %s  ->  %s" % (i, q, v) for i, (q, v) in enumerate(zip(items, a), 1)]
            reply = "The patient answered:\n\n" + "\n".join(qa)
            trace.append(dict(round=rnd, kind="ask", items=items, result=a))
        else:
            got = run_chart(items, inv, menu)
            lines = []
            for i, (x, g) in enumerate(zip(items, got), 1):
                orders.append(x)
                lines.append("%d. %s" % (i, x))
                if not g:
                    lines.append("     not performed / not available")
                    continue
                for k in g:
                    if k not in served:
                        served.append(k)
                    lines.append("     %s: %s" % (k, inv[k]["v"]))
            reply = ("The results are:\n\n" + "\n".join(lines)
                     + "\n\nAnything reported as not available was not done and has no result.")
            trace.append(dict(round=rnd, kind="order", items=items, result=got))
        msgs += [{"role": "assistant", "content": t.strip()},
                 {"role": "user", "content": reply + "\n\nNext round."}]
    if not dx_raw:
        # the rounds ran out, or the model kept replying in a shape the parser cannot read:
        # either way ask for the diagnosis rather than dropping the case
        msgs += [{"role": "user", "content": LAST % MAXROUND}]
        dx_raw, u = post(MODEL, msgs, 1500)
        cost += (u or {}).get("cost", 0) or 0
        trace.append(dict(round=MAXROUND + 1, kind="forced_diagnosis", text=dx_raw[:200]))

    m = re.search(r"DIAGNOS\w*\s*:\s*(.+)", dx_raw)
    dx = m.group(1).strip().strip("*").strip() if m else (dx_raw.strip().splitlines() or [""])[0]
    results = ["R%d %s %s -> %s" % (s["round"], s["kind"].upper(),
                                    "; ".join(s.get("items") or [s.get("text", "")]),
                                    s.get("result", "")) for s in trace]
    return dict(questions=qs, answers=answers,
                n_yes_answers=sum(1 for v in answers.values() if v == "yes"),
                orders=orders, served=served, results=results, trace=trace,
                dx=dx, dx_raw=dx_raw, protocol="multiround", maxround=MAXROUND,
                n_rounds=len([s for s in trace if s["kind"] in ("ask", "order")]),
                stopped_early=bool(trace) and trace[-1]["kind"] == "diagnosis",
                invalid_replies=bad, novideo=NOVIDEO, role=ROLE,
                decisive_served=sorted({k for k in served if inv[k].get("decisive")}),
                n_decisive=sum(1 for v in inv.values() if v.get("decisive")),
                cost_usd=round(cost, 4), n_frames=len(fs), duration_s=round(dur, 1))


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
        r.update(video=c["video"], line=c["line"], model=MODEL, reasoning=REASONING,
                 elapsed_s=round(time.time() - t0, 1))
        json.dump(r, open(out, "w"), indent=1, ensure_ascii=False)
        print("%-40s %2dR %2dq %2do dec %d/%d | %s" % (
            c["video"][:40], r.get("n_rounds", 0), len(r.get("questions") or []),
            len(r.get("orders") or []),
            len(r.get("decisive_served") or []), r.get("n_decisive", 0),
            (r.get("dx") or r.get("error", ""))[:52]), flush=True)


t0 = time.time()
ts = [threading.Thread(target=work) for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6)]
[t.start() for t in ts]
[t.join() for t in ts]
print("done in %.1f min" % ((time.time() - t0) / 60))
