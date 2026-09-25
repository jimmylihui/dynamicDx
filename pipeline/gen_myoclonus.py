"""Myoclonus cases, rebuilt on the aetiology each source article actually documents.

Three of the five change disease entirely: the clip labelled Creutzfeldt-Jakob is a
post-resuscitation hypoxic myoclonus, the palatal clip is neuro-Behcet's, and the paroxysmal
myoclonus clip belongs to a different line. Localising myoclonus - cortical, subcortical,
segmental - is what the investigations here are for, because it is what decides treatment.
"""
from genlib import build

LINE = "myoclonus"

PANEL = {
    # added 2026-07-31: the line had no genetic entry, so the progressive myoclonic epilepsies
    # could not be excluded even in principle
    "progressive myoclonic epilepsy gene panel (EPM1/CSTB, EPM2A, NHLRC1, KCNC1)":
        {"v": "no pathogenic variant", "p": "derived", "tier": "blood"},
    "observation of the jerks": {"v": "brief shock-like jerks", "p": "derived", "tier": "bedside"},
    "provocation by action or posture": {"v": "not clearly action-sensitive", "p": "derived",
                                         "tier": "bedside"},
    "provocation by startle": {"v": "no startle sensitivity", "p": "derived", "tier": "bedside"},
    "effect of sleep": {"v": "jerks disappear in sleep", "p": "derived", "tier": "bedside"},
    "medication review": {"v": "no culprit drug identified", "p": "derived", "tier": "bedside"},
    "cognitive screen (MMSE / ACE-R)": {"v": "normal", "p": "derived", "tier": "bedside"},
    "vital signs": {"v": "normal, afebrile", "p": "derived", "tier": "bedside"},
    "full blood count": {"v": "normal", "p": "derived", "tier": "blood"},
    "renal function (urea, creatinine)": {"v": "normal", "p": "derived", "tier": "blood"},
    "liver function and ammonia": {"v": "normal", "p": "derived", "tier": "blood"},
    "electrolytes (Na, K, Ca, Mg)": {"v": "normal", "p": "derived", "tier": "blood"},
    "glucose": {"v": "normal", "p": "derived", "tier": "blood"},
    "TSH / free T4": {"v": "normal", "p": "derived", "tier": "blood"},
    "vitamin B12 / folate": {"v": "normal", "p": "derived", "tier": "blood"},
    "copper / caeruloplasmin": {"v": "normal", "p": "derived", "tier": "blood"},
    "coeliac serology (tissue transglutaminase IgA)": {"v": "negative", "p": "derived",
                                                       "tier": "blood"},
    "autoimmune and paraneoplastic antibody panel": {"v": "negative", "p": "derived",
                                                     "tier": "blood"},
    "anti-measles antibody titres (serum)": {"v": "not raised", "p": "derived", "tier": "blood"},
    "toxicology screen": {"v": "negative", "p": "derived", "tier": "blood"},
    "ESR / CRP": {"v": "normal", "p": "derived", "tier": "blood"},
    "HIV / syphilis serology": {"v": "negative", "p": "derived", "tier": "blood"},
    "brain MRI": {"v": "no relevant structural lesion", "p": "derived", "tier": "imaging"},
    "MRI brainstem / dentato-rubro-olivary pathway": {"v": "normal; no inferior olivary "
                                                          "hypertrophy", "p": "derived",
                                                      "tier": "imaging"},
    "CT chest / abdomen / pelvis (occult tumour)": {"v": "no malignancy", "p": "derived",
                                                    "tier": "imaging"},
    "EEG": {"v": "no epileptiform discharges", "p": "derived", "tier": "invasive"},
    "EEG-EMG polygraphy (back-averaging)": {"v": "no cortical correlate preceding the jerks",
                                            "p": "derived", "tier": "invasive"},
    "somatosensory evoked potentials": {"v": "normal, no giant SSEP", "p": "derived",
                                        "tier": "invasive"},
    "EMG burst duration": {"v": "not recorded", "p": "derived", "tier": "invasive"},
    "lumbar puncture / CSF": {"v": "normal cells, protein and glucose; no oligoclonal bands",
                              "p": "derived", "tier": "invasive"},
    "CSF 14-3-3 / RT-QuIC (prion)": {"v": "negative", "p": "derived", "tier": "invasive"},
    "upper GI endoscopy with duodenal biopsy": {"v": "not performed", "p": "derived",
                                                "tier": "invasive"},
}

