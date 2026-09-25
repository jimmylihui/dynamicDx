"""Build the ataxia cases on documented aetiologies.

Two layers. The line panel is the menu every ataxia case offers, so ordering behaviour is
comparable across cases; its entries carry the result a patient with this presentation would
normally have. Each case then overrides the entries its own article reports, and flags the ones
that actually decide the diagnosis.

Provenance is explicit: "reported" means the value appears in the source article, "derived" means
it is the expected result for this presentation and was not measured in that paper.
"""
import json
import os
import re

LINE = "ataxia"

PANEL = {
    "gait examination": {"v": "wide-based, unsteady gait", "p": "derived", "tier": "bedside"},
    "finger-nose / heel-shin testing": {"v": "dysmetria", "p": "derived", "tier": "bedside"},
    "Romberg test": {"v": "negative - swaying is not worse with the eyes closed",
                     "p": "derived", "tier": "bedside"},
    "bedside eye-movement exam": {"v": "normal", "p": "derived", "tier": "bedside"},
    "SARA score": {"v": "not recorded", "p": "derived", "tier": "bedside"},
    "vital signs": {"v": "normal, afebrile", "p": "derived", "tier": "bedside"},
    "full blood count": {"v": "normal", "p": "derived", "tier": "blood"},
    "renal and liver function": {"v": "normal", "p": "derived", "tier": "blood"},
    "electrolytes (Na, K, Ca, Mg)": {"v": "normal", "p": "derived", "tier": "blood"},
    "glucose / HbA1c": {"v": "normal", "p": "derived", "tier": "blood"},
    "TSH / free T4": {"v": "normal", "p": "derived", "tier": "blood"},
    "vitamin B12 / folate": {"v": "normal", "p": "derived", "tier": "blood"},
    "vitamin E": {"v": "normal", "p": "derived", "tier": "blood"},
    "serum thiamine (vitamin B1)": {"v": "normal", "p": "derived", "tier": "blood"},
    "copper / caeruloplasmin": {"v": "normal - excludes Wilson disease", "p": "derived",
                                "tier": "blood"},
    "serum lithium and drug levels": {"v": "not detected", "p": "derived", "tier": "blood"},
    "alcohol history / GGT / CDT": {"v": "no alcohol excess; markers normal", "p": "derived",
                                    "tier": "blood"},
    "ESR / CRP": {"v": "normal", "p": "derived", "tier": "blood"},
    "coeliac serology (anti-TTG)": {"v": "negative", "p": "derived", "tier": "blood"},
    "paraneoplastic antibody panel (serum)": {"v": "negative", "p": "derived", "tier": "blood"},
    "anti-GQ1b / anti-ganglioside antibodies": {"v": "negative", "p": "derived", "tier": "blood"},
    "anti-GAD antibodies": {"v": "negative", "p": "derived", "tier": "blood"},
    "HIV / syphilis serology": {"v": "negative", "p": "derived", "tier": "blood"},
    "genetic ataxia panel": {"v": "no pathogenic repeat expansion or variant", "p": "derived",
                             "tier": "blood"},
    "brain MRI": {"v": "no cerebellar atrophy, no focal lesion", "p": "derived",
                  "tier": "imaging"},
    "MR angiography (posterior circulation)": {"v": "normal", "p": "derived", "tier": "imaging"},
    "CT chest / abdomen / pelvis (occult tumour)": {"v": "no malignancy", "p": "derived",
                                                   "tier": "imaging"},
    "FDG-PET (occult tumour)": {"v": "no hypermetabolic lesion", "p": "derived",
                                "tier": "imaging"},
    "lumbar puncture / CSF": {"v": "normal cells, protein and glucose; no oligoclonal bands",
                              "p": "derived", "tier": "invasive"},
    "nerve conduction studies / EMG": {"v": "normal", "p": "derived", "tier": "invasive"},
    "EEG": {"v": "normal", "p": "derived", "tier": "invasive"},
    "somatosensory evoked potentials": {"v": "normal", "p": "derived", "tier": "invasive"},
}

