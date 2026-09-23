"""Shared builder: a per-line list of test names plus per-case results from the source article.

The line panel names the investigations a doctor might order for that presentation and the tier
each belongs to; it carries no values. A case's chart holds only what its own article reports
(p = "reported"), with the tests that decided the diagnosis flagged decisive. Anything else the
doctor orders returns "not performed / not available": the benchmark never supplies a result the
source did not record.
"""
import json
import re

# A therapeutic trial is an intervention, not a specimen. It costs the patient days to weeks and
# carries its own risk, and in 20 of the 71 cases it is the decisive evidence - so a doctor who
# can fire off "run the treatment trials" gets the answer for free. These entries are marked
# explicit_only: the harness returns them ONLY when the doctor names that specific trial, never
# in response to a blanket or category-level request.
_TRIAL = re.compile(r"\btrial\b|\bchallenge\b", re.I)

ANSWERING_RULE = ("Answer yes, no, or unknown. Use symptom_table: yes when it documents the feature "
                  "as present, no when it documents the feature as absent, unknown when the feature "
                  "is not listed or the documented features do not settle the whole question. A "
                  "feature absent from the table is unreported, never NO.")
EXPLICIT_ONLY_RULE = ("Entries flagged explicit_only are therapeutic trials, not tests. Return one "
                      "only when the doctor names that specific trial. A blanket or category-level "
                      "request ('try treatment', 'run the trials', 'give something and see') "
                      "returns nothing.")
FIELDS = ("v value | p reported=read from the source article | tier bedside<blood<imaging<invasive "
          "| decisive=confirms or excludes | explicit_only=must be named individually")


def build(line, panel, cases, out=None, explicit_only_rule=None):
    built = []
    for c in cases:
        bad = [k for k, v in c["inv"].items() if v.get("p") != "reported"]
        assert not bad, "%s: entries not read from the source: %s" % (c["video"], bad)
        # panel order first, so a line's charts list shared tests in the same order
        keys = [k for k in panel if k in c["inv"]] + [k for k in c["inv"] if k not in panel]
        inv = {}
        for k in keys:
            e = dict(c["inv"][k])
            e.setdefault("tier", panel.get(k, {}).get("tier", "blood"))
            if _TRIAL.search(k):
                e["explicit_only"] = True
            inv[k] = e
        assert any(v.get("decisive") for v in inv.values()), "%s: no decisive entry" % c["video"]
        table = {s: "yes" for s in c["yes"]}
        table.update({s: "no" for s in c["no"]})
        built.append(dict(
            video=c["video"], line=line, source={"pmcid": c["pmcid"]},
            true_diagnosis=c["dx"],
            part1_video_only=dict(task="name the primary disease from the frames alone",
                                  visible_sign=c["sign"], accept_as_correct=c["correct"],
                                  accept_as_partial=c["partial"]),
            part2_yes_no=dict(
                answering_rule=ANSWERING_RULE,
                demographics=c["who"], symptom_table=table),
            investigation_rules=dict(
                default_for_unlisted="not performed / not available",
                explicit_only=explicit_only_rule or EXPLICIT_ONLY_RULE,
                fields=FIELDS),
            investigations=inv,
            scoring=dict(treatable_dont_miss=c["dont_miss"],
                         must_not_conclude=c["must_not"])))
    path = out or ("cases_%s.json" % line)
    json.dump(built, open(path, "w"), indent=1, ensure_ascii=False)
    for c in built:
        inv = c["investigations"]
        print("%-52s inv=%-3d reported=%-3d decisive=%d  yes/no=%d/%d"
              % (c["video"][:52], len(inv),
                 sum(1 for v in inv.values() if v["p"] == "reported"),
                 sum(1 for v in inv.values() if v.get("decisive")),
                 sum(1 for v in c["part2_yes_no"]["symptom_table"].values() if v == "yes"),
                 sum(1 for v in c["part2_yes_no"]["symptom_table"].values() if v == "no")))
    print("wrote %s (%d cases, %d reported entries)"
          % (path, len(built), sum(len(c["investigations"]) for c in built)))
    return built
