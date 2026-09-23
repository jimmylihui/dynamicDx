"""An open disease space built from the literature, not from a closed candidate list.

HPOA covers rare disease and misses 89% of our aetiologies; a 71-case closed set is not a general
system. Every case here came from a published case report, so the literature itself can be the
disease space: query it with the phenomenology alone, extract what causes other authors reported
for that same sign, and see whether the true cause is among them.

The query is built from phenomenology terms ONLY. Nothing about the aetiology, the demographics or
the investigations may enter it - otherwise the retrieval is told the answer.

usage: openspace.py oracle       query from the ground-truth phenomenology (isolates retrieval)
       openspace.py MODEL_ROOT   query from a model's own phenomenology
"""
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request

B = os.environ.get("DDX_ROOT", ".")
ORKEY = os.environ["ORKEY"]
EXTRACT_MODEL = os.environ.get("EXTRACT_MODEL", "openai/gpt-5.6-luna")
NPAPERS = int(os.environ.get("NPAPERS", "250"))
SCOPE = os.environ.get("SCOPE", "broad")
USE_VARIANTS = os.environ.get("VARIANTS", "1") == "1"
SUBTYPE_CAP = int(os.environ.get("SUBTYPE_CAP", "10"))
PERCONCEPT = int(os.environ.get("PERCONCEPT", "250"))
MODE = sys.argv[1]

KF = int(os.environ.get("KFRAMES", "32"))
cases = {c["video"]: c for c in json.load(open(B + "/data/cases.json"))}

# --- retrieval decontamination -------------------------------------------------------------
# Both the cases and the corpus come from Europe PMC, so an unfiltered query can return the very
# article the case was built from. CLEAN selects how much of that is removed:
#   orig    nothing (the original implementation, kept only for comparison)
#   clean   the source PMCID, anything sharing its DOI, and near-duplicate titles
#   strict  clean, plus any record naming the confirmed diagnosis in its title or abstract excerpt
# The strict rule reads the ground truth and is therefore an evaluation-side contamination audit,
# not a deployable retrieval step. Filtering happens BEFORE cause extraction in every condition.
CLEAN = os.environ.get("CLEAN", "orig")
# where the raw Europe PMC records are cached, one file per case, so every condition sees
# the same corpus and the search is paid for once
RECDIR = os.environ.get("RECDIR", "")
if RECDIR:
    os.makedirs(RECDIR, exist_ok=True)
JACCARD = float(os.environ.get("JACCARD", "0.85"))
STOP = set("a an the of and or in on with without for to from by at as is are was were case "
           "report reports study patient patients novel rare due secondary associated presenting "
           "presentation clinical review series".split())
_srcmeta, _srclock = {}, threading.Lock()


def norm_words(t):
    return [w for w in re.sub(r"[^a-z0-9 ]", " ", (t or "").lower()).split()
            if w and w not in STOP]


def jaccard(a, b):
    A, B = set(norm_words(a)), set(norm_words(b))
    return len(A & B) / len(A | B) if A and B else 0.0


def source_meta(pmcid):
    """Title and DOI of the article a case was built from, read from Europe PMC itself."""
    with _srclock:
        if pmcid in _srcmeta:
            return _srcmeta[pmcid]
    url = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMCID:"%s"'
           "&format=json&pageSize=1&resultType=core" % pmcid)
    meta = {}
    for _ in range(3):
        try:
            r = json.loads(urllib.request.urlopen(url, timeout=60).read().decode())
            hit = (r.get("resultList", {}).get("result") or [{}])[0]
            meta = {"title": hit.get("title", ""), "doi": (hit.get("doi") or "").lower()}
            break
        except Exception:                                          # noqa: BLE001
            time.sleep(2)
    with _srclock:
        _srcmeta[pmcid] = meta
    return meta