CASES = [
 dict(
  video="mild_sca_genetic_PMC12678565.mp4", pmcid="PMC12678565",
  dx="Spinocerebellar ataxia type 8 (ATXN8OS CTG expansion), which had been preceded for years "
     "by a functional gait disorder",
  sign="unsteady, wide-based walking",
  correct=["spinocerebellar ataxia", "SCA8", "hereditary/genetic cerebellar ataxia"],
  partial=["cerebellar ataxia", "degenerative ataxia", "functional gait disorder"],
  who=dict(age=59, sex="female"),
  yes=["unsteady walking", "slurred speech that came on years after the walking problem",
       "the walking problem improved with intensive physiotherapy",
       "walking looks better when distracted", "symptoms have progressed slowly over years",
       "a relative with a similar walking problem"],
  no=["sudden onset", "double vision", "recent infection", "heavy alcohol use",
      "numbness or tingling", "headache", "weakness of the limbs", "any recent new medication",
      "cancer", "fever"],
  inv={
   "genetic ataxia panel": {"v": "112 and 29 CTG repeats in ATXN8OS - confirms SCA8",
                            "p": "reported", "decisive": True},
   "brain MRI": {"v": "cerebellar atrophy on sagittal T1 and axial FLAIR", "p": "reported",
                 "decisive": True},
   "SARA score": {"v": "0 at first assessment; cerebellar dysarthria appeared at age 59",
                  "p": "reported"},
   "Simplified Functional Movement Disorders Rating Scale (S-FMDRS)":
       {"v": "3 - mild gait disturbance that normalises with distraction", "p": "reported",
        "tier": "bedside", "decisive": True},
   "trial of intensive physiotherapy for functional gait disorder":
       {"v": "walking improved significantly", "p": "reported", "tier": "bedside"},
  },
  dont_miss="A functional gait disorder and a degenerative ataxia can coexist; improvement with "
            "distraction or physiotherapy does not exclude a genetic ataxia, so send the panel "
            "when cerebellar signs appear.",
  must_not="calling it purely functional and stopping - the SCA8 expansion is the answer"),

 dict(
  video="moderate_checkpoint_drug_PMC11585521.mp4", pmcid="PMC11585521",
  dx="Immune checkpoint inhibitor-related cerebellar toxicity (anti-PD-L1) - a neurological "
     "immune-related adverse event",
  sign="truncal and gait ataxia with limb dysmetria",
  correct=["immune checkpoint inhibitor cerebellar toxicity",
           "immune-related adverse event", "autoimmune/immune-mediated cerebellitis"],
  partial=["cerebellar ataxia", "paraneoplastic cerebellar degeneration",
           "autoimmune cerebellar ataxia"],
  who=dict(age=71, sex="female"),
  yes=["unsteady walking", "slurred speech", "falling backwards",
       "clumsy hands", "being treated for cancer",
       "started a new cancer immunotherapy in the last year",
       "joint pain that started after the cancer treatment",
       "a low sodium episode after the cancer treatment",
       "symptoms got worse over about two months", "now uses a wheelchair"],
  no=["heavy alcohol use", "recent infection", "fever", "headache", "double vision",
      "family history of ataxia", "numbness or tingling", "seizures", "sudden onset"],
  inv={
   "lumbar puncture / CSF": {"v": "normal protein and cellularity but CSF-restricted oligoclonal "
                                  "bands present - inflammatory", "p": "reported",
                             "decisive": True},
   "medication and oncology history": {"v": "anti-PD-L1 for HPV-related anal squamous cell "
                                            "carcinoma; ankle arthritis at 2 months and grade 3 "
                                            "hyponatraemia at 7 months, both irAEs",
                                       "p": "reported", "tier": "bedside", "decisive": True},
   "paraneoplastic antibody panel (serum)": {"v": "negative in this patient (neuronal antibodies "
                                                 "are found in only about half of such cases)",
                                             "p": "reported"},
   "brain MRI": {"v": "no structural lesion; cerebellar atrophy develops later", "p": "derived"},
   "CT chest / abdomen / pelvis (occult tumour)": {"v": "known anal squamous cell carcinoma; no "
                                                        "new lesion", "p": "reported"},
  },
  dont_miss="Stop the checkpoint inhibitor and start immunotherapy early - the deficit becomes "
            "fixed, and this patient was wheelchair-bound at four years.",
  must_not="attributing it to the cancer itself as paraneoplastic degeneration and continuing "
           "the checkpoint inhibitor"),

 dict(
  video="moderate_ms_demyelinating_PMC13085407.mp4", pmcid="PMC13085407",
  dx="Persistent cerebellar dysfunction after acute lithium toxicity (SILENT-type syndrome), "
     "with progressive isolated cerebellar atrophy",
  sign="unsteady, wide-based gait",
  correct=["lithium toxicity", "lithium-induced cerebellar syndrome", "drug/toxic ataxia"],
  partial=["toxic cerebellar degeneration", "acquired cerebellar ataxia"],
  who=dict(age=38, sex="male"),
  yes=["unsteady walking", "slurred speech",
       "an episode of reduced consciousness needing hospital admission",
       "the ataxia started right after that episode and never went away",
       "an accidental overdose of a medicine",
       "symptoms have been present for about five years", "previously completely healthy"],
  no=["heavy alcohol use", "a psychiatric illness", "being prescribed lithium",
      "family history of ataxia", "recent infection", "cancer", "double vision",
      "numbness or tingling", "headache", "fever", "gradual onset over years"],
  inv={
   "serum lithium and drug levels": {"v": "serum lithium 4.07 mmol/L on admission; CSF lithium "
                                          "2.45 mmol/L; later fell below 0.2 mmol/L",
                                     "p": "reported", "decisive": True},
   "brain MRI": {"v": "cerebellar atrophy at one year; serial imaging over five years shows "
                      "progressive ISOLATED cerebellar atrophy with no supratentorial "
                      "abnormality", "p": "reported", "decisive": True},
   "medication history": {"v": "no prior lithium use and no psychiatric indication - the exposure "
                               "was accidental", "p": "reported", "tier": "bedside",
                          "decisive": True},
   "creatine kinase": {"v": "raised during the acute episode (neuroleptic-malignant-like "
                            "syndrome)", "p": "reported", "tier": "blood"},
  },
  dont_miss="Take a drug-exposure history in any acute encephalopathy with later cerebellar "
            "signs; lithium neurotoxicity can be permanent even after levels normalise.",
  must_not="calling it multiple sclerosis or a demyelinating ataxia - imaging shows isolated "
           "cerebellar atrophy with no demyelinating lesions"),

 dict(
  video="moderate_postinfectious_millerfisher_PMC13224678.mp4", pmcid="PMC13224678",
  dx="Post-infectious (COVID-19) myoclonus-ataxia syndrome of subcortical origin",
  sign="unsteady wide-based gait with jerky limb movements",
  correct=["post-infectious myoclonus-ataxia syndrome", "COVID-19 related myoclonus-ataxia",
           "para-infectious cerebellar syndrome"],
  partial=["opsoclonus-myoclonus syndrome", "cerebellar ataxia", "Miller Fisher syndrome"],
  who=dict(age=52, sex="female"),
  yes=["unsteady walking", "jerky involuntary movements of the arms", "slurred speech",
       "shaky eye movements", "a fever about two weeks before the movements started",
       "widespread body aches at the time of the fever",
       "the movements got much worse within a few days",
       "the movements have almost completely gone now"],
  no=["heavy alcohol use", "cancer", "family history of a similar illness",
      "a new medication before the symptoms", "headache", "limb weakness", "double vision",
      "numbness or tingling", "gradual onset over months"],
  inv={
   "nerve conduction studies / EMG": {"v": "rhythmic bursts in both hands, synchronised with the "
                                           "visible jerks", "p": "reported", "decisive": True},
   "somatosensory evoked potentials": {"v": "NO giant SSEP - argues against a cortical origin",
                                       "p": "reported", "decisive": True},
   "EEG": {"v": "no abnormality, and no EEG-EMG correlation on video-EEG - the myoclonus is "
                "subcortical", "p": "reported", "decisive": True},
   "SARS-CoV-2 testing": {"v": "recent COVID-19 infection", "p": "reported", "tier": "blood",
                          "decisive": True},
   "CT chest": {"v": "no notable abnormality", "p": "reported", "tier": "imaging"},
   "clinical course / follow-up": {"v": "about 90% improvement at two months, medication free",
                                   "p": "reported", "tier": "bedside"},
  },
  dont_miss="Localise the myoclonus before treating: absent giant SSEP and no EEG-EMG "
            "correlation put it below the cortex, which changes the drug choice and the "
            "prognosis - this syndrome recovers.",
  must_not="labelling it Miller Fisher syndrome; there is no ophthalmoplegia-areflexia-ataxia "
           "triad and the anti-GQ1b antibody is not the finding here"),

 dict(
  video="severe_paraneoplastic_PMC12741441.mp4", pmcid="PMC12741441",
  dx="Anti-Ri (ANNA-2) paraneoplastic progressive supranuclear palsy-like syndrome, with no "
     "tumour found despite extensive search",
  sign="severe postural instability with a tendency to fall backwards; restricted eye movements",
  correct=["anti-Ri paraneoplastic syndrome", "paraneoplastic PSP-like syndrome",
           "autoimmune/paraneoplastic parkinsonism"],
  partial=["progressive supranuclear palsy", "atypical parkinsonism",
           "paraneoplastic cerebellar degeneration"],
  who=dict(age=39, sex="male"),
  yes=["falling backwards", "difficulty looking down", "difficulty moving the eyes",
       "stiffness and slowness", "the problem has progressed rapidly over about 18 months",
       "being unusually young for this kind of problem",
       "having had surgery to look for a hidden cancer"],
  no=["a resting tremor", "heavy alcohol use", "family history of a similar illness",
      "recent infection", "fever", "a known cancer", "headache", "numbness or tingling",
      "sudden onset", "improvement with levodopa"],
  inv={
   "paraneoplastic antibody panel (serum)": {"v": "anti-Ri (ANNA-2) POSITIVE", "p": "reported",
                                             "decisive": True},
   "bedside eye-movement exam": {"v": "vertical gaze palsy progressing to complete external "
                                      "ophthalmoplegia", "p": "reported", "decisive": True},
   "FDG-PET (occult tumour)": {"v": "suspicious thymic and testicular sites; both were removed "
                                    "surgically and NO tumour was found", "p": "reported"},
   "CT chest / abdomen / pelvis (occult tumour)": {"v": "no tumour identified", "p": "reported"},
   "levodopa trial": {"v": "no meaningful response", "p": "derived", "tier": "bedside"},
   "brain MRI": {"v": "no structural lesion accounting for the syndrome", "p": "derived"},
  },
  dont_miss="Rapidly progressive PSP-like disease in a young patient is paraneoplastic until "
            "proven otherwise - send anti-Ri and hunt for a tumour; immunotherapy is the "
            "treatable part.",
  must_not="diagnosing idiopathic progressive supranuclear palsy, which would close off the "
           "antibody testing and the tumour search"),

 dict(
  video="severe_wernicke_PMC13008232.mp4", pmcid="PMC13008232",
  dx="Wernicke encephalopathy from thiamine deficiency in a haemodialysis patient; recurrent, "
     "having relapsed when thiamine was stopped",
  sign="wide-based unsteady gait",
  correct=["Wernicke encephalopathy", "thiamine deficiency", "vitamin B1 deficiency"],
  partial=["nutritional/metabolic ataxia", "acquired cerebellar ataxia", "uraemic encephalopathy"],
  who=dict(age=53, sex="male"),
  yes=["unsteady walking", "slurred speech", "memory problems",
       "symptoms came back after a supplement was stopped", "regular haemodialysis",
       "kidney failure", "eating much less than usual",
       "losing more than 10 kg in three months", "high blood pressure"],
  no=["heavy alcohol use", "double vision", "eye movement problems", "fever", "headache",
      "limb weakness", "seizures", "family history of a similar illness", "recent head injury",
      "cancer"],
  inv={
   "serum thiamine (vitamin B1)": {"v": "0.97 ng/mL (reference 1.7-10) - LOW; 2539.27 ng/mL after "
                                        "supplementation, 2.24 ng/mL on maintenance",
                                   "p": "reported", "decisive": True},
   "brain MRI": {"v": "bilateral symmetric hyperintensity in the mammillary bodies, thalami and "
                      "periaqueductal midbrain, with the LENTIFORM FORK SIGN; reversed after "
                      "treatment", "p": "reported", "decisive": True},
   "empirical IV thiamine trial": {"v": "marked clinical and radiological improvement",
                                   "p": "reported", "tier": "bedside", "decisive": True},
   "bedside eye-movement exam": {"v": "no ophthalmoplegia and no nystagmus - the classic triad is "
                                      "incomplete", "p": "reported"},
   "MMSE": {"v": "23, cutoff 21 for his education - mild cognitive impairment", "p": "reported",
            "tier": "bedside"},
   "alcohol history / GGT / CDT": {"v": "explicitly NO history of alcoholism", "p": "reported"},
   "renal and liver function": {"v": "end-stage renal disease on maintenance haemodialysis",
                                "p": "reported"},
   "glucose / HbA1c": {"v": "HbA1c 5.9% (reference 4.0-6.0) - normal", "p": "reported"},
  },
  dont_miss="Give thiamine before glucose and do not wait for the level; dialysis and poor "
            "intake cause Wernicke without any alcohol, and it recurs if supplementation stops.",
  must_not="assuming alcoholic Wernicke, or excluding the diagnosis because there is no "
           "ophthalmoplegia - the triad is complete in a minority of patients"),
]


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

