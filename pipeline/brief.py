"""Compact per-case evidence brief: what the source article records about this patient."""
import json
import os, re, sys
LINE = sys.argv[1] if len(sys.argv) > 1 else None
d = json.load(open("dossier.json"))
CLIN = re.compile(r"(presented|complain|history of|examination reveal|revealed|was diagnosed|"
                  r"developed|denied|no history|showed|treated with|improved|resolved|"
                  r"year-old|admitted)", re.I)
for r in d:
    if LINE and r["line"] != LINE:
        continue
    body = " ".join(r.get("sections", {}).values())
    ag = re.search(r"\b(\d{1,2})[- ]year[- ]old\s+(\w+)", body)
    sents = [s.strip() for s in re.split(r"(?<=[.;])\s+", body) if CLIN.search(s)]
    seen, keep = set(), []
    for s in sents:
        k = s[:60]
        if k in seen:
            continue
        seen.add(k)
        keep.append(s[:250])
    print("=" * 4, r["video"], "|", r["line"])
    print("  TITLE :", (r.get("title") or "")[:130])
    print("  NOW   :", r["current_etiology"][:90])
    print("  WHO   :", ag.group(0) if ag else "?")
    for s in keep[:9]:
        print("   *", s)
    for s in r.get("numeric_sentences", [])[:6]:
        if "Creative Commons" in s or "open access" in s:
            continue
        print("   #", s[:210])
    print()