def answer_strings(case):
    """The confirmed diagnosis and its accepted synonyms, normalised for substring matching.

    true_diagnosis is a sentence - the entity, then a dash, then the reasoning - so only the part
    before the dash is used. Anything under four characters or reducing to a single stopword is
    dropped: matching those would delete the corpus rather than the answer.
    """
    out = []
    td = (case.get("true_diagnosis") or "").split(" - ")[0]
    for t in [td] + list(case["part1_video_only"].get("accept_as_correct") or []):
        w = norm_words(t)
        if w and len(" ".join(w)) >= 4:
            out.append(" ".join(w))
    return out


def decontaminate(papers, case, pmcid):
    """Drop the source article and, at the stricter levels, its relatives and answer-bearing hits.

    Returns the surviving records and a per-rule count, so the appendix can report what each rule
    removed rather than only the total.
    """
    n = dict(source_pmcid=0, shared_doi=0, near_duplicate=0, answer_string=0)
    flagged = []
    if CLEAN == "orig":
        return papers, n, flagged
    meta = source_meta(pmcid) if pmcid else {}
    ans = answer_strings(case) if CLEAN == "strict" else []
    keep = []
    for p2 in papers:
        pid = (p2.get("pmcid") or "").upper()
        doi = (p2.get("doi") or "").lower()
        title = p2.get("title") or ""
        if pmcid and pid == pmcid.upper():
            n["source_pmcid"] += 1
            continue
        if meta.get("doi") and doi and doi == meta["doi"]:
            n["shared_doi"] += 1
            continue
        if meta.get("title") and jaccard(title, meta["title"]) >= JACCARD:
            n["near_duplicate"] += 1
            flagged.append({"pmcid": pid, "title": title,
                            "jaccard": round(jaccard(title, meta["title"]), 3)})
            continue
        if ans:
            hay = " ".join(norm_words(title + " " +
                                      " ".join((p2.get("abstractText") or "").split())[:260]))
            if any(a in hay for a in ans):
                n["answer_string"] += 1
                continue
        keep.append(p2)
    return keep, n, flagged


if MODE == "oracle":
    # the ceiling: perfect phenomenology, so this isolates the retrieval layer
    gt = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/gt_hpo.json"))
else:
    # end to end: the query is built from what the VISION MODEL said it saw
    src = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/ans_hpo_%s.json" % MODE))
    gt = {}
    for a in src.values():
        if a["k"] == KF and a.get("labels"):
            gt[a["video"]] = dict(labels=a["labels"])
    print("model=%s k=%d, cases with a usable description: %d" % (MODE, KF, len(gt)))

# Anatomy is not a search term, but laterality and distribution ARE - unilateral chorea and
# generalised chorea have different cause lists, and the modifiers were encoded precisely so they
# could narrow the query. Only the body-part words are dropped.
ANATOMY = re.compile(r"^(arm|arms|leg|legs|hand|hands|foot|feet|face|head|neck|trunk|eye|eyes|"
                     r"eyelid|limb|limbs|upper limb|lower limb|upper limbs|lower limbs|"
                     r"shoulder|finger|fingers|tongue|jaw)$", re.I)
MODIFIER = re.compile(r"^(bilateral|unilateral|left|right|generalized|focal|multifocal|axial|"
                      r"proximal|distal|lateral|alternating laterality)$", re.I)
DROP = ANATOMY


# Standardising the terminology improved the encoding and hurt the retrieval: authors title their
# papers with free wording, so a paper on lithium cerebellar toxicity says "cerebellar dysfunction"
# and never "gait ataxia". 15 of 27 misses were the query failing to reach the case's OWN source
# paper. The fix is expansion, not further standardisation - query with every surface form the
# ontology carries for the concept, plus its ancestors' forms.
_VOC = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/hpo_vocab.json"))
_icv = os.environ.get("DDX_WORK", "/tmp") + "/icvd_vocab.json"
if os.path.exists(_icv):
    for _h, _d in json.load(open(_icv)).items():
        _VOC.setdefault(_h, _d)