# Promote every key any case overrides into the shared menu, so the menu itself cannot identify
# the case. Written out here rather than imported because this file predates genlib.
_GENERIC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "generic_panel.json")))["entries"]
_GVALS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "generic_values.json")))
_GDROP = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "generic_drop.json"))).get(LINE, []))
for _k, _t in _GENERIC.items():
    if _k not in _GDROP:                          # this line already has that test
        PANEL.setdefault(_k, {"v": "normal", "p": "derived", "tier": _t})

for _c in CASES:
    for _k, _v in _c["inv"].items():
        if _k not in PANEL:
            _t = _v.get("tier", "blood")
            PANEL[_k] = {"v": _neutral(_k, _t), "p": "derived", "tier": _t}
for _k in PANEL:
    if _is_trial(_k):
        PANEL[_k]["explicit_only"] = True


def build(c):
    inv = {k: dict(v) for k, v in PANEL.items()}
    for k, v in (_GVALS.get(c["video"]) or {}).items():
        if k in PANEL and k in _GENERIC and k not in c["inv"]:
            inv[k] = {"v": v, "p": "derived", "tier": _GENERIC[k]}
    for k, v in c["inv"].items():
        base = inv.get(k, {"tier": v.get("tier", "blood")})
        base.update(v)
        base.setdefault("tier", "blood")
        if _is_trial(k):
            base["explicit_only"] = True
        inv[k] = base
    table = {s: "yes" for s in c["yes"]}
    table.update({s: "no" for s in c["no"]})
    return dict(
        video=c["video"], line=LINE,
        source={"pmcid": c["pmcid"]},
        true_diagnosis=c["dx"],
        part1_video_only=dict(task="name the primary disease from the frames alone",
                              visible_sign=c["sign"],
                              accept_as_correct=c["correct"],
                              accept_as_partial=c["partial"]),
        part2_yes_no=dict(
            answering_rule="Answer strictly yes or no. Use symptom_table; any feature not listed "
                           "is answered NO.",
            demographics=c["who"], symptom_table=table),
        investigation_rules=dict(
            default_for_unlisted="not performed / not available",
            explicit_only="Entries flagged explicit_only are therapeutic trials, not tests. "
                          "Return one only when the doctor names that specific trial. A blanket "
                          "or category-level request returns nothing.",
            fields="v value | p reported=from the source article, derived=expected for this "
                   "presentation | tier bedside<blood<imaging<invasive | decisive=confirms or "
                   "excludes | explicit_only=must be named individually"),
        investigations=inv,
        scoring=dict(treatable_dont_miss=c["dont_miss"], must_not_conclude=c["must_not"]))


out = [build(c) for c in CASES]
json.dump(out, open("cases_%s.json" % LINE, "w"), indent=1, ensure_ascii=False)
for c in out:
    inv = c["investigations"]
    print("%-52s inv=%-3d reported=%-3d decisive=%d  yes/no=%d/%d"
          % (c["video"][:52], len(inv),
             sum(1 for v in inv.values() if v["p"] == "reported"),
             sum(1 for v in inv.values() if v.get("decisive")),
             sum(1 for v in c["part2_yes_no"]["symptom_table"].values() if v == "yes"),
             sum(1 for v in c["part2_yes_no"]["symptom_table"].values() if v == "no")))
assert len({frozenset(c["investigations"]) for c in out}) == 1, "menu differs across cases"
print("\nwrote cases_%s.json (%d cases, identical %d-item menu)" % (LINE, len(out), len(PANEL)))
