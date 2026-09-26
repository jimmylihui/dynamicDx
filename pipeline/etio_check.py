"""How many clips carry a real, documented aetiology?

For each clip the dataset states an aetiology. That statement can stand on three very different
footings:

  documented   the source article names the same disease, so the label is evidence-backed
  borrowed     the source names a different disease; the sign is real, the cause is synthesized
               (the benchmark's stated design, but it means the label is not evidence about the
               patient on screen)
  unsourced    there is no source article at all, so nothing can be checked

The distinction matters for what the dataset can claim: only the documented group supports
"this video shows disease X".

Fetches each PMC record's title and abstract and scores overlap with the assigned aetiology.
The score only sorts the list for review; the verdicts still need reading.
"""
import json
import os
import re
import urllib.parse
import urllib.request

REST = "https://www.ebi.ac.uk/europepmc/webservices/rest"
STOP = set("""the a an of and or with from due to in on for by as at is are was were this that
these those case report a rare presenting presentation patient patients disease syndrome
secondary related associated onset acute chronic severe moderate mild very type""".split())


def norm(s):
    return {w for w in re.findall(r"[a-z]{4,}", (s or "").lower()) if w not in STOP}


index = json.load(open("index.json"))
rows = []
for e in index:
    pmcid = (e["source"] or {}).get("pmcid")
    etio = ((e.get("clinician_labels") or {}).get("etiology")
            or e.get("etiology") or "")
    rec = dict(video=e["video"], line=e["disease_line"], etiology=etio, pmcid=pmcid,
               title="", overlap=0.0, status="unsourced")
    if pmcid:
        try:
            u = ("%s/search?query=%s&resultType=core&format=json"
                 % (REST, urllib.parse.quote("PMCID:" + pmcid)))
            d = json.loads(urllib.request.urlopen(u, timeout=60).read())
            r0 = (d.get("resultList", {}).get("result") or [{}])[0]
            title = r0.get("title") or ""
            abstract = (r0.get("abstractText") or "")[:900]
            rec["title"] = title
            a, b = norm(etio), norm(title + " " + abstract)
            rec["overlap"] = round(len(a & b) / max(len(a), 1), 2)
            rec["shared"] = sorted(a & b)
            rec["status"] = "checked"
        except Exception as ex:
            rec["status"] = "fetch-failed:%s" % ex
    rows.append(rec)

json.dump(rows, open("etio_check.json", "w"), indent=1, ensure_ascii=False)
un = [r for r in rows if r["status"] == "unsourced"]
ck = [r for r in rows if r["status"] == "checked"]
print("clips: %d | with a source article: %d | with NO source at all: %d"
      % (len(rows), len(ck), len(un)))
print("\n=== NO SOURCE ARTICLE (aetiology cannot be checked at all) ===")
for r in sorted(un, key=lambda r: r["line"]):
    print("  %-14s %-40s %s" % (r["line"], r["video"][:40], r["etiology"][:60]))
print("\n=== SOURCED, sorted by how much the label overlaps the article ===")
for r in sorted(ck, key=lambda r: r["overlap"]):
    print("  ov=%.2f %-14s %-38s" % (r["overlap"], r["line"], r["video"][:38]))
    print("        label   : %s" % r["etiology"][:100])
    print("        article : %s" % r["title"][:100])