LABEL2FORMS = {}
for _h, _d in _VOC.items():
    LABEL2FORMS.setdefault(_d["label"], set()).update(_d.get("terms", []))
    LABEL2FORMS[_d["label"]].add(_d["label"].lower())


# HPO carries about two surface forms per concept, which is far short of how many ways authors
# actually write a sign - "gait ataxia" appears in the literature as unsteady gait, wide-based
# gait, staggering gait, cerebellar gait, gait instability, ataxic gait. The ontology synonyms are
# kept and a cached set of free-text variants is generated once per concept and reused.
VARIANT_CACHE = os.environ.get("DDX_WORK", "/tmp") + "/sign_variants.json"
_variants = json.load(open(VARIANT_CACHE)) if os.path.exists(VARIANT_CACHE) else {}
_vlock = threading.Lock()

# Synonyms of the concept were not enough. Papers are titled with the SUBTYPE, not the umbrella
# term: the NIID case is "Unilateral Wing-Beating Tremor", the anti-IgLON5 case is "Pisa
# syndrome", the vaccine case is "Hemichorea-Hemiballism" - none of which a query for tremor,
# dystonia or chorea reaches. Expansion therefore goes downward into named subtypes as well as
# sideways into synonyms.
VASK = """A clinical author is writing the title of a case report about the sign "%s".

Give 10 lines, nothing else:
- first, 4 ways to write that sign itself, as an author would phrase it
- then 6 NAMED SUBTYPES or named variants of that sign that have their own name in the
  literature. For tremor these would include wing-beating tremor, Holmes tremor, orthostatic
  tremor, palatal tremor. For chorea, hemichorea, hemiballismus, choreoathetosis. For dystonia,
  Pisa syndrome, blepharospasm, torticollis, camptocormia.

Use only real published terminology. Do not name any disease or cause."""


def free_variants(label):
    with _vlock:
        if label in _variants:
            return _variants[label]
    body = json.dumps({"model": EXTRACT_MODEL, "temperature": 0, "max_tokens": 150,
                       "messages": [{"role": "user", "content": VASK % label}],
                       "provider": {"order": ["OpenAI"], "allow_fallbacks": False,
                                    "sort": "price"},
                       "reasoning": {"enabled": False}}).encode()
    got = []
    try:
        r = json.loads(urllib.request.urlopen(urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions", data=body,
            headers={"Authorization": "Bearer " + ORKEY,
                     "Content-Type": "application/json"}), timeout=120).read().decode())
        t = r.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
        for line in t.splitlines():
            v = re.sub(r"^\s*[-*\d.)]+\s*", "", line).strip().strip('"').lower()
            if 4 < len(v) < 45 and v not in got:
                got.append(v)
    except Exception:                                              # noqa: BLE001
        pass
    with _vlock:
        _variants[label] = got[:6]
        json.dump(_variants, open(VARIANT_CACHE, "w"), indent=1, ensure_ascii=False)
    return got[:6]


def expand(label, cap=4):
    """ontology synonyms first, then author phrasings, then named subtypes"""
    forms = sorted(LABEL2FORMS.get(label, {label.lower()}), key=len)
    forms = [f for f in forms if 4 < len(f) < 45][:cap] or [label.lower()]
    if USE_VARIANTS:
        for v in free_variants(label):
            if v not in forms:
                forms.append(v)
    return forms[:SUBTYPE_CAP]


