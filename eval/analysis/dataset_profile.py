"""Dataset profile for the reviewer: labels, demographics, geography, source clustering,
subgroup performance, and case-level vs source-clustered bootstrap intervals."""
import os
import collections
import json
import random
import re

B = os.environ.get("DDX_ROOT", ".")
C = json.load(open(B + "/data/cases.json"))
M = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/src_meta.json"))

COUNTRY = {"China": "China", "India": "India", "IND": "India", "USA": "United States",
           "United States": "United States", "CA": "United States", "Kansas": "United States",
           "Korea": "South Korea", "Japan": "Japan", "UK": "United Kingdom", "PRT": "Portugal",
           "Italy": "Italy", "Türkiye": "Turkey", "Turkey": "Turkey", "THA": "Thailand",
           "Russia": "Russia", "Morocco": "Morocco", "MAR": "Morocco", "Malaysia": "Malaysia",
           "Greece": "Greece", "Germany": "Germany", "GIN": "Guinea", "France": "France",
           "Ethiopia": "Ethiopia", "Croatia": "Croatia", "Colombia": "Colombia", "BGR": "Bulgaria",
           "Australia": "Australia", "MD": "Netherlands"}
REGION = {"China": "East Asia", "Japan": "East Asia", "South Korea": "East Asia",
          "India": "South/SE Asia", "Thailand": "South/SE Asia", "Malaysia": "South/SE Asia",
          "United States": "North America", "Colombia": "Latin America",
          "United Kingdom": "Europe", "Portugal": "Europe", "Italy": "Europe", "Greece": "Europe",
          "Germany": "Europe", "France": "Europe", "Croatia": "Europe", "Bulgaria": "Europe",
          "Netherlands": "Europe", "Russia": "Europe", "Turkey": "Middle East",
          "Morocco": "Africa", "Guinea": "Africa", "Ethiopia": "Africa", "Australia": "Oceania"}


def src_info(p):
    m = M[p]
    al = m.get("authorList", {}).get("author", [])
    aff = ""
    for a in al:
        d = a.get("authorAffiliationDetailsList", {}).get("authorAffiliation", [])
        if d and d[0].get("affiliation"):
            aff = d[0]["affiliation"]
            break
        if a.get("affiliation"):
            aff = a["affiliation"]
            break
    aff = aff or m.get("affiliation") or ""
    tail = aff.rstrip(". ").split(",")[-1].strip()
    tail = re.sub(r"\.\s*\S+@\S+$", "", tail).strip()
    tail = tail.split(".")[0].strip()
    country = COUNTRY.get(tail)
    if country is None:
        for k, v in COUNTRY.items():
            if k in aff.split()[-1:] or aff.rstrip(".").endswith(k):
                country = v
                break
    if country is None:
        country = {"PMC13093780": "Ethiopia", "PMC6230673": "Japan"}.get(p, "?")
    return dict(year=int(m.get("pubYear") or 0),
                journal=m.get("journalInfo", {}).get("journal", {}).get("title", "?"),
                country=country, region=REGION.get(country, "?"), aff=aff[:90])


rows = []
for c in C:
    d = c["part2_yes_no"].get("demographics") or {}
    age = d.get("age")
    age_n = age if isinstance(age, (int, float)) else (67 if isinstance(age, str) and "67" in age else None)
    sex = (d.get("sex") or "").split(" ")[0]
    sex = sex if sex in ("male", "female") else "not stated"
    s = src_info(c["source"]["pmcid"])
    rows.append(dict(video=c["video"], line=c["line"], dx=c["true_diagnosis"], pmc=c["source"]["pmcid"],
                     age=age_n, age_raw=age, sex=sex, **s))

P = lambda t: print(t)
P("=" * 78)
P("CASES %d   SOURCE ARTICLES %d" % (len(rows), len({r["pmc"] for r in rows})))
cnt = collections.Counter(r["pmc"] for r in rows)
P("sources contributing 1 case: %d, 2 cases: %d, 3 cases: %d" % tuple(
    sum(1 for v in cnt.values() if v == k) for k in (1, 2, 3)))
