"""Pull a source dossier for every clip, so cases can be rebuilt on documented facts.

The new design needs two things the dataset does not currently hold: a yes/no answerable feature
table for the patient, and investigations that return a real result rather than a line-level
template ("Usually normal", "n/a"). Both have to come from the source case report, so the first
step is to extract, per clip, what its article actually records.

Per article this stores the title, the licence, the abstract, and the body split into the
sections a case report uses - presentation, examination, investigations, diagnosis, treatment
and outcome - plus every sentence carrying a numeric result, which is where lab values live.

Nothing here decides anything; it is the evidence base the case rewrite reads from.
"""
import json
import os
import re
import urllib.parse
import urllib.request

REST = "https://www.ebi.ac.uk/europepmc/webservices/rest"

SECTION = re.compile(
    r"(case (?:report|presentation|description)|clinical (?:presentation|course|vignette)|"
    r"presentation|examination|investigation|diagnosis|treatment|management|outcome|"
    r"follow[- ]up|discussion)", re.I)
NUMERIC = re.compile(r"\d")
UNITS = re.compile(r"(mg/dL|mmol/L|g/L|IU/L|mIU/L|ng/dL|µg|mcg|%|/µL|mm/h|U/mL|titer|titre|"
                   r"Hz|mm|cm|score|ratio|copies|cells)", re.I)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "clinic-video-bench/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def plain(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x))


index = json.load(open("index.json"))
out = []
for e in index:
    v = e["video"]
    pmcid = (e["source"] or {}).get("pmcid")
    if not pmcid:
        m = re.search(r"PMC(\d+)", v)
        pmcid = "PMC" + m.group(1) if m else None
    rec = dict(video=v, line=e["disease_line"], pmcid=pmcid,
               current_etiology=(e.get("clinician_labels") or {}).get("etiology") or "")
    if not pmcid:
        rec["status"] = "no source"
        out.append(rec)
        continue
    try:
        meta = json.loads(get("%s/search?query=%s&resultType=core&format=json"
                              % (REST, urllib.parse.quote("PMCID:" + pmcid))))
        r0 = (meta.get("resultList", {}).get("result") or [{}])[0]
        rec["title"] = r0.get("title") or ""
        rec["journal"] = r0.get("journalTitle") or ""
        rec["licence"] = r0.get("license") or "?"
        rec["abstract"] = (r0.get("abstractText") or "")[:2500]
        xml = get("%s/%s/fullTextXML" % (REST, pmcid))
        body = plain(xml)
        # sentences that look like they carry a measured result
        sents = re.split(r"(?<=[.;])\s+", body)
        rec["numeric_sentences"] = [s.strip()[:320] for s in sents
                                    if NUMERIC.search(s) and UNITS.search(s)][:60]
        # rough section slices around case-report headings
        slices = {}
        for m in SECTION.finditer(body):
            key = m.group(1).lower()
            slices.setdefault(key, body[m.start():m.start() + 2200])
        rec["sections"] = slices
        rec["status"] = "ok"
    except Exception as ex:
        rec["status"] = "error: %s" % ex
    out.append(rec)
    print("%-46s %-12s %s" % (v[:46], rec.get("status"), (rec.get("title") or "")[:60]),
          flush=True)

json.dump(out, open("dossier.json", "w"), indent=1, ensure_ascii=False)
ok = sum(1 for r in out if r.get("status") == "ok")
print("\ndossiers: %d ok / %d clips" % (ok, len(out)))
print("with numeric result sentences: %d"
      % sum(1 for r in out if r.get("numeric_sentences")))