def query_terms(labels, anc_of=None):
    """Specific terms rank the answer; broad terms keep it in the pool at all.

    Standardising the ground truth made the terms precise, which pushed the true cause up the
    ranking but shrank the literature pool - "wing-beating tremor" retrieves far fewer case
    reports than "tremor", and the long-tail aetiologies fall out of reach. Querying at both
    granularities and merging recovers the recall without giving back the precision.
    """
    signs = [l for l in labels
             if not ANATOMY.match(l.strip()) and not MODIFIER.match(l.strip())]
    mods = [l for l in labels if MODIFIER.match(l.strip())]
    broad = []
    for l in signs:
        for a in (anc_of or {}).get(l, []):
            if a not in broad and not ANATOMY.match(a) and not MODIFIER.match(a):
                broad.append(a)
    # Round-robin across concepts was tried and rolled back: it did reach the second concept of a
    # multi-sign case, but it widened every query at once, the candidate set went 202 -> 458 and
    # lenient recall fell 82.4% -> 73.5%. Concept-major order is kept; multi-concept coverage is
    # bought instead by the per-concept quota pass below, which keeps each concept's results in
    # their own ranked list rather than merging them into one query.
    sign_forms, seen = [], set()
    for l in signs:
        for f in expand(l):
            if f not in seen:
                seen.add(f)
                sign_forms.append(f)
    broad_forms = []
    for l in broad[:3]:
        for f in expand(l, 2):
            if f not in seen:
                seen.add(f)
                broad_forms.append(f)
    return sign_forms[:20], broad_forms[:6], mods[:2]


def epmc(terms, mods=(), scope=None, n=None):
    """Two filters were costing an order of magnitude of corpus for no necessary reason.

    OPEN_ACCESS:Y removed 90% of the pool - chorea went from 7548 papers to 312 - but open access
    is only needed to redistribute a full text, and this pipeline reads titles and abstracts,
    which Europe PMC serves for everything. PUB_TYPE:"Case Reports" removed another 50-86%, and
    it excludes exactly the reviews that enumerate a whole differential in one paper.

    scope: "strict" reproduces the old behaviour, "broad" drops both filters, None uses BROAD.
    """
    if not terms:
        return []
    q = "(%s)" % " OR ".join('TITLE:"%s" OR ABSTRACT:"%s"' % (t, t) for t in terms)
    if mods:
        q += " AND (%s)" % " OR ".join('ABSTRACT:"%s"' % m for m in mods)
    if (scope or SCOPE) == "strict":
        q += ' AND (PUB_TYPE:"Case Reports") AND OPEN_ACCESS:Y'
    else:
        q += ' AND (PUB_TYPE:"Case Reports" OR PUB_TYPE:"Review")' 
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%s"
           "&format=json&pageSize=%d&resultType=core" % (urllib.parse.quote(q), n or NPAPERS))
    for _ in range(3):
        try:
            r = json.loads(urllib.request.urlopen(url, timeout=90).read().decode())
            return r.get("resultList", {}).get("result", [])
        except Exception:                                          # noqa: BLE001
            time.sleep(3)
    return []


ASK = """Below are published papers, all retrieved because they describe the same clinical sign.
Each entry is a title followed by the start of its abstract.

For each entry, name the underlying CAUSE or DISEASE it was about, in four words or fewer. If the
paper is a review that enumerates several causes, list them separated by " ; ". One entry per
line, in the same order, nothing else. Write SKIP if no cause is named.

%s"""


def extract_raw(prompt):
    body = json.dumps({"model": EXTRACT_MODEL, "temperature": 0, "max_tokens": 1200,
                       "messages": [{"role": "user", "content": prompt}],
                       "provider": {"order": ["OpenAI"], "allow_fallbacks": False,
                                    "sort": "price"},
                       "reasoning": {"enabled": False}}).encode()
    for _ in range(3):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=300).read().decode())
            return r.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
        except Exception:                                          # noqa: BLE001
            time.sleep(5)
    return ""


def extract(titles):
    body = json.dumps({"model": EXTRACT_MODEL, "temperature": 0, "max_tokens": 2500,
                       "messages": [{"role": "user",
                                     "content": ASK % "\n".join(titles)}],
                       "provider": {"order": ["OpenAI"], "allow_fallbacks": False,
                                    "sort": "price"},
                       "reasoning": {"enabled": False}}).encode()
    for _ in range(3):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=300).read().decode())
            return r.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
        except Exception:                                          # noqa: BLE001
            time.sleep(5)
    return ""


