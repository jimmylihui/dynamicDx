"""Decidability split: the neurologist's video-only call (22 'cannot tell' vs 49) as an
independent, diagnosis-blind label; report model Part-1 recognition and Part-2 accuracy on each
subset; audit the reference phenomenology for non-visual content."""
import os
import glob, json, os, random, re, threading, urllib.request, time
ACCURATE = {"accurate", "exact"}   # grade names: current grader / earlier result files

B = os.environ.get("DDX_ROOT", ".")
C = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}
vids = sorted(C)
clin = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/clin_step1.json"))
UND = {v for v, r in clin.items() if re.search(r"不确定|不明确|^正常|^无|备注:无", r["text"])}
DEC = [v for v in vids if v not in UND]; UNDL = [v for v in vids if v in UND]
print("undecidable (clinician, video only): %d   decidable: %d" % (len(UNDL), len(DEC)))
print("by line, undecidable:", {l: sum(1 for v in UNDL if C[v]["line"] == l) for l in sorted({C[v]["line"] for v in vids})})

P1 = [("GPT-5.6-luna", "part1_oldp_luna_judge"), ("Gemma-4-31B", "part1_oldp_gemma_judge"),
      ("MiMo-v2.5", "part1_oldp_mimo_judge"), ("MiniMax-M3", "part1_oldp_minimax_judge"),
      ("Qwen3.7-plus", "part1_oldp_qwen_judge")]
P2 = [("GPT-5.6-luna", "part2_lunathink_vid_doctor"), ("Gemma-4-31B", "part2_gemmathink_vid_doctor"),
      ("MiMo-v2.5", "part2_mimothink_vid_doctor"), ("MiniMax-M3", "part2_minimaxthink_vid_doctor"),
      ("Qwen3.8-flash", "part2_qwen38_vid_doctor")]
BL = {"GPT-5.6-luna": "part2_lunathink_novid_doctor", "Qwen3.8-flash": "part2_qwen38_novid_doctor"}
K = 32


def p1(root):
    out = {}
    for f in glob.glob("%s/results/%s/*__k%d.json" % (B, root, K)):
        d = json.load(open(f)); s = (d.get("verdict") or {}).get("sign")
        out[d["video"]] = s
    return out


def rate(g, sub, ok):
    return 100.0 * sum(1 for v in sub if g.get(v) in ok) / len(sub)


def boot_diff(ga, gb, A, Bs, ok, n=10000):
    """difference of rates between two disjoint subsets, percentile bootstrap"""
    r = random.Random(0); xa = [1.0 if ga.get(v) in ok else 0.0 for v in A]; xb = [1.0 if gb.get(v) in ok else 0.0 for v in Bs]
    d = []
    for _ in range(n):
        sa = [xa[r.randrange(len(xa))] for _ in xa]; sb = [xb[r.randrange(len(xb))] for _ in xb]
        d.append(100.0 * (sum(sa) / len(sa) - sum(sb) / len(sb)))
    d.sort(); return d[int(.025 * n)], d[int(.975 * n)]


print("\nPART 1 sign recognition at k=%d (%% of clips), clinician-decidable vs undecidable" % K)
print("%-14s %20s %20s %10s %26s" % ("system", "decidable(49)", "undecidable(22)", "gap", "95% CI of gap"))
for nm, root in P1:
    g = p1(root)
    for lab, ok in (("correct", {"correct"}), ("correct+partial", {"correct", "partial"})):
        a, b = rate(g, DEC, ok), rate(g, UNDL, ok); lo, hi = boot_diff(g, g, DEC, UNDL, ok)
        print("%-14s %-16s %5.1f %14.1f %14.1f   [%+.1f, %+.1f]" % (nm if lab == "correct" else "", lab, a, b, a - b, lo, hi))
cg = {v: r["grade"] for v, r in clin.items()}
print("%-14s %-16s %5.1f %14.1f" % ("Clinician", "correct", rate(cg, DEC, {"correct"}), rate(cg, UNDL, {"correct"})))
print("%-14s %-16s %5.1f %14.1f" % ("", "correct+partial", rate(cg, DEC, {"correct", "partial"}), rate(cg, UNDL, {"correct", "partial"})))

