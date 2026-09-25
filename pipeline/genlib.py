"""Shared builder: a per-line investigation panel plus per-case overrides.

Every case in a line offers the same menu, so what a doctor chooses to order is comparable
across cases; each case then overrides the entries its own article reports and marks the ones
that decide the diagnosis.

The menu must be IDENTICAL across a line, and that is enforced here rather than trusted to the
per-line files. An audit on 2026-07-31 found 42 investigations that existed on exactly one case
of their line, 20 of them flagged decisive - "empirical IV thiamine trial" on the Wernicke case,
"serotonin syndrome criteria (Hunter)" on the serotonin-syndrome case, "HLA-B51 and Behcet's
assessment" on the Behcet case. A model that never looked at the patient could shortlist the
diagnosis from the menu alone. Any key a case overrides is now promoted into the line's panel,
with a neutral value on the siblings, so ordering a test is informative only after it is ordered.
"""
import json
import os
import re

_HISTORY = re.compile(r"history|clinical course|course /|follow.?up", re.I)
_TRIAL = re.compile(r"\btrial\b|\bchallenge\b", re.I)


def _is_trial(key):
    """A therapeutic trial is an intervention the doctor gives the patient.

    Matching on the words trial/challenge alone over-fires: "clinical course",
    "tuberculosis treatment history" and the functional-sign entry "suggestibility / sham stimulus
    (tuning fork or vibration applied as 'treatment')" are history or bedside examination, not
    interventions, and flagging them would let the harness withhold a plain history question.
    """
    return bool(_TRIAL.search(key)) and not _HISTORY.search(key)


def _neutral(key, tier):
    """What a sibling case returns for a test it never had."""
    if _HISTORY.search(key):
        return "not recorded"
    if _is_trial(key):
        return "not tried"
    if tier in ("imaging", "invasive"):
        return "not performed"
    return "normal / non-contributory"

# A therapeutic trial is an intervention, not a specimen. It costs the patient days to weeks and
# carries its own risk, and in 21 of the 71 cases it is the decisive evidence - so a doctor who
# can fire off "run the treatment trials" gets the answer for free. These entries are marked
# explicit_only: the harness returns them ONLY when the doctor names that specific trial, never
# in response to a blanket or category-level request.



_GENERIC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "generic_panel.json")))["entries"]
_GVALS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "generic_values.json")))
_GDROP = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "generic_drop.json")))


def generic_panel(line=None):
    """The tests doctors order unprompted that no line menu carried.

    Measured on 140 free-text investigation lists: 54-57% of the atomic tests requested matched no
    menu entry, so under the old rule they came back "normal / non-contributory". That is not a
    gap the doctor notices - it is a reassuring result they are told, and it falls hardest on the
    doctor who works up the differential properly. These entries are added to EVERY line, so they
    cannot tell one case from another.
    """
    skip = set(_GDROP.get(line or "", []))       # this line already has that test
    return {k: {"v": "normal", "p": "derived", "tier": t}
            for k, t in _GENERIC.items() if k not in skip}


def apply_generic(video, inv):
    """Per-case values for the generic entries; the case's own reported findings still win."""
    for k, v in (_GVALS.get(video) or {}).items():
        if k in _GENERIC and k not in inv:
            inv[k] = {"v": v, "p": "derived", "tier": _GENERIC[k]}
    return inv


def build(line, panel, cases, out=None):
    panel = dict(generic_panel(line), **dict(panel))
    for c in cases:                       # promote every override key into the shared menu
        for k, v in c["inv"].items():
            if k not in panel:
                tier = v.get("tier", "blood")
                panel[k] = {"v": _neutral(k, tier), "p": "derived", "tier": tier}
    for k in panel:
        if _is_trial(k):
            panel[k]["explicit_only"] = True
    built = []
    for c in cases:
        inv = {k: dict(v) for k, v in panel.items()}
        for k, v in (_GVALS.get(c["video"]) or {}).items():
            if k in panel and k in _GENERIC and k not in c["inv"]:
                inv[k] = {"v": v, "p": "derived", "tier": _GENERIC[k]}
        for k, v in c["inv"].items():
            base = inv.get(k, {"tier": v.get("tier", "blood")})
            base.update(v)
            base.setdefault("tier", "blood")
            if _TRIAL.search(k):
                base["explicit_only"] = True
            inv[k] = base
        table = {s: "yes" for s in c["yes"]}
        table.update({s: "no" for s in c["no"]})
        built.append(dict(
            video=c["video"], line=line, source={"pmcid": c["pmcid"]},
            true_diagnosis=c["dx"],
            part1_video_only=dict(task="name the primary disease from the frames alone",
                                  visible_sign=c["sign"], accept_as_correct=c["correct"],
                                  accept_as_partial=c["partial"],
                                  accept_as_coverage=c["correct"],
                                  related_but_not_covered=c["partial"]),
            final_diagnosis=dict(accept_as_accurate=c["correct"], accept_as_partial=c["partial"]),
            part2_yes_no=dict(
                answering_rule="Answer yes, no, or unknown. Use symptom_table: yes when it "
                               "documents the feature as present, no when it documents the "
                               "feature as absent, unknown when the feature is not listed or the "
                               "documented features do not settle the whole question. A feature "
                               "absent from the table is unreported, never NO.",
                demographics=c["who"], symptom_table=table),
            investigation_rules=dict(
                default_for_unlisted="not performed / not available",
                explicit_only="Entries flagged explicit_only are therapeutic trials, not tests. "
                              "Return one only when the doctor names that specific trial. A "
                              "blanket or category-level request ('try treatment', 'run the "
                              "trials', 'give something and see') returns nothing.",
                fields="v value | p reported=from the source article, derived=expected for this "
                       "presentation | tier bedside<blood<imaging<invasive | decisive=confirms "
                       "or excludes | explicit_only=must be named individually"),
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
    menus = {frozenset(c["investigations"]) for c in built}
    assert len(menus) == 1, ("%s: menu differs across cases, %d variants" % (line, len(menus)))
    print("wrote %s (%d cases, identical %d-item menu)" % (path, len(built), len(panel)))
    return built
