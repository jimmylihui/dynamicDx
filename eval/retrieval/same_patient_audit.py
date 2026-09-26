"""Same-patient audit of the retained retrieval records (Appendix F, "Decontamination").

Source-clean filtering removes the source article itself, but another report of the SAME patient
(a follow-up, a series, a conference abstract) would leak the answer just as well. Every record
retained after source-clean filtering is checked two ways:

  1. author overlap  - the record shares at least one author (surname + first initial) with the
                       source article; those that ALSO share two or more diagnosis words are
                       listed for manual review
  2. author-independent - the abstract describes a patient of the case's age and sex and shares a
                       rare diagnosis term (a diagnosis word present in fewer than RARE of all
                       retained records); these are listed for manual review

A record flagged by both checks would be a same-patient candidate. The flagged records are written
out with the source article's details so that a reviewer can compare country, year and
presentation; the script itself does not decide.

usage: same_patient_audit.py RETAINDIR [OUT_JSON]
       RETAINDIR: per-case retained records written by openspace.py (RETAINDIR=..., CLEAN=clean)
env:   RARE (default 0.005)
"""
import collections
import glob
import json
import os
import re
import sys

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RETAIN = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else B + "/results/same_patient_audit.json"
RARE = float(os.environ.get("RARE", "0.005"))

cases = {c["video"].rsplit(".", 1)[0]: c for c in json.load(open(B + "/data/cases.json"))}
arts = json.load(open(B + "/data/source_licences.json"))
STOP = set("""a an the of and or with without in on to for from by due as at after before
associated related secondary primary acute chronic type syndrome disease disorder case patient
left right bilateral unilateral onset induced""".split())
SEX = {"male": {"man", "male", "boy", "gentleman"}, "female": {"woman", "female", "girl", "lady"}}


def words(t):
    return {w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if len(w) >= 4 and w not in STOP}


def authors(s):
    """'Nie J, Gao Q, Li Y.' -> {('nie','j'), ...}"""
    out = set()
    for a in re.split(r"[,;]", s or ""):
        parts = a.strip(" .").split()
        if len(parts) >= 2:
            out.add((parts[0].lower(), parts[-1][0].lower()))
    return out


def diag_terms(c):
    txt = [re.split(r"\s[-–—]\s", c.get("true_diagnosis") or "", maxsplit=1)[0]]
    txt += list(c["part1_video_only"].get("accept_as_correct") or [])
    return set().union(*[words(t) for t in txt]) if txt else set()


def age_sex(abstract, age, sex):
    if age is None or sex not in SEX:
        return False
    a = (abstract or "").lower()
    pat = r"\b%d[- ](?:year|yr)s?[- ]old\b|\baged? %d\b" % (age, age)
    return bool(re.search(pat, a)) and any(re.search(r"\b%s\b" % w, a) for w in SEX[sex])


recs = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(RETAIN + "/*.json")}
# document frequency of every word over all distinct retained records, for "rare diagnosis term"
distinct = {}
for rs in recs.values():
    for r in rs:
        distinct[r.get("id") or r.get("pmid") or r.get("title")] = r
df = collections.Counter()
for r in distinct.values():
    df.update(words((r.get("title") or "") + " " + (r.get("abstractText") or "")))
N = max(len(distinct), 1)

flag_auth, flag_indep, both = [], [], []
n_auth_cases = set()
for key, rs in sorted(recs.items()):
    c = cases.get(key)
    if not c:
        continue
    src = arts.get(c["source"]["pmcid"]) or {}
    src_auth = authors(src.get("authors"))
    dterms = diag_terms(c)
    rare = {w for w in dterms if df[w] / N < RARE}
    demo = c["part2_yes_no"].get("demographics") or {}
    for r in rs:
        text = (r.get("title") or "") + " " + (r.get("abstractText") or "")
        w = words(text)
        item = dict(case=key, source_pmcid=c["source"]["pmcid"], source_year=src.get("year"),
                    record=r.get("pmcid") or r.get("pmid") or r.get("id"), title=r.get("title"),
                    year=r.get("pubYear"), journal=r.get("journalTitle"))
        a = bool(src_auth & authors(r.get("authorString")))
        i = bool(rare & w) and age_sex(r.get("abstractText"), demo.get("age"), demo.get("sex"))
        if a:
            n_auth_cases.add(key)
            if len(dterms & w) >= 2:
                flag_auth.append(dict(item, shared_terms=sorted(dterms & w)))
        if i:
            flag_indep.append(dict(item, rare_terms=sorted(rare & w)))
        if a and i:
            both.append(item)

n_auth = sum(1 for key, rs in recs.items() if key in cases for r in rs
             if authors((arts.get(cases[key]["source"]["pmcid"]) or {}).get("authors"))
             & authors(r.get("authorString")))
json.dump(dict(n_records=len(distinct), author_overlap=dict(records=n_auth, cases=len(n_auth_cases)),
               author_overlap_and_two_diagnosis_words=flag_auth,
               author_independent_age_sex_rare_term=flag_indep, both_criteria=both),
          open(OUT, "w"), indent=1, ensure_ascii=False)
print("distinct retained records             : %d" % len(distinct))
print("share an author with the source       : %d records in %d cases" % (n_auth, len(n_auth_cases)))
print("  ... and two or more diagnosis words : %d (listed for review)" % len(flag_auth))
print("age + sex + rare diagnosis term       : %d (listed for review)" % len(flag_indep))
print("both criteria                         : %d" % len(both))
print("-> %s" % OUT)