CASES = [
 dict(
  video="mild_palatal_PMC12933468.mp4", pmcid="PMC12933468",
  dx="Symptomatic palatal myoclonus (palatal tremor) as a manifestation of neuro-Behcet's disease",
  sign="rhythmic movement of the soft palate seen through the open mouth",
  correct=["neuro-Behcet's disease", "Behcet's disease with brainstem involvement",
           "symptomatic palatal tremor from an inflammatory brainstem lesion"],
  partial=["palatal myoclonus", "palatal tremor", "brainstem lesion"],
  who=dict(age=30, sex="male"),
  yes=["a clicking sound in the ears", "rhythmic movement in the throat or palate",
       "recurrent mouth ulcers", "genital ulcers", "pain in several joints",
       "abdominal pain and diarrhoea for years", "numbness or altered sensation",
       "the systemic symptoms improved on immunosuppressive treatment",
       "the palate movement persisted despite treatment"],
  no=["a stroke", "recent head injury", "heavy alcohol use", "cancer",
      "the movements stop during sleep", "seizures", "cognitive decline", "family history",
      "jerks brought on by movement", "jerks brought on by a sudden noise"],
  inv={
   "observation of the jerks": {"v": "rhythmic palatal movements at 2-3 Hz with bilateral "
                                     "acoustic clicks, louder on the right", "p": "reported",
                                "decisive": True},
   "effect of sleep": {"v": "palatal tremor PERSISTS in sleep - characteristic of palatal tremor "
                            "rather than true myoclonus", "p": "derived", "decisive": True},
   "MRI brainstem / dentato-rubro-olivary pathway": {"v": "inflammatory brainstem involvement in "
                                                         "the Guillain-Mollaret triangle",
                                                     "p": "reported", "decisive": True},
   "HLA-B51 and Behcet's assessment (pathergy, ophthalmology review)":
       {"v": "consistent with Behcet's disease", "p": "reported", "tier": "blood",
        "decisive": True},
   "ESR / CRP": {"v": "raised during systemic flares", "p": "reported"},
   "trial of colchicine, corticosteroids and azathioprine":
       {"v": "systemic symptoms improved but the palatal tremor persisted", "p": "reported",
        "tier": "bedside"},
   "upper GI endoscopy with duodenal biopsy": {"v": "intestinal Behcet involvement", "p": "reported"},
  },
  dont_miss="Palatal tremor means a brainstem lesion; in a young patient with recurrent oral and "
            "genital ulcers and gut symptoms it is neuro-Behcet's, which is treatable with "
            "immunosuppression.",
  must_not="calling it idiopathic palatal tremor and stopping - the systemic ulcer history is "
           "the diagnosis"),

 dict(
  video="moderate_coeliac_PMC10548079.mp4", pmcid="PMC10548079",
  dx="Coeliac disease-related CORTICAL myoclonus with ataxia, refractory to drugs and treated "
     "with pallidal (GPi) deep brain stimulation",
  sign="jerky movements of the arms brought out by posture and action, with unsteadiness",
  correct=["coeliac-related myoclonus", "gluten/coeliac myoclonic ataxia",
           "cortical myoclonus from coeliac disease"],
  partial=["cortical myoclonus", "myoclonus-ataxia syndrome", "coeliac disease"],
  who=dict(age=60, sex="male"),
  yes=["jerky movements of the arms", "the jerks are worse on the left",
       "jerks in the legs as well", "unsteadiness when walking",
       "jerks brought on by reaching or holding a posture",
       "years of diarrhoea", "the jerks started about six months ago"],
  no=["a known bowel diagnosis before this", "family history of similar jerks",
      "family history of balance problems", "heavy alcohol use", "recent infection", "fever",
      "a new medication before the jerks", "cancer", "cognitive decline", "seizures"],
  inv={
   "coeliac serology (tissue transglutaminase IgA)": {"v": "23 U/mL (normal up to 10) - RAISED",
                                                      "p": "reported", "decisive": True},
   "upper GI endoscopy with duodenal biopsy": {"v": "flattened villi - coeliac disease",
                                               "p": "reported", "decisive": True},
   "somatosensory evoked potentials": {"v": "GIANT median nerve SSEP", "p": "reported",
                                       "decisive": True},
   "EEG-EMG polygraphy (back-averaging)": {"v": "electropositive polyspikes equally at Cz and C4; "
                                                "cortical potential 11 ms before the jerk - "
                                                "CORTICAL myoclonus", "p": "reported",
                                           "decisive": True},
   "autoimmune and paraneoplastic antibody panel": {"v": "negative across AMPA, amphiphysin, "
                                                        "CV2.1, DPPX, GABA-B, GAD65, Hu, NMDA, "
                                                        "PNMA2, recoverin, Ri, SOX1, Titin, Tr",
                                                    "p": "reported"},
   "brain MRI": {"v": "mild diffuse atrophy only", "p": "reported"},
   "Unified Myoclonus Rating Scale": {"v": "90 before GPi DBS, 83 after; action myoclonus "
                                           "subscore 56 to 53 - partial benefit", "p": "reported",
                                      "tier": "bedside"},
  },
  dont_miss="Send coeliac serology in unexplained myoclonus-ataxia; a gluten-free diet treats the "
            "cause, and the myoclonus here proved drug-refractory.",
  must_not="treating it as idiopathic cortical myoclonus without looking for coeliac disease"),

 dict(
  video="moderate_druginduced_PMC12297136.mp4", pmcid="PMC12297136",
  dx="Risperidone-induced generalized myoclonus (on concomitant sertraline, without meeting "
     "criteria for serotonin syndrome)",
  sign="sudden generalized shock-like jerks in a patient lying in bed",
  correct=["drug-induced myoclonus", "risperidone-induced myoclonus",
           "antipsychotic adverse effect"],
  partial=["toxic/metabolic myoclonus", "serotonin syndrome", "generalized myoclonus"],
  who=dict(age=73, sex="male"),
  yes=["sudden generalized jerking", "the jerks started abruptly",
       "taking an antipsychotic long term", "taking an antidepressant as well",
       "behavioural symptoms treated with medication", "previous stroke or cerebrovascular disease",
       "memory and attention problems", "the jerks stopped after one drug was withdrawn"],
  no=["fever", "muscle rigidity", "sweating and agitation", "overactive reflexes and clonus",
      "recent infection", "heavy alcohol use", "family history of similar jerks",
      "jerks brought on by a sudden noise", "cancer", "recent head injury"],
  inv={
   "medication review": {"v": "long-term risperidone with concomitant sertraline; myoclonus "
                              "resolved completely within 24 h of withdrawing RISPERIDONE alone",
                         "p": "reported", "decisive": True},
   "serotonin syndrome criteria (Hunter)": {"v": "NOT met - no clonus, hyperreflexia, fever or "
                                                 "autonomic instability", "p": "reported",
                                            "tier": "bedside", "decisive": True},
   "full blood count": {"v": "white cells mildly raised at 11.8 x10^9/L", "p": "reported"},
   "renal function (urea, creatinine)": {"v": "blood urea nitrogen 24 mg/dL, creatinine "
                                              "1.62 mg/dL - stable", "p": "reported"},
   "cognitive screen (MMSE / ACE-R)": {"v": "ACE-R 33/100 - significant impairment of memory, "
                                            "attention, fluency, language and visuospatial "
                                            "function", "p": "reported"},
   "brain MRI": {"v": "chronic cerebrovascular change", "p": "reported"},
  },
  dont_miss="Review the drug chart first in new generalized myoclonus - withdrawal of the culprit "
            "resolved this within a day, with no other treatment.",
  must_not="diagnosing serotonin syndrome; the Hunter criteria are not met and the trigger was "
           "the antipsychotic, not the antidepressant"),

 dict(
  video="severe_cjd_PMC9833462.mp4", pmcid="PMC9833462",
  dx="Intractable generalized post-hypoxic myoclonus after cardiac arrest and resuscitation, in a "
     "minimally conscious patient, controlled with intrathecal baclofen",
  sign="frequent generalized shock-like jerks in a bed-bound patient",
  correct=["post-hypoxic myoclonus", "myoclonus after cardiac arrest",
           "hypoxic-ischaemic brain injury"],
  partial=["Lance-Adams syndrome", "generalized myoclonus", "myoclonic status"],
  who=dict(age=29, sex="female"),
  yes=["generalized jerking", "the jerks began after a resuscitation",
       "being in a minimally conscious state", "stiff joints that will not straighten",
       "difficulty being positioned comfortably", "disturbed sleep because of the jerks",
       "crying or distress with the jerks", "increased muscle tone"],
  no=["rapidly progressive dementia before the jerks", "startle-provoked jerks as the first sign",
      "a family history of a similar illness", "recent infection", "fever",
      "a new medication before the jerks", "heavy alcohol use", "cancer", "seizures on EEG"],
  inv={
   "history of the precipitating event": {"v": "cardiac arrest with resuscitation; myoclonus and "
                                               "contractures developed afterwards", "p": "reported",
                                          "tier": "bedside", "decisive": True},
   "brain MRI": {"v": "hypoxic-ischaemic injury", "p": "reported", "decisive": True},
   "CSF 14-3-3 / RT-QuIC (prion)": {"v": "negative - excludes Creutzfeldt-Jakob disease",
                                    "p": "derived", "decisive": True},
   "modified Ashworth scale (spasticity)": {"v": "grade 3 in both upper and lower limbs before "
                                                "treatment; improved to grade 1+ in the upper "
                                                "limbs and grade 2 in the lower limbs after "
                                                "intrathecal baclofen", "p": "reported",
                                            "tier": "bedside"},
   "intrathecal baclofen trial": {"v": "50 mcg bolus on day 1, 75 mcg on day 2; Unified Myoclonus "
                                       "Rating Scale improved progressively with dose; sleep and "
                                       "positioning improved", "p": "reported", "tier": "invasive",
                                  "decisive": True},
   "joint range of motion": {"v": "multiple contractures of shoulders, elbows, wrists, hips, "
                                  "knees and ankles; unchanged by treatment", "p": "reported",
                             "tier": "bedside"},
   "EEG": {"v": "diffuse encephalopathic changes without periodic sharp wave complexes",
           "p": "derived"},
  },
  dont_miss="Post-hypoxic myoclonus is disabling but treatable symptomatically; intrathecal "
            "baclofen relieved the jerks, the sleep disturbance and the distress even when "
            "function could not be restored.",
  must_not="diagnosing Creutzfeldt-Jakob disease - there is no preceding dementia, the trigger is "
           "a documented cardiac arrest, and prion markers are negative"),

 dict(
  video="severe_sspe_PMC13071100.mp4", pmcid="PMC13071100",
  dx="ADULT-ONSET subacute sclerosing panencephalitis, presenting with subacute cognitive decline "
     "and later periodic myoclonus",
  sign="periodic jerks of the shoulders and hips every few seconds, with a slow relaxation phase",
  correct=["subacute sclerosing panencephalitis", "SSPE", "measles-related encephalitis"],
  partial=["periodic myoclonus", "progressive myoclonic encephalopathy",
           "Creutzfeldt-Jakob disease"],
  who=dict(age=41, sex="male"),
  yes=["regular jerks every few seconds", "the jerks involve the shoulders and hips",
       "difficulty concentrating at work", "making uncharacteristic mistakes with numbers",
       "trouble with memory and planning", "the cognitive problems came first, months before the jerks",
       "slurred speech", "unsteadiness", "slow movements", "born outside the country",
       "wide-based gait"],
  no=["heavy alcohol use", "recent infection", "fever", "weight loss", "night sweats",
      "a family history of a similar illness", "a new medication before the symptoms",
      "seizures", "cancer", "jerks brought on by a sudden noise"],
  inv={
   "EEG": {"v": "periodic slow wave complexes TIME-LOCKED to the myoclonic jerks", "p": "reported",
           "decisive": True},
   "lumbar puncture / CSF": {"v": "intrathecal synthesis of anti-measles IgG", "p": "reported",
                             "decisive": True},
   "anti-measles antibody titres (serum)": {"v": "raised, with CSF-restricted synthesis",
                                            "p": "reported", "decisive": True},
   "brain MRI": {"v": "only mild parietal-predominant cerebral atrophy", "p": "reported"},
   "cognitive screen (MMSE / ACE-R)": {"v": "frontoparietal pattern of deficits on formal "
                                            "neuropsychological testing", "p": "reported"},
   "measles vaccination and infection history": {"v": "measles in infancy; SSPE typically follows "
                                                     "4-12 years later, but onset here was in "
                                                     "adulthood", "p": "reported",
                                                 "tier": "bedside", "decisive": True},
   "CSF 14-3-3 / RT-QuIC (prion)": {"v": "negative", "p": "derived"},
   "observation of the jerks": {"v": "periodic myoclonus with a SLOW relaxation phase involving "
                                     "bilateral shoulder abductors and hip flexors",
                                "p": "reported", "decisive": True},
  },
  dont_miss="SSPE is not only a childhood disease; a frontoparietal cognitive profile followed by "
            "periodic myoclonus should prompt CSF anti-measles antibodies before a "
            "neurodegenerative label is applied.",
  must_not="diagnosing Creutzfeldt-Jakob disease on the periodic EEG - the complexes here are "
           "time-locked to the jerks and the CSF shows anti-measles synthesis"),
]

build(LINE, PANEL, CASES)
