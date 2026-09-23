"""Tremor cases, rebuilt on documented aetiologies.

Four of the six change disease entirely: the thyrotoxic label is Hirayama disease, the Wilson
label is neuronal intranuclear inclusion disease, the multiple sclerosis label is a novel POU4F1
variant, and the hepatic case is acquired hepatocerebral degeneration from herbal hepatotoxicity
with manganese loading rather than plain asterixis.

The classification that matters here is the activation condition - rest, postural, action or
intention - so the panel keeps those as separate bedside items, and the confirmatory tests are
mostly genetic, structural or toxicological rather than serological.
"""
from genlib import build

LINE = "tremor"

PANEL = {
    # added 2026-07-31: this line had no antibody entry at all, so an immune-mediated tremor
    # could not be worked up even in principle
    "neuronal surface and paraneoplastic antibody panel": {"tier": "blood"},
    "anti-GAD65 antibodies": {"tier": "blood"},
    "tremor at rest": {"tier": "bedside"},
    "postural tremor (arms outstretched)": {"tier": "bedside"},
    "kinetic / intention tremor (finger-nose)": {"tier": "bedside"},
    "tremor frequency estimate": {"tier": "bedside"},
    "effect of alcohol on the tremor": {"tier": "bedside"},
    "asterixis (wrist extension)": {"tier": "bedside"},
    "limb power and wasting": {"tier": "bedside"},
    "reflexes and plantar responses": {"tier": "bedside"},
    "sensory examination (vibration, pinprick)": {"tier": "bedside"},
    "foot deformity (pes cavus)": {"tier": "bedside"},
    "cerebellar signs (dysmetria, dysdiadochokinesia)": {"tier": "bedside"},
    "gait examination": {"tier": "bedside"},
    "cognitive screen (MMSE / MoCA / FAB)": {"tier": "bedside"},
    "slit-lamp examination for Kayser-Fleischer rings": {"tier": "bedside"},
    "medication, supplement and herbal history": {"tier": "bedside"},
    "family history": {"tier": "bedside"},
    "TSH / free T4": {"tier": "blood"},
    "full blood count": {"tier": "blood"},
    "liver function and albumin/globulin": {"tier": "blood"},
    "prothrombin time": {"tier": "blood"},
    "ammonia": {"tier": "blood"},
    "copper / caeruloplasmin / 24 h urinary copper": {"tier": "blood"},
    "whole-blood manganese": {"tier": "blood"},
    "vitamin B12 / folate": {"tier": "blood"},
    "glucose / HbA1c": {"tier": "blood"},
    "genetic testing (targeted panel or exome)": {"tier": "blood"},
    "brain MRI": {"tier": "imaging"},
    "cervical spine MRI (including flexion views)": {"tier": "imaging"},
    "DAT-SPECT": {"tier": "imaging"},
    "abdominal ultrasound / liver imaging": {"tier": "imaging"},
    "nerve conduction studies / EMG": {"tier": "invasive"},
    "surface EMG of forearm flexors and extensors": {"tier": "invasive"},
    "skin biopsy": {"tier": "invasive"},
}

