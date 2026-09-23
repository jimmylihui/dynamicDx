"""Encode free text into HPO concepts by asking a model to normalise it first.

Direct string matching against HPO fails on plain clinical English: "unsteady, wide-based walking"
shares no surface form with "Gait ataxia", so 51 of our 71 ground-truth signs encoded to nothing.
Normalising first fixes that - the model rewrites the description as a short list of standard
phenomenology terms, and those short canonical phrases do match HPO labels and synonyms.

The model is not asked to diagnose, and it is not shown the diagnosis. It is a vocabulary
translator, which is a much weaker and more checkable role than judging.

usage: hpo_normalize.py gt            encode the 71 ground-truth visible_sign fields
       hpo_normalize.py answers ROOT  encode one model run's prose answers
"""
import glob
import json
import os
import re
import sys
import threading
import time
import urllib.request

B = os.environ.get("DDX_ROOT", ".")
ORKEY = os.environ["ORKEY"]
MODEL = os.environ.get("NORM_MODEL", "openai/gpt-5.6-luna")
PROV = os.environ.get("NORM_PROVIDER", "OpenAI")
vocab = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/hpo_vocab.json"))

# HPO files laterality and distribution as clinical MODIFIERS, not as separate phenotypes, which
# is why "hemichorea" has no entry - the intended encoding is Chorea + Unilateral. Loading the
# modifier subontology recovers a dimension the earlier pass threw away, and half the chorea line
# in this dataset is unilateral.
MODIFIERS = {
    "HP:0012832": "Bilateral", "HP:0012833": "Unilateral", "HP:0012834": "Right",
    "HP:0012835": "Left", "HP:0012837": "Generalized", "HP:0012839": "Distal",
    "HP:0012840": "Proximal", "HP:0025287": "Axial", "HP:0030650": "Focal",
    "HP:0030651": "Multifocal", "HP:4000152": "Alternating laterality",
    "HP:0025275": "Lateral",
}
for _h, _l in MODIFIERS.items():
    vocab.setdefault(_h, dict(label=_l, terms=[_l.lower()], parents=["HP:0012823"]))

# Three ocular-motility signs the whole of HPO has no term for - searching the full 20,464-node
# release returns Skewfoot and Torsion dystonia and nothing usable. Declared here as a local
# extension with their nearest HPO parent, so they are visible as project-added rather than
# silently mixed into the ontology.
# The eye-movement terms HPO lacks come from the Barany Society's ICVD consensus - the ocular
# equivalent of the MDS phenomenology statements - rather than from anything invented here.
# Harvested from Eggers 2019 (PMC9249296, CC BY).
# Terms that neither HPO nor the nystagmus consensus carries. Skew deviation and ocular torsion
# belong to the ocular tilt reaction, which is a different ICVD document from the one harvested;
# rather than leave them unencodable they are declared here with their nearest HPO parent.
# Terms added to the ontology change the ENCODING, so they change every downstream number and
# have to be versioned like any other parameter. LOCALSET=v1 is the set as of round 12, v2 adds
# the two terms introduced in round 14.
LOCALSET = os.environ.get("LOCALSET", "v2")
_LOCAL_V1 = {
        "LOCAL:0001": ("Skew deviation", ["skew deviation", "ocular skew deviation",
                                          "vertical ocular misalignment"], "HP:0000496"),
        "LOCAL:0002": ("Ocular torsion", ["ocular torsion", "cyclotorsion"], "HP:0000496"),
}
_LOCAL_V2 = dict(_LOCAL_V1, **{
        # the MSA case is defined by a sustained upward gaze deviation, and with no term for it
        # the encoder kept only the accompanying eyelid closure and queried for blepharospasm
        "LOCAL:0003": ("Oculogyric crisis", ["oculogyric crisis", "oculogyric dystonia",
                                             "sustained upward gaze deviation",
                                             "conjugate upward eye deviation"], "HP:0000496"),
        # scissoring is a gait pattern; calling it spasticity asserts the mechanism, and in the
        # functional case the whole point is that the mechanism is NOT spastic
        "LOCAL:0004": ("Scissoring gait", ["scissoring gait", "scissor gait",
                                           "scissoring of the legs"], "HP:0001288"),
})
for _h, (_l, _t, _p) in (_LOCAL_V1 if LOCALSET == "v1" else _LOCAL_V2).items():
    vocab[_h] = dict(label=_l, terms=_t, parents=[_p])