for p, n in cnt.items():
    if n > 1:
        P("  %s (%d cases):" % (p, n))
        for r in rows:
            if r["pmc"] == p:
                P("     %-48s %s %s | %s" % (r["video"][:48], r["age_raw"], r["sex"], r["dx"][:70]))

P("\nAGE  numeric n=%d, adult-unstated %d" % (sum(1 for r in rows if r["age"] is not None),
                                              sum(1 for r in rows if r["age"] is None)))
ages = sorted(r["age"] for r in rows if r["age"] is not None)
P("  median %.0f  IQR %d-%d  range %d-%d" % (ages[len(ages) // 2], ages[len(ages) // 4],
                                               ages[3 * len(ages) // 4], ages[0], ages[-1]))
bins = [("<18 (paediatric)", lambda a: a < 18), ("18-39", lambda a: 18 <= a < 40),
        ("40-59", lambda a: 40 <= a < 60), ("60-74", lambda a: 60 <= a < 75), (">=75", lambda a: a >= 75)]
for lab, f in bins:
    P("  %-18s %2d" % (lab, sum(1 for a in ages if f(a))))
P("  paediatric cases: %s" % [(r["video"][:40], r["age"]) for r in rows if r["age"] is not None and r["age"] < 18])
P("\nSEX  %s" % dict(collections.Counter(r["sex"] for r in rows)))
P("  (sex read off the video rather than stated in text: %d)" % sum(
    1 for c in C if "apparent" in str((c["part2_yes_no"].get("demographics") or {}).get("sex", ""))))

P("\nPUBLICATION YEAR (sources)")
yc = collections.Counter(src_info(p)["year"] for p in cnt)
for y in sorted(yc):
    P("  %d: %d" % (y, yc[y]))
P("\nJOURNALS (sources)")
for j, n in collections.Counter(src_info(p)["journal"] for p in cnt).most_common():
    P("  %2d  %s" % (n, j))
P("\nCOUNTRY of first affiliation (sources / cases)")
sc = collections.Counter(src_info(p)["country"] for p in cnt)
cc = collections.Counter(r["country"] for r in rows)
for k, n in sc.most_common():
    P("  %-16s %2d / %2d" % (k, n, cc[k]))
P("REGION (cases)")
for k, n in collections.Counter(r["region"] for r in rows).most_common():
    P("  %-16s %2d" % (k, n))
P("\nDIAGNOSIS LABELS by line (true_diagnosis, abridged)")
for line in sorted({r["line"] for r in rows}):
    P("  [%s]" % line)
    for r in rows:
        if r["line"] == line:
            P("     - %s" % re.split(r"[;(]| which | with | from | in a | in an | after ", r["dx"])[0].strip()[:80])

# ---------------- performance by subgroup and clustered bootstrap -----------------------
MODELS = [("GPT-5.6-luna", "part2_lunathink_vid_doctor"), ("Gemma-4-31B", "part2_gemmathink_vid_doctor"),
          ("MiMo-v2.5", "part2_mimothink_vid_doctor"), ("MiniMax-M3", "part2_minimaxthink_vid_doctor"),
          ("Qwen3.8-flash", "part2_qwen38_vid_doctor")]
grades = {}
for nm, t in MODELS:
    g = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/fulljudge_%s.json" % t))
    grades[nm] = {v: 1.0 if d.get("grade") == "exact" else 0.0 for v, d in g.items()}
H = B + "/human_study/"
cl = {}
for n in ("2", "3"):
    for d in json.load(open(H + "doctor_graded%s.json" % n)).values():
        cl[d["video"]] = 1.0 if d.get("grade") == "exact" else 0.0
grades["Clinician"] = cl
vids = [r["video"] for r in rows]
byv = {r["video"]: r for r in rows}


def acc(g, sub):
    return 100.0 * sum(g.get(v, 0.0) for v in sub) / len(sub) if sub else float("nan")


P("\nEXACT (%) in the video condition by subgroup (denominator = cases in subgroup, missing = wrong)")
groups = [("all", lambda r: True),
          ("male", lambda r: r["sex"] == "male"), ("female", lambda r: r["sex"] == "female"),
          ("age <18", lambda r: r["age"] is not None and r["age"] < 18),
          ("age 18-59", lambda r: r["age"] is not None and 18 <= r["age"] < 60),
          ("age >=60", lambda r: r["age"] is not None and r["age"] >= 60),
          ("East Asia", lambda r: r["region"] == "East Asia"),
          ("South/SE Asia", lambda r: r["region"] == "South/SE Asia"),
          ("Europe", lambda r: r["region"] == "Europe"),
          ("North America", lambda r: r["region"] == "North America"),
          ("other regions", lambda r: r["region"] in ("Africa", "Middle East", "Latin America", "Oceania")),
          ("published <=2022", lambda r: r["year"] <= 2022),
          ("published 2023-24", lambda r: 2023 <= r["year"] <= 2024),
          ("published 2025-26", lambda r: r["year"] >= 2025),
          ("single-case source", lambda r: cnt[r["pmc"]] == 1),
          ("multi-case source", lambda r: cnt[r["pmc"]] > 1)]
hdr = "%-20s %3s " % ("subgroup", "n") + " ".join("%13s" % k[:13] for k in grades)
P(hdr)
for lab, f in groups:
    sub = [v for v in vids if f(byv[v])]
    P("%-20s %3d " % (lab, len(sub)) + " ".join("%13.1f" % acc(g, sub) for g in grades.values()))


def boot(g, n=10000, seed=0, cluster=False):
    r = random.Random(seed)
    if cluster:
        clus = collections.defaultdict(list)
        for v in vids:
            clus[byv[v]["pmc"]].append(v)
        keys = list(clus)
    xs = []
    for _ in range(n):
        if cluster:
            s = [v for _ in keys for v in clus[keys[r.randrange(len(keys))]]]
        else:
            s = [vids[r.randrange(len(vids))] for _ in vids]
        xs.append(100.0 * sum(g.get(v, 0.0) for v in s) / len(s))
    xs.sort()
    return xs[int(.025 * n)], xs[int(.975 * n)]


P("\nVIDEO-CONDITION EXACT: case-level vs source-clustered 95%% bootstrap (10,000 resamples)")
P("%-14s %6s %18s %18s %8s" % ("system", "point", "by case", "by source (66)", "width x"))
for nm, g in grades.items():
    pt = acc(g, vids)
    a = boot(g)
    b = boot(g, cluster=True)
    P("%-14s %6.1f  [%5.1f, %5.1f]    [%5.1f, %5.1f]  %6.2f" % (nm, pt, a[0], a[1], b[0], b[1],
                                                                 (b[1] - b[0]) / (a[1] - a[0])))
# paired video - blind where a blind grading exists
for nm, vt, bt in (("GPT-5.6-luna", "part2_lunathink_vid_doctor", "part2_lunathink_novid_doctor"),
                   ("Qwen3.8-flash", "part2_qwen38_vid_doctor", "part2_qwen38_novid_doctor")):
    gv = grades[nm]
    gb = {v: 1.0 if d.get("grade") == "exact" else 0.0 for v, d in json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/fulljudge_%s.json" % bt)).items()}
    diff = {v: gv.get(v, 0.0) - gb.get(v, 0.0) for v in vids}
    a = boot(diff)
    b = boot(diff, cluster=True)
    P("%-14s video-blind %+5.1f  by case [%+5.1f, %+5.1f]  by source [%+5.1f, %+5.1f]" % (
        nm, 100.0 * sum(diff.values()) / len(vids), a[0], a[1], b[0], b[1]))

json.dump(rows, open(os.environ.get("DDX_WORK", "/tmp") + "/dataset_rows.json", "w"), indent=1, ensure_ascii=False)