# label -> its ancestors' labels, so a query can be widened one level up the ontology
_v = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/hpo_vocab.json"))
_lab = {h: d["label"] for h, d in _v.items()}
_par = {h: d.get("parents", []) for h, d in _v.items()}
ANC_LABEL = {}
for _h, _d in _v.items():
    up = []
    for _p in _par.get(_h, []):
        if _p in _lab:
            up.append(_lab[_p])
    if up:
        ANC_LABEL[_d["label"]] = up

WIKI = os.environ.get("WIKI", "0") == "1"
WCACHE = os.environ.get("DDX_WORK", "/tmp") + "/wiki_causes.json"
_wiki = json.load(open(WCACHE)) if os.path.exists(WCACHE) else {}
_wlock = threading.Lock()

WASK = """Below is the text of an encyclopaedia article about a clinical sign. List every disease,
drug, toxin, deficiency or other cause it names as producing that sign. Four words or fewer each,
one per line, nothing else. Do not add causes the text does not mention.

%s"""


def wiki_causes(label):
    """A literature search returns what is publishable, which skews rare and novel. An
    encyclopaedia article lists what is common - the Ataxia article names lithium and thiamine,
    the Myoclonus article names hyperglycaemia - which is exactly the half of our aetiologies that
    case reports under-represent. Coverage is uneven: the Chorea article is a fifth the length of
    the others and names neither thyroid disease nor hyperglycaemia, so this is a parallel source,
    not a replacement."""
    with _wlock:
        if label in _wiki:
            return _wiki[label]
    txt = ""
    for title in (label, label + " (medicine)", label.split()[-1].capitalize()):
        u = ("https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1"
             "&redirects=1&format=json&titles=" + urllib.parse.quote(title))
        try:
            rq = urllib.request.Request(u, headers={"User-Agent": "clinic-video-bench/1.0"})
            d = json.loads(urllib.request.urlopen(rq, timeout=30).read().decode())
            for pg in d.get("query", {}).get("pages", {}).values():
                e = pg.get("extract") or ""
                if len(e) > len(txt):
                    txt = e
        except Exception:                                          # noqa: BLE001
            pass
        if len(txt) > 4000:
            break
    causes = []
    if len(txt) > 400:
        rep = extract_raw(WASK % txt[:12000])
        for line in rep.splitlines():
            c = re.sub(r"^\s*[-*\d.)]+\s*", "", line).strip()
            if 2 < len(c) < 60 and c.upper() != "SKIP":
                causes.append(c)
    with _wlock:
        _wiki[label] = causes
        json.dump(_wiki, open(WCACHE, "w"), indent=1, ensure_ascii=False)
    return causes


out, lock = {}, threading.Lock()
done = [0]
todo = [v for v in cases if v in gt and gt[v].get("labels")]
t0 = time.time()