import os as _os
_icvd = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "icvd_vocab.json")
if _os.path.exists(_icvd):
    for _h, _v in json.load(open(_icvd)).items():
        vocab.setdefault(_h, _v)          # never overwrite the local declarations above
    print("loaded %d Barany ICVD ocular-motor terms" % len(json.load(open(_icvd))))

# The vocabulary builder dropped surface forms shorter than 5 characters and the matcher then
# required 6, which silently excluded "chorea", "tremor" and "ptosis" - three of the terms this
# whole exercise is about. Length is the wrong filter; ambiguity is the thing to guard against,
# so only a short stop list is applied.
# Anatomical words are not pathology and must never be looked up in the phenotype table. Letting
# them through is how "Arm" became "Upper limb muscle weakness" and "Leg" became "Exercise-induced
# leg cramps", which then went on to poison the literature queries built from those concepts.
BODY = {"arm", "arms", "leg", "legs", "hand", "hands", "foot", "feet", "face", "head", "neck",
        "trunk", "eye", "eyes", "eyelid", "eyelids", "tongue", "jaw", "limb", "limbs",
        "upper limb", "upper limbs", "lower limb", "lower limbs", "shoulder", "hip", "knee",
        "finger", "fingers", "toe", "toes", "mouth", "lip", "lips", "torso", "body"}
AMBIG = {"tic", "gait", "sign", "test", "pain", "weak"} | BODY
surface = {}
for hp, v in vocab.items():
    for t in v["terms"]:
        if t in AMBIG:
            continue
        surface.setdefault(t, hp)

ASK = """Rewrite the clinical description below as a list of standard neurological
phenomenology terms, the kind used as headings in a movement-disorder textbook.

Rules:
- one term per line, nothing else, no numbering, no explanation
- use the canonical noun form: "Gait ataxia", "Chorea", "Resting tremor", "Ptosis",
  "Nystagmus", "Bradykinesia", "Dystonia", "Myoclonus", "Facial palsy", "Spasticity"
- include the body region as a separate term when the description gives one
- when the description states a side or a distribution, add it on its own line using exactly
  one of: Unilateral, Bilateral, Left, Right, Generalized, Focal, Multifocal, Axial, Proximal,
  Distal, Alternating laterality
- include only what the description actually states; do not infer a diagnosis
- if the description states no abnormality, output the single line NONE

Description:
%s"""


def ask(text):
    body = json.dumps({"model": MODEL, "temperature": 0, "max_tokens": 200,
                       "messages": [{"role": "user", "content": ASK % text}],
                       "provider": {"order": [PROV], "allow_fallbacks": False, "sort": "price"},
                       "reasoning": {"enabled": False}}).encode()
    r = json.loads(urllib.request.urlopen(urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": "Bearer " + ORKEY,
                 "Content-Type": "application/json"}), timeout=180).read().decode())
    return r.get("choices", [{}])[0].get("message", {}).get("content", "") or ""


def norm(s):
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", s.lower()).split())


def to_hpo(reply):
    """Exact match, or a whole-term match inside the line. No longest-substring fallback.

    The fallback used to guarantee a concept for every line by taking the longest key that
    overlapped at all, which reliably produced the least related concept: the longer an ontology
    term is, the more specific and the further from a loose word match. Missing is better than
    wrong here, because a wrong concept goes on to become a wrong literature query.
    """
    hits, unmatched = set(), []
    for line in (reply or "").splitlines():
        t = norm(line.strip(" -*•"))
        if not t or t == "none" or t in AMBIG:
            continue
        if t in surface:
            hits.add(surface[t])
            continue
        # the ontology term must appear whole inside the line, not merely share characters
        found = {surface[k] for k in surface
                 if len(k.split()) >= 2 and re.search(r"\b%s\b" % re.escape(k), t)}
        if found:
            hits |= found
        else:
            unmatched.append(t)
    return hits, unmatched


