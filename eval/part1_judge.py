"""Stage 1 grading as in the paper (Appendix H, Part 1): sign and differential, and the uncapped rank probe.

The case-specific lists: accepted as COVERAGE = part1_video_only.accept_as_coverage,
related but NOT accepted = part1_video_only.related_but_not_covered (data/cases.json).
Aetiological coverage = best == "correct"; the rank probe gives coverage over the full list.

usage: part1_judge.py TAG=RUNDIR [TAG=RUNDIR ...]    e.g. luna=part1_luna
env:   ORKEY, JUDGE (default deepseek/deepseek-v4.1-flash), JPROVIDER (default unset: OpenRouter routes), CASES, OUT, PAR
Writes one file per answer under results/part1_judge/<TAG>__<clip>__k<K>.json with the verdict and the rank.
"""
import glob, json, os, re, sys, threading, time, urllib.request
B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORKEY = os.environ["ORKEY"]; JUDGE = os.environ.get("JUDGE", "deepseek/deepseek-v4.1-flash"); JPROV = os.environ.get("JPROVIDER", "")
CASES = {c["video"]: c for c in json.load(open(os.environ.get("CASES", B + "/data/cases.json")))}
OUT = os.environ.get("OUT", B + "/results/part1_judge"); PAR = int(os.environ.get("PAR", "12"))
GRADE = """You are grading a vision model that was shown a short clinical video of one
patient and asked, with NO history and NO test results, to describe what it saw
and propose possible diagnoses.

Evaluate two separate outcomes:
(1) recognition of the visible phenomenology;
(2) coverage of a diagnostic hypothesis compatible with the reference case.

Diagnostic coverage does NOT require exact identification of the confirmed
disease. A clinically appropriate syndrome or broader aetiological category
may qualify under the case-specific acceptance criteria below.

GROUND TRUTH
  confirmed diagnosis : %s
  reference visible phenomenology : %s
  additional hypotheses accepted as COVERAGE, including qualifying syndromes
  and broader aetiological categories : %s
  related but insufficient hypotheses, NOT accepted as coverage :
  %s

THE MODEL'S ANSWER (free prose)
%s

Read the whole answer. Grade SIGN and DIAGNOSIS independently.
Correct sign recognition does not by itself establish diagnostic coverage,
and an incorrect sign description does not rule out diagnostic coverage.

SIGN - did it identify the visible abnormality?
  correct : identifies the reference phenomenology or an equivalent physical
            description anywhere in the answer; clinical synonyms count.
  partial : describes a relevant abnormality in the correct body region,
            but the description is incomplete or too vague to establish
            the reference phenomenology.
  wrong   : identifies an incompatible phenomenology or the wrong body
            region, or does not describe a relevant visible abnormality.

DIAGNOSIS - does a proposed hypothesis cover the reference case?
  correct : identifies the confirmed disease or an equivalent diagnosis,
            OR identifies a syndrome or broader aetiological category
            included in the case-specific COVERAGE list.
            Equivalent clinical terminology is accepted.
            Exact disease identification and equal specificity to the
            confirmed diagnosis are NOT required for accepted hypotheses.
  partial : proposes a clinically related hypothesis that does not satisfy
            the COVERAGE criteria, including an entry in the
            related-but-not-covered list.
  wrong   : proposes an incompatible or unrelated hypothesis, or does not
            propose a diagnostic hypothesis.

Apply these rules:
- Do not reject an accepted hypothesis merely because it is broader than
  the confirmed disease.
- Do not automatically accept every broad syndrome or disease category.
  Broad hypotheses must match the case-specific COVERAGE list or an
  equivalent clinical expression.
- Merely repeating the visible sign does not establish coverage unless
  that expression also names an explicitly accepted diagnostic syndrome.
- Count hypotheses the model proposes as possibilities, even if they are
  not its leading diagnosis.
- Do not count a diagnosis mentioned only to deny or explicitly rule it out.
- Do not infer a diagnostic hypothesis that the model did not express.

Assign dx1 to the explicitly designated primary diagnosis, if present;
otherwise use the first proposed diagnosis. Assign dx2 and dx3 to the next
two distinct proposed diagnoses in presentation order.
Use "wrong" for missing slots.

Assign best using ALL distinct proposed diagnoses in the complete answer,
including diagnoses beyond dx3:
  correct : at least one hypothesis is graded correct.
  partial : none is correct, but at least one is partial.
  wrong   : all are wrong, or no diagnostic hypothesis is proposed.

The binary aetiological-coverage outcome is 1 if best is "correct",
and 0 otherwise. Partial hypotheses do not receive coverage credit.

Reply with ONLY this JSON:
{"sign":"correct|partial|wrong",
 "dx1":"correct|partial|wrong",
 "dx2":"correct|partial|wrong",
 "dx3":"correct|partial|wrong",
 "best":"correct|partial|wrong",
 "reason":"<= 12 words"}"""