def work(q):
    while True:
        with lock:
            if not q:
                return
            v = q.pop()
        terms, broad, mods = query_terms(gt[v]["labels"], ANC_LABEL)
        # One big OR query lets Europe PMC spend its whole page budget on whichever concept it
        # finds most relevant, so a case described by three signs gets one sign retrieved well and
        # the others barely at all. Each concept is given its own quota instead, and only then are
        # the modifier-constrained and ancestor passes added.
        papers, seen_t = [], set()

        def add(ps):
            for p2 in ps:
                k = p2.get("title", "").strip()
                if k and k not in seen_t:
                    seen_t.add(k)
                    papers.append(p2)

        # The three decontamination conditions must be compared on ONE corpus. Europe PMC is a live
        # index and re-querying returned 1000 records for a case in one run and 991 in the next, so
        # running each condition as its own search would confound the filter with search drift.
        # The search is therefore done once, cached to disk, and every condition filters that file.
        rec = "%s/%s.json" % (RECDIR, v.split(".")[0]) if RECDIR else None
        if rec and os.path.exists(rec):
            papers = json.load(open(rec))
            seen_t = {(x.get("title") or "").strip() for x in papers}
        else:
            add(epmc(terms, mods))                   # narrowest first, ranks highest
            for t1 in terms:
                add(epmc([t1], (), n=PERCONCEPT))    # per-concept quota, subtypes included
            if broad:
                add(epmc(broad, (), n=PERCONCEPT))
            if rec:
                json.dump([{k: x.get(k) for k in
                            ("id", "pmcid", "pmid", "doi", "title", "abstractText",
                             "authorString", "pubYear", "journalTitle")}
                           for x in papers], open(rec, "w"), indent=1, ensure_ascii=False)
        pmcid = ((cases[v].get("source") or {}).get("pmcid") or "")
        papers, removed, flagged = decontaminate(papers, cases[v], pmcid)
        entries = []
        for p in papers:
            t = (p.get("title") or "").strip()
            if not t:
                continue
            ab = " ".join((p.get("abstractText") or "").split())[:260]
            entries.append("%s%s" % (t, (" || " + ab) if ab else ""))
        titles = entries
        causes = []
        for i in range(0, min(len(entries), NPAPERS), 40):     # batch so the reply is not cut off
            rep = extract(entries[i:i + 40])
            for line in rep.splitlines():
                s = re.sub(r"^\s*[-*\d.)]+\s*", "", line).strip()
                if not s or s.upper() == "SKIP":
                    continue
                for part in s.split(";"):                      # reviews may list several
                    part = part.strip()
                    if part and part.upper() != "SKIP" and 2 < len(part) < 60:
                        causes.append(part)
        wiki_c = []
        if WIKI:
            for l in gt[v]["labels"][:3]:
                if not ANATOMY.match(l) and not MODIFIER.match(l):
                    wiki_c += wiki_causes(l)
        # Appended, not prepended. Putting the encyclopaedia list first was tried and it filled
        # the top 34-53 positions of every case with the classic differential, taking recall@5
        # from 19.1% to 4.4% - our aetiologies are rare presentations of common disease, which is
        # not what a "causes of chorea" section leads with. Appending can only add reach.
        causes = causes + [c for c in wiki_c if c.lower() not in {x.lower() for x in causes}]
        with lock:
            out[v] = dict(line=cases[v]["line"], terms=terms, broad=broad, mods=mods,
                          n_wiki=len(wiki_c),
                          clean=CLEAN, removed=removed, flagged=flagged,
                          n_retrieved=len(seen_t), n_papers=len(titles),
                          causes=causes, truth=cases[v]["true_diagnosis"])
            done[0] += 1
            if done[0] % 10 == 0:
                el = time.time() - t0
                print("[%2d/%2d] %4.0fs eta %4.0fs" % (done[0], len(todo), el,
                                                       (len(todo) - done[0]) * el / done[0]),
                      flush=True)


SUBSET = set(x for x in os.environ.get("ONLY", "").split(",") if x)
if SUBSET:
    prev = os.environ.get("DDX_WORK", "/tmp") + "/openspace_%s.json" % MODE
    if os.path.exists(prev):
        out.update(json.load(open(prev)))
    todo = [v for v in todo if v in SUBSET]
    print("ONLY: %d cases to re-probe" % len(todo))
q = list(todo)
ts = [threading.Thread(target=work, args=(q,)) for _ in range(6)]
[t.start() for t in ts]
[t.join() for t in ts]
OUTF = os.environ.get("OUTFILE", os.environ.get("DDX_WORK", "/tmp") + "/openspace_%s_%s.json" % (MODE, CLEAN))
json.dump(out, open(OUTF, "w"), indent=1, ensure_ascii=False)
print("CLEAN=%s -> %s" % (CLEAN, OUTF))
print("\n%d cases probed" % len(out))
print("mean papers retrieved : %.0f" % (sum(o["n_papers"] for o in out.values()) / len(out)))
print("mean causes extracted : %.0f" % (sum(len(o["causes"]) for o in out.values()) / len(out)))
print("mean DISTINCT causes  : %.0f"
      % (sum(len({c.lower() for c in o["causes"]}) for o in out.values()) / len(out)))