CASES = [
 dict(
  video="mild_neuropathic_CMT_PMC11600610.mp4", pmcid="PMC11600610",
  dx="Charcot-Marie-Tooth disease type 2A presenting with neuropathic POSTURAL tremor - a rare "
     "presentation of a common hereditary polyneuropathy",
  sign="a postural tremor of the outstretched arms",
  correct=["Charcot-Marie-Tooth disease", "CMT2A", "hereditary polyneuropathy with tremor"],
  partial=["neuropathic tremor", "essential tremor", "Roussy-Levy syndrome"],
  who=dict(age=34, sex="male"),
  yes=["hand tremor when holding a posture", "the tremor started about six months ago",
       "weakness in the hands and feet", "the legs are weaker than the arms",
       "high-arched feet", "reduced sensation in the feet", "difficulty walking"],
  no=["tremor at rest", "a family history of the same illness", "the tremor improves with alcohol",
      "heavy alcohol use", "palpitations", "weight loss", "heat intolerance", "neck pain",
      "cognitive problems", "a new medication before the tremor"],
  inv={
   "limb power and wasting": {"v": "distal weakness - 4+/5 in the upper limbs, 3/5 in the lower "
                                   "limbs bilaterally", "p": "reported", "decisive": True},
   "foot deformity (pes cavus)": {"v": "pes cavus present", "p": "reported", "decisive": True},
   "reflexes and plantar responses": {"v": "ankle reflexes ABSENT", "p": "reported"},
   "sensory examination (vibration, pinprick)": {"v": "mild vibratory sensory loss", "p": "reported"},
   "nerve conduction studies / EMG": {"v": "moderate to severe motor polyneuropathy, axonal more "
                                           "than demyelinating", "p": "reported", "decisive": True},
   "genetic testing (targeted panel or exome)": {"v": "heterozygous deletion in MPZ and MFN2; "
                                                     "ambiguous copy number decrease in PMP22 "
                                                     "exons 2-3 - CMT2A", "p": "reported",
                                                 "decisive": True},
   "family history": {"v": "the patient DENIED any family history of a similar illness",
                      "p": "reported"},
   "cervical spine MRI (including flexion views)": {"v": "disc bulges at all cervical levels, no "
                                                        "cord compression", "p": "reported"},
  },
  dont_miss="Examine the feet and the reflexes in anyone with a postural tremor; pes cavus with "
            "absent ankle jerks turns essential tremor into a hereditary neuropathy, which "
            "changes the genetic counselling entirely.",
  must_not="diagnosing essential tremor and stopping - the distal weakness, pes cavus and absent "
           "ankle reflexes are the diagnosis"),

 dict(
  video="mild_thyrotoxic_PMC11639689.mp4", pmcid="PMC11639689",
  dx="Hirayama disease (juvenile cervical flexion myelopathy) presenting with a postural hand "
     "tremor that mimicked essential tremor",
  sign="a fine, fast tremor of the outstretched hands",
  correct=["Hirayama disease", "cervical flexion myelopathy",
           "juvenile monomelic amyotrophy"],
  partial=["neurogenic tremor", "essential tremor", "cervical myelopathy"],
  who=dict(age=20, sex="male"),
  yes=["hand tremor when holding a posture", "the tremor has progressed over five years",
       "the tremor is worse on one side than the other",
       "wasting of the small muscles of the hands", "being a young man"],
  no=["tremor at rest", "palpitations", "weight loss", "heat intolerance", "sweating",
      "neck or arm pain", "sensory loss", "a family history of the same illness",
      "the tremor improves with alcohol", "cognitive problems", "gait problems"],
  inv={
   "limb power and wasting": {"v": "mild distal finger muscle wasting", "p": "reported",
                              "decisive": True},
   "nerve conduction studies / EMG": {"v": "normal conduction velocity with NEUROGENIC changes in "
                                           "the C7-C8 myotome", "p": "reported", "decisive": True},
   "surface EMG of forearm flexors and extensors": {"v": "synchronous discharges at about 8 Hz in "
                                                        "both forearm flexors and extensors",
                                                    "p": "reported", "decisive": True},
   "cervical spine MRI (including flexion views)": {"v": "ON NECK FLEXION, prominent flow voids in "
                                                        "a widened posterior epidural space from "
                                                        "C6 to T3 - diagnostic of Hirayama "
                                                        "disease", "p": "reported",
                                                    "decisive": True},
   "brain MRI": {"v": "no brain lesion on unenhanced MRI with diffusion imaging", "p": "reported"},
  },
  dont_miss="A young man with a progressive postural tremor and wasted hand muscles needs a "
            "cervical MRI IN FLEXION; the plain neutral study can be normal and the diagnosis is "
            "missed.",
  must_not="calling it essential tremor or a thyrotoxic tremor - thyroid function is normal and "
           "the wasting and C7-C8 denervation point at the cervical cord"),

 dict(
  video="moderate_cerebellar_ms_PMC12558638.mp4", pmcid="PMC12558638",
  dx="Ataxia, intention tremor and hypotonia syndrome caused by a novel heterozygous nonsense "
     "POU4F1 variant, segregating in three affected female relatives",
  sign="an intention tremor with cerebellar signs on examination",
  correct=["POU4F1-related ataxia syndrome", "genetic cerebellar ataxia with intention tremor",
           "hereditary cerebellar disorder"],
  partial=["cerebellar intention tremor", "spinocerebellar ataxia", "cerebellar atrophy"],
  who=dict(age=28, sex="male"),
  yes=["unsteady walking since childhood", "the problem has been present all his life",
       "slowness of movement", "weakness of the legs", "learning difficulties",
       "problems with memory and thinking", "a mother with the same problem",
       "a sister with the same problem", "a grandmother with the same problem"],
  no=["sudden onset", "recent infection", "double vision", "heavy alcohol use",
      "a new medication before the symptoms", "numbness or tingling", "cancer", "fever",
      "the tremor improves with alcohol", "bladder problems"],
  inv={
   "genetic testing (targeted panel or exome)": {"v": "novel heterozygous NONSENSE variant in "
                                                     "POU4F1; present in the symptomatic mother, "
                                                     "sister and grandmother and absent in a "
                                                     "healthy uncle", "p": "reported",
                                                 "decisive": True},
   "brain MRI": {"v": "significant cerebellar atrophy with dilatation of the fourth ventricle",
                 "p": "reported", "decisive": True},
   "cognitive screen (MMSE / MoCA / FAB)": {"v": "MMSE 17, MoCA 12 - cognitive impairment",
                                            "p": "reported"},
   "family history": {"v": "mother, sister and grandmother affected - autosomal dominant pattern",
                      "p": "reported", "decisive": True},
   "cerebellar signs (dysmetria, dysdiadochokinesia)": {"v": "present, with hypotonia",
                                                        "p": "reported"},
  },
  dont_miss="Lifelong symptoms with three affected female relatives is a genetic ataxia; sending "
            "the family history and an exome answers it, and spares the patient immunotherapy.",
  must_not="diagnosing multiple sclerosis - the course is lifelong and non-relapsing, the MRI "
           "shows isolated cerebellar atrophy and there are no oligoclonal bands"),

 dict(
  video="moderate_hepatic_cirrhosis_PMC13166699.mp4", pmcid="PMC13166699",
  dx="Acquired hepatocerebral degeneration from OCCULT CIRRHOSIS, induced by long-term "
     "hepatotoxic traditional Chinese medicine (Psoralea corylifolia) together with "
     "manganese-containing supplements",
  sign="a coarse postural and intention tremor of the outstretched hands",
  correct=["acquired hepatocerebral degeneration", "occult cirrhosis with tremor",
           "manganese/hepatic toxic tremor"],
  partial=["hepatic encephalopathy", "asterixis", "manganism", "Wilson disease"],
  who=dict(age=66, sex="female"),
  yes=["tremor for more than two years", "the tremor got much worse in the last two months",
       "the tremor interferes with daily activities", "tremor when holding a posture",
       "tremor when reaching for something",
       "taking herbal medicines for a long time", "taking supplements for a long time",
       "living and working on a farm"],
  no=["heavy alcohol use", "jaundice", "abdominal swelling", "vomiting blood", "confusion",
      "a family history of the same illness", "a known liver diagnosis before this",
      "tremor at rest", "rings around the coloured part of the eye", "cognitive decline"],
  inv={
   "medication, supplement and herbal history": {"v": "long-term hepatotoxic traditional Chinese "
                                                     "medicine, notably Psoralea corylifolia, "
                                                     "plus manganese-containing supplements",
                                                 "p": "reported", "decisive": True},
   "liver function and albumin/globulin": {"v": "albumin 35.1 g/L (ref 35-52), globulin 30.8 g/L "
                                                "RAISED (ref 15-30), A/G ratio 1.14 LOW (ref "
                                                "1.2-2.4)", "p": "reported", "decisive": True},
   "prothrombin time": {"v": "prolonged at 14.4 seconds", "p": "reported"},
   "brain MRI": {"v": "bilateral T1 HYPERINTENSITY in the basal ganglia - manganese deposition",
                 "p": "reported", "decisive": True},
   "whole-blood manganese": {"v": "ELEVATED; fell after the supplements were stopped but remained "
                                  "above normal", "p": "reported", "decisive": True},
   "slit-lamp examination for Kayser-Fleischer rings": {"v": "NO Kayser-Fleischer rings - against "
                                                            "Wilson disease", "p": "reported"},
   "abdominal ultrasound / liver imaging": {"v": "cirrhosis", "p": "reported", "decisive": True},
   "ammonia": {"v": "raised, and it fell with treatment alongside clinical improvement",
               "p": "reported"},
  },
  dont_miss="Ask what herbal products and supplements the patient takes; the liver disease here "
            "was silent, and stopping the hepatotoxin with treatment reduced both the manganese "
            "and the tremor.",
  must_not="stopping at 'asterixis from hepatic encephalopathy' without finding the cause of the "
           "cirrhosis, or diagnosing Wilson disease - there are no Kayser-Fleischer rings"),

 dict(
  video="severe_holmes_structural_PMC13093780.mp4", pmcid="PMC13093780",
  dx="Holmes tremor following a thalamic TUBERCULOMA, appearing after completion of "
     "anti-tuberculous treatment",
  sign="a slow, large-amplitude tremor of one arm present at rest, on posture and on reaching",
  correct=["Holmes tremor", "rubral tremor", "tremor after CNS tuberculoma"],
  partial=["midbrain/thalamic lesion tremor", "structural tremor", "CNS tuberculosis"],
  who=dict(age=32, sex="female"),
  yes=["abnormal movement of the left arm", "the movement has progressed over about a month",
       "tremor present at rest", "tremor when holding a posture", "tremor when reaching",
       "the movements are slow and large", "the tremor is worse on stretching and action",
       "numbness of the affected arm", "having completed treatment for tuberculosis",
       "clumsiness of the left hand"],
  no=["a family history of ataxia", "heavy alcohol use", "a new medication before the tremor",
      "tremor in the other arm", "weight loss now", "fever now", "headache",
      "the tremor improves with alcohol", "cognitive problems"],
  inv={
   "brain MRI": {"v": "thalamic lesion (tuberculoma) that DECREASED in size after anti-tuberculous "
                      "treatment, with no gliosis", "p": "reported", "decisive": True},
   "tuberculosis treatment history": {"v": "CNS tuberculoma treated with anti-tuberculous therapy; "
                                           "the tremor began after treatment was completed",
                                      "p": "reported", "tier": "bedside", "decisive": True},
   "tremor at rest": {"v": "present", "p": "reported"},
   "postural tremor (arms outstretched)": {"v": "present", "p": "reported"},
   "kinetic / intention tremor (finger-nose)": {"v": "present and worse on reaching", "p": "reported"},
   "tremor frequency estimate": {"v": "slow, under about 4.5 Hz, with a wing-beating quality",
                                 "p": "reported", "decisive": True},
   "cerebellar signs (dysmetria, dysdiadochokinesia)": {"v": "dysmetria and dysdiadochokinesia in "
                                                            "the left upper limb", "p": "reported"},
   "full blood count": {"v": "normal", "p": "reported"},
   "family history": {"v": "no family history of spinocerebellar ataxia", "p": "reported"},
  },
  dont_miss="A tremor that is present at rest AND on posture AND on action localises to the "
            "midbrain or thalamus and demands imaging; Holmes tremor appears one to twenty-four "
            "months after the insult, so a treated CNS infection is still the cause.",
  must_not="attributing it to a degenerative or hereditary ataxia - the lesion is visible and "
           "there is no family history"),

 dict(
  video="severe_wilson_wingbeating_PMC10359687.mp4", pmcid="PMC10359687",
  dx="Neuronal intranuclear inclusion disease (NIID) presenting with a UNILATERAL wing-beating "
     "tremor, frontal/executive dysfunction, miosis and parkinsonism; partially improved with "
     "zonisamide",
  sign="a slow, large-amplitude proximal arm tremor on sustained abduction with flexed elbows",
  correct=["neuronal intranuclear inclusion disease", "NIID"],
  partial=["wing-beating tremor", "Wilson disease", "atypical parkinsonism"],
  who=dict(age=68, sex="male"),
  yes=["tremor of the right arm", "the tremor has been present for about eight years",
       "the tremor appears when holding the arms out with the elbows bent",
       "the movements are slow and large", "problems with memory and planning",
       "slowness of movement", "small pupils", "the tremor improved partially on a medication"],
  no=["tremor in the other arm", "a family history of neurological disease", "heavy alcohol use",
      "jaundice or liver disease", "rings around the coloured part of the eye",
      "recent infection", "sudden onset", "the tremor improves with alcohol", "seizures"],
  inv={
   "skin biopsy": {"v": "eosinophilic, p62- and ubiquitin-POSITIVE intranuclear inclusions in "
                        "adipocytes, sweat gland cells and fibroblasts - diagnostic of NIID",
                   "p": "reported", "decisive": True},
   "cognitive screen (MMSE / MoCA / FAB)": {"v": "MMSE 23/30 and Frontal Assessment Battery 9/18 "
                                                 "- frontal/executive dysfunction", "p": "reported",
                                            "decisive": True},
   "DAT-SPECT": {"v": "specific binding ratios 3.94 right and 3.82 left striatum", "p": "reported"},
   "genetic testing (targeted panel or exome)": {"v": "NOTCH2NLC GGC repeat expansion - genetically "
                                                     "confirmed NIID", "p": "reported",
                                                 "decisive": True},
   "trial of zonisamide": {"v": "the wing-beating tremor partially improved", "p": "reported",
                           "tier": "bedside"},
   "trial of pramipexole": {"v": "added at 0.375 mg/day and increased", "p": "reported",
                            "tier": "bedside"},
   "family history": {"v": "no family history of neurological disease", "p": "reported"},
  },
  dont_miss="Wing-beating tremor is not synonymous with Wilson disease; in an older patient with "
            "cognitive decline and miosis, send copper studies AND consider a skin biopsy for "
            "NIID, because the diagnosis changes counselling entirely.",
  must_not="diagnosing Wilson disease on the wing-beating tremor alone - copper studies are "
           "normal, there are no Kayser-Fleischer rings and the patient is 68"),
]

build(LINE, PANEL, CASES)