if sys.argv[1] == "answers":
    root = sys.argv[2]
    files = sorted(glob.glob("%s/results/%s/*/*.json" % (B, root)))
    out, lock = {}, threading.Lock()
    done = [0]
    t0 = time.time()

    def work(q):
        while True:
            with lock:
                if not q:
                    return
                f = q.pop()
            d = json.load(open(f))
            key = "%s__k%d" % (d["video"][:-4], d["k"])
            txt = (d.get("raw") or "")[:20000]
            try:
                rep = ask(txt) if txt.strip() else ""
            except Exception as e:                                # noqa: BLE001
                rep = ""
            hp, un = to_hpo(rep)
            with lock:
                # keep the normaliser's raw output so the matching rules can be changed
                # without paying for the API again
                out[key] = dict(video=d["video"], k=d["k"], reply=rep.strip(),
                                hpo=sorted(hp),
                                labels=sorted(vocab[h]["label"] for h in hp if h in vocab))
                done[0] += 1
                if done[0] % 200 == 0:
                    el = time.time() - t0
                    print("[%4d/%4d] %4.0fs eta %4.0fs"
                          % (done[0], len(files), el,
                             (len(files) - done[0]) * el / done[0]), flush=True)

    ONLY = set(x for x in os.environ.get("ONLY", "").split(",") if x)
    if ONLY:
        prev = os.environ.get("DDX_WORK", "/tmp") + "/ans_hpo_%s.json" % root
        if os.path.exists(prev):
            out.update(json.load(open(prev)))
        files = [f for f in files
                 if os.path.basename(f).rsplit("__", 1)[0] + ".mp4" in ONLY]
        print("ONLY: %d files to renormalise" % len(files))
    q = list(files)
    ts = [threading.Thread(target=work, args=(q,)) for _ in range(8)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    o = os.environ.get("DDX_WORK", "/tmp") + "/ans_hpo_%s.json" % root
    json.dump(out, open(o, "w"), indent=1, ensure_ascii=False)
    enc = sum(1 for v in out.values() if v["hpo"])
    print("%s: encoded %d/%d answers, mean %.1f concepts"
          % (root, enc, len(out), sum(len(v["hpo"]) for v in out.values()) / max(enc, 1)))

elif sys.argv[1] == "gt":
    cases = json.load(open(B + "/data/cases.json"))
    out, lock = {}, threading.Lock()
    miss = []

    def work(q):
        while True:
            with lock:
                if not q:
                    return
                c = q.pop()
            txt = c["part1_video_only"]["visible_sign"]
            try:
                rep = ask(txt)
            except Exception as e:                                # noqa: BLE001
                rep = ""
                print("ERR", c["video"], e)
            hp, un = to_hpo(rep)
            with lock:
                out[c["video"]] = dict(line=c["line"], sign=txt, reply=rep.strip(),
                                       hpo=sorted(hp),
                                       labels=sorted(vocab[h]["label"] for h in hp),
                                       unmatched=un)
                miss.extend(un)

    q = list(cases)
    ts = [threading.Thread(target=work, args=(q,)) for _ in range(6)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    json.dump(out, open(os.environ.get("DDX_WORK", "/tmp") + "/gt_hpo.json", "w"), indent=1, ensure_ascii=False)
    enc = sum(1 for v in out.values() if v["hpo"])
    print("encoded %d/71 ground-truth signs (was 20/71 with plain string matching)" % enc)
    print("mean HPO concepts per case: %.1f"
          % (sum(len(v["hpo"]) for v in out.values()) / max(enc, 1)))
    print("\nexamples")
    for v in list(out.values())[:10]:
        print("   %-58s -> %s" % (v["sign"][:58], ", ".join(v["labels"]) or "(none)"))
    from collections import Counter
    print("\nterms the model produced that HPO has no entry for (top 15)")
    for t, n in Counter(miss).most_common(15):
        print("   %-44s %d" % (t, n))