print("\nPART 2 diagnosis accuracy, video condition (%%)")
print("%-14s %14s %16s %8s %22s" % ("system", "decidable(49)", "undecidable(22)", "gap", "95% CI of gap"))
for nm, root in P2:
    g = {v: d.get("grade") for v, d in json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/fulljudge_%s.json" % root)).items()}
    a, b = rate(g, DEC, ACCURATE), rate(g, UNDL, ACCURATE); lo, hi = boot_diff(g, g, DEC, UNDL, ACCURATE)
    line = "%-14s %14.1f %16.1f %+8.1f   [%+.1f, %+.1f]" % (nm, a, b, a - b, lo, hi)
    if nm in BL:
        gb = {v: d.get("grade") for v, d in json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/fulljudge_%s.json" % BL[nm])).items()}
        line += "   video-blind: decidable %+.1f, undecidable %+.1f" % (a - rate(gb, DEC, ACCURATE), b - rate(gb, UNDL, ACCURATE))
    print(line)
H = B + "/human_study/"; cl = {}
for n in ("2", "3"):
    for d in json.load(open(H + "doctor_graded%s.json" % n)).values(): cl[d["video"]] = d.get("grade")
print("%-14s %14.1f %16.1f" % ("Clinician", rate(cl, DEC, ACCURATE), rate(cl, UNDL, ACCURATE)))

# ---- reference phenomenology audit -------------------------------------------------------
ORKEY = os.environ["ORKEY"]
PROMPT = """Below is a one-line description of the sign visible in a short silent clinical video. It is
supposed to be written ONLY from what a viewer can see in the video, with no history, no test
results and no diagnosis.

Description: "%s"

Split it into its atomic claims and classify each as
  V = observable in a silent video of the patient (movement, posture, eye position, face, gait)
  N = NOT observable from video alone (history, time course, symptoms the patient reports, test
      results, anatomical localisation, a named disease or syndrome, response to a manoeuvre that
      is not shown)
Reply with ONLY JSON: {"claims":[{"text":"...","class":"V"|"N","why":"<=8 words"}],
"names_disease_or_syndrome":true|false}"""
res = {}; lock = threading.Lock(); todo = list(vids)


def ask(p):
    body = json.dumps({"model": "openai/gpt-5.6-luna", "temperature": 0, "max_tokens": 6000,
                       "messages": [{"role": "user", "content": p}],
                       "provider": {"order": ["OpenAI"], "allow_fallbacks": False}}).encode()
    for _ in range(4):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY, "Content-Type": "application/json"}), timeout=120).read())
            m = re.search(r"\{.*\}", r["choices"][0]["message"]["content"] or "", re.S)
            if m: return json.loads(m.group(0))
        except Exception: time.sleep(3)
    return None


def work():
    while True:
        with lock:
            if not todo: return
            v = todo.pop()
        a = ask(PROMPT % C[v]["part1_video_only"]["visible_sign"])
        with lock: res[v] = a


ts = [threading.Thread(target=work) for _ in range(8)]; [t.start() for t in ts]; [t.join() for t in ts]
json.dump(res, open(os.environ.get("DDX_WORK", "/tmp") + "/ref_audit.json", "w"), indent=1, ensure_ascii=False)
nc = sum(len(a["claims"]) for a in res.values() if a); nn = sum(1 for a in res.values() if a for c in a["claims"] if c["class"] == "N")
flag = [v for v, a in res.items() if a and any(c["class"] == "N" for c in a["claims"])]
named = [v for v, a in res.items() if a and a.get("names_disease_or_syndrome")]
print("\nREFERENCE PHENOMENOLOGY AUDIT (%d descriptions, %d atomic claims)" % (len([a for a in res.values() if a]), nc))
print("claims not observable from silent video: %d (%.1f%%) in %d descriptions; names a disease/syndrome: %d" % (nn, 100.0 * nn / nc, len(flag), len(named)))
for v in sorted(flag):
    ns = [c for c in res[v]["claims"] if c["class"] == "N"]
    print("  %-46s | %s" % (v[:46], "; ".join("%s (%s)" % (c["text"][:60], c["why"]) for c in ns)))
json.dump(dict(undecidable=sorted(UNDL), decidable=DEC), open(os.environ.get("DDX_WORK", "/tmp") + "/decidability_split.json", "w"), indent=1)
