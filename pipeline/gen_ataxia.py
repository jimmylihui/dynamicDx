"""Build the ataxia cases on documented aetiologies.

The line panel names the tests an ataxia work-up draws on, with their tier and no values. Each
case's chart holds only the results its own article reports, and flags the ones that actually
decide the diagnosis.
"""
from genlib import build

LINE = "ataxia"

PANEL = {
    "gait examination": {"tier": "bedside"},
    "finger-nose / heel-shin testing": {"tier": "bedside"},
    "Romberg test": {"tier": "bedside"},
    "bedside eye-movement exam": {"tier": "bedside"},
    "SARA score": {"tier": "bedside"},
    "vital signs": {"tier": "bedside"},
    "full blood count": {"tier": "blood"},
    "renal and liver function": {"tier": "blood"},
    "electrolytes (Na, K, Ca, Mg)": {"tier": "blood"},
    "glucose / HbA1c": {"tier": "blood"},
    "TSH / free T4": {"tier": "blood"},
    "vitamin B12 / folate": {"tier": "blood"},
    "vitamin E": {"tier": "blood"},
    "serum thiamine (vitamin B1)": {"tier": "blood"},
    "copper / caeruloplasmin": {"tier": "blood"},
    "serum lithium and drug levels": {"tier": "blood"},
    "alcohol history / GGT / CDT": {"tier": "blood"},
    "ESR / CRP": {"tier": "blood"},
    "coeliac serology (anti-TTG)": {"tier": "blood"},
    "paraneoplastic antibody panel (serum)": {"tier": "blood"},
    "anti-GQ1b / anti-ganglioside antibodies": {"tier": "blood"},
    "anti-GAD antibodies": {"tier": "blood"},
    "HIV / syphilis serology": {"tier": "blood"},
    "genetic ataxia panel": {"tier": "blood"},
    "brain MRI": {"tier": "imaging"},
    "MR angiography (posterior circulation)": {"tier": "imaging"},
    "CT chest / abdomen / pelvis (occult tumour)": {"tier": "imaging"},
    "FDG-PET (occult tumour)": {"tier": "imaging"},
    "lumbar puncture / CSF": {"tier": "invasive"},
    "nerve conduction studies / EMG": {"tier": "invasive"},
    "EEG": {"tier": "invasive"},
    "somatosensory evoked potentials": {"tier": "invasive"},
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

# this line was written before genlib and states the trial rule without the examples
build(LINE, PANEL, CASES, explicit_only_rule=(
    "Entries flagged explicit_only are therapeutic trials, not tests. Return one only when the "
    "doctor names that specific trial. A blanket or category-level request returns nothing."))