RANK = """A model was shown frames from a video of one patient and asked to describe
what it saw and propose possible diagnoses, with no history or test results.

TRUE DIAGNOSIS: %s
Additional hypotheses accepted as COVERAGE, including qualifying
syndromes and broader aetiological categories: %s
Related but insufficient hypotheses, NOT accepted as coverage:
%s

THE MODEL'S ANSWER:
%s

Read the whole answer and list, in order of first appearance, every
distinct diagnosis proposed as a possibility. Merge synonymous entries
and exclude diagnoses mentioned only to rule them out.

Return the rank of the first hypothesis that covers the reference case:
either the confirmed disease or an explicitly accepted syndrome or
broader aetiological category. Equivalent clinical terminology counts.
Exact disease identification and equal specificity to the confirmed
diagnosis are NOT required. Do not accept other broad hypotheses unless
equivalent to an explicitly accepted hypothesis. Merely repeating the
visible sign does not qualify unless it names an accepted syndrome.

n_listed is the total number of distinct proposed diagnoses.
rank is the 1-based position of the first qualifying hypothesis.
Use rank = 0 if none qualifies. Consider the entire list, not only
the first three entries.

Reply with ONLY {"n_listed": <int>, "rank": <int>}"""
def ask(p):
    body = json.dumps({"model": JUDGE, "temperature": 0, "max_tokens": 1000, "messages": [{"role": "user", "content": p}],
                       **({"provider": {"order": [JPROV], "allow_fallbacks": False}} if JPROV else {})}).encode()
    for a in range(5):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY, "Content-Type": "application/json"}), timeout=180).read())
            m = re.search(r"\{.*\}", r["choices"][0]["message"]["content"] or "", re.S)
            if m: return json.loads(m.group(0))
        except Exception: time.sleep(3 * (a + 1))
    return None
jobs = []
for spec in sys.argv[1:]:
    tag, run = spec.split("=")
    for f in sorted(glob.glob("%s/results/%s/*/*__k*.json" % (B, run))):
        jobs.append((tag, f))
os.makedirs(OUT, exist_ok=True); lock = threading.Lock(); done = [0]
def work():
    while True:
        with lock:
            if not jobs: return
            tag, f = jobs.pop()
        d = json.load(open(f)); v = d.get("video"); c = CASES.get(v)
        out = "%s/%s__%s__k%d.json" % (OUT, tag, v[:-4], d["k"])
        if not c or os.path.exists(out): continue
        p1 = c["part1_video_only"]; ans = d.get("raw") or ""
        rec = dict(tag=tag, video=v, k=d["k"], subject=d.get("model"), judge=JUDGE, answer_error=d.get("error"))
        if ans.strip():
            rec["verdict"] = ask(GRADE % (c["true_diagnosis"], p1["visible_sign"], p1["accept_as_coverage"], p1["related_but_not_covered"], ans))
            rec["rank"] = ask(RANK % (c["true_diagnosis"], p1["accept_as_coverage"], p1["related_but_not_covered"], ans))
        json.dump(rec, open(out, "w"), ensure_ascii=False)
        with lock:
            done[0] += 1
            if done[0] % 200 == 0: print(done[0], flush=True)
ts = [threading.Thread(target=work) for _ in range(PAR)]; [t.start() for t in ts]; [t.join() for t in ts]
print("DONE", flush=True)
