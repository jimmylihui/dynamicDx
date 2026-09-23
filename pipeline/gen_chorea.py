"""Chorea cases, rebuilt on documented aetiologies.

Two labels change: the clip relabelled hyperglycemic in an earlier pass is a COVID-19
vaccine-induced hemichorea-hemiballismus, and the clip relabelled demyelinating is hyperthyroid
chorea. The remaining eight already matched their sources but carried template investigations
rather than the values their articles report.

Five of the ten are hyperglycaemic in origin, so the discriminating work in this line is done by
glucose, HbA1c and the pattern on imaging, and by the negatives that separate the other five -
thyroid function, an autoimmune screen, the sodium and the vaccine history.
"""
from genlib import build

LINE = "chorea"

PANEL = {
    # added 2026-07-31: the line had no genetic entry, so the inherited choreas could not be
    # excluded even in principle
    "HTT CAG repeat testing (Huntington disease)": {"tier": "blood"},
    "chorea gene panel (VPS13A, JPH3, C9orf72, FRRS1L)": {"tier": "blood"},
    "distribution of the movements (one side, both, face, limbs)": {"tier": "bedside"},
    "effect of voluntary action and anxiety": {"tier": "bedside"},
    "effect of sleep": {"tier": "bedside"},
    "speed of onset": {"tier": "bedside"},
    "vital signs": {"tier": "bedside"},
    "cognitive and behavioural assessment (MMSE / FAB)": {"tier": "bedside"},
    "speech assessment": {"tier": "bedside"},
    "gait and coordination": {"tier": "bedside"},
    "skin examination": {"tier": "bedside"},
    "medication and vaccination history": {"tier": "bedside"},
    "family history of chorea or Huntington disease": {"tier": "bedside"},
    "blood glucose": {"tier": "blood"},
    "HbA1c": {"tier": "blood"},
    "ketones (blood or urine)": {"tier": "blood"},
    "sodium and serum osmolality": {"tier": "blood"},
    "renal function and eGFR": {"tier": "blood"},
    "full blood count": {"tier": "blood"},
    "TSH, free T4 and free T3": {"tier": "blood"},
    "thyrotropin receptor antibodies (TRAb)": {"tier": "blood"},
    "morning cortisol, ACTH and pituitary hormones": {"tier": "blood"},
    "antinuclear antibody and rheumatological screen": {"tier": "blood"},
    "antiphospholipid antibodies": {"tier": "blood"},
    "autoimmune encephalopathy / paraneoplastic antibody panel": {"tier": "blood"},
    "copper / caeruloplasmin": {"tier": "blood"},
    "peripheral blood film for acanthocytes": {"tier": "blood"},
    "Huntington HTT CAG repeat testing": {"tier": "blood"},
    "HIV and syphilis serology": {"tier": "blood"},
    "inflammatory markers (ESR, CRP)": {"tier": "blood"},
    "CT head (non-contrast)": {"tier": "imaging"},
    "brain MRI with contrast": {"tier": "imaging"},
    "MR or CT angiography": {"tier": "imaging"},
    "FDG-PET brain": {"tier": "imaging"},
    "PET-CT or CT body (occult malignancy)": {"tier": "imaging"},
    "thyroid ultrasound": {"tier": "imaging"},
    "lumbar puncture / CSF": {"tier": "invasive"},
    "EEG": {"tier": "invasive"},
    "trial of glucose correction with insulin": {"tier": "bedside"},
    "trial of immunotherapy": {"tier": "invasive"},
}

CASES = [
 dict(
  video="c_10051035.mp4", pmcid="PMC10051035",
  dx="POST-STROKE hemichorea - chorea as the presenting manifestation of an ischaemic stroke "
     "involving the lentiform nucleus",
  sign="continuous one-sided writhing movements of the arm and leg",
  correct=["post-stroke chorea", "hemichorea from a basal-ganglia infarct", "ischaemic stroke"],
  partial=["structural hemichorea", "vascular chorea", "hemichorea-hemiballism"],
  who=dict(age=64, sex="female"),
  yes=["one-sided involuntary movements", "sudden onset", "the movements were the first symptom",
       "high blood pressure", "the movements affect the arm and the leg on the same side",
       "weakness on the same side"],
  no=["a family history of chorea", "diabetes with very high sugars", "recent vaccination",
      "a rash", "thyroid symptoms", "confusion or behavioural change", "recent infection",
      "fever", "the movements are on both sides", "gradual onset over months"],
  inv={
   "speed of onset": {"v": "chorea was the INITIAL manifestation of the stroke in 57% of the "
                           "series; two patients within 24 hours, three between days 2 and 5",
                      "p": "reported", "decisive": True},
   "CT head (non-contrast)": {"v": "ischaemic stroke - 92.9% of the series were ischaemic and one "
                                   "was haemorrhagic", "p": "reported", "decisive": True},
   "brain MRI with contrast": {"v": "lesions in the LENTIFORM NUCLEUS (50%), insula (35.7%), "
                                    "caudate (14.3%) and thalamus (14.3%); cortical in 35.7%, deep "
                                    "in 35.7%, both in 28.6%", "p": "reported", "decisive": True},
   "MR or CT angiography": {"v": "middle cerebral artery in 64.3%, anterior cerebral artery in "
                                 "21.4%, posterior cerebral artery in 14.3%", "p": "reported"},
   "blood glucose": {"v": "normal - non-ketotic hyperglycaemia was an exclusion criterion for this "
                          "series", "p": "reported", "decisive": True},
   "family history of chorea or Huntington disease": {"v": "none - a family history of chorea was "
                                                          "an exclusion criterion", "p": "reported"},
  },
  dont_miss="Acute one-sided chorea is a stroke presentation - image immediately and start "
            "secondary prevention; in most of this series the chorea came BEFORE any other "
            "stroke symptom.",
  must_not="attributing acute hemichorea to hyperglycaemia without checking the glucose, or "
           "waiting for weakness before calling it a stroke"),

 dict(
  video="c_11093232.mp4", pmcid="PMC11093232",
  dx="SERONEGATIVE autoimmune hemichorea with encephalopathy, diagnosed by an empirical response "
     "to intravenous immunoglobulin after an entirely negative work-up",
  sign="one-sided writhing movements of the face, arm and leg",
  correct=["autoimmune hemichorea", "immunotherapy-responsive chorea",
           "seronegative autoimmune movement disorder"],
  partial=["autoimmune encephalitis", "hemichorea", "paraneoplastic chorea"],
  who=dict(age=74, sex="female"),
  yes=["one-sided involuntary movements", "the face is involved as well as the arm and leg",
       "the movements came on over days to weeks", "a rash on the arm just before it started",
       "confusion and disorientation developed afterwards", "rambling, off-topic speech",
       "grandiose beliefs", "an unusually elevated mood", "several years of mild memory decline",
       "the movements improved dramatically after an infusion treatment"],
  no=["a family history of chorea", "very high blood sugars", "thyroid symptoms",
      "recent vaccination", "a known cancer", "sudden onset in a single moment",
      "fever", "the movements affect both sides", "heavy alcohol use"],
  inv={
   "trial of immunotherapy": {"v": "empirical IVIg produced DRAMATIC improvement of the hemichorea "
                                   "- the diagnosis rests on the treatment response",
                              "p": "reported", "decisive": True},
   "autoimmune encephalopathy / paraneoplastic antibody panel": {"v": "NEGATIVE in serum and CSF - "
                                                                     "seronegative", "p": "reported",
                                                                 "decisive": True},
   "CT head (non-contrast)": {"v": "symmetric frontal-predominant atrophy, no focal lesion",
                              "p": "reported"},
   "brain MRI with contrast": {"v": "1.5T with gadolinium - frontal-predominant atrophy but NO "
                                    "focal lesion, with normal basal ganglia structure and volume",
                               "p": "reported", "decisive": True},
   "PET-CT or CT body (occult malignancy)": {"v": "skull base to thighs - no malignancy and no "
                                                  "infection", "p": "reported", "decisive": True},
   "antinuclear antibody and rheumatological screen": {"v": "ANA mildly positive at 1:40; extensive "
                                                            "rheumatological labs otherwise normal",
                                                       "p": "reported"},
   "skin examination": {"v": "a painless, non-pruritic confluent erythematous rash on the left arm "
                             "one day before the chorea began; it improved with doxycycline and "
                             "clindamycin but the chorea did not", "p": "reported",
                        "decisive": True},
   "cognitive and behavioural assessment (MMSE / FAB)": {"v": "progressive disorientation, "
                                                              "tangential speech, grandiose "
                                                              "hallucinations and euphoric affect",
                                                         "p": "reported"},
  },
  dont_miss="A negative antibody panel does not exclude an autoimmune chorea; when imaging and "
            "serology are clean and the course is subacute with encephalopathy, an empirical "
            "immunotherapy trial is both diagnostic and therapeutic.",
  must_not="concluding a neurodegenerative chorea because the antibodies are negative and the "
           "MRI shows only atrophy"),

 dict(
  video="c_11098550.mp4", pmcid="PMC11098550",
  dx="Generalized chorea from EUVOLAEMIC HYPONATRAEMIA due to SECONDARY ADRENAL INSUFFICIENCY, "
     "with an empty sella",
  sign="generalized writhing movements of all four limbs, the tongue and the face",
  correct=["secondary adrenal insufficiency", "hypopituitarism with hyponatraemia",
           "chorea from adrenal insufficiency"],
  partial=["hyponatraemic chorea", "metabolic chorea", "generalized chorea"],
  who=dict(age=48, sex="male"),
  yes=["involuntary movements of all four limbs", "the tongue moves involuntarily",
       "the face is involved", "irritability and aggressive behaviour for months",
       "the behaviour changed before the movements started", "low blood pressure",
       "an underactive thyroid treated with tablets", "loss of libido or sexual function",
       "the symptoms improved in hospital"],
  no=["a family history of chorea", "very high blood sugars", "recent vaccination", "a rash",
      "one-sided movements only", "sudden onset", "recent infection", "fever",
      "a known cancer", "heavy alcohol use"],
  inv={
   "sodium and serum osmolality": {"v": "HYPONATRAEMIA with LOW serum osmolality, euvolaemic",
                                   "p": "reported", "decisive": True},
   "morning cortisol, ACTH and pituitary hormones": {"v": "LOW ACTH, low prolactin and low "
                                                          "testosterone - secondary adrenal "
                                                          "insufficiency with anterior pituitary "
                                                          "failure", "p": "reported",
                                                     "decisive": True},
   "brain MRI with contrast": {"v": "EMPTY SELLA sign", "p": "reported", "decisive": True},
   "vital signs": {"v": "pulse 90/min, blood pressure 90/60 mmHg", "p": "reported"},
   "cognitive and behavioural assessment (MMSE / FAB)": {"v": "MMSE 27/30, Frontal Assessment "
                                                              "Battery 14", "p": "reported"},
   "TSH, free T4 and free T3": {"v": "T3 1.19 ng/mL, T4 0.52 ug/dL, TSH 0.96 uIU/L - on treatment "
                                     "for hypothyroidism", "p": "reported"},
   "blood glucose": {"v": "random glucose 88 mg/dL, HbA1c 5.6% - normal", "p": "reported"},
   "lumbar puncture / CSF": {"v": "protein 32 mg/dL, glucose 66 mg/dL against a blood sugar of "
                                  "100, two lymphocytes - normal", "p": "reported"},
  },
  dont_miss="Check the sodium and the pituitary axis in unexplained generalized chorea; "
            "hyponatraemia from secondary adrenal insufficiency is fully reversible and the "
            "empty sella points straight at the pituitary.",
  must_not="starting only symptomatic chorea suppression without correcting the sodium and "
           "replacing steroid"),

 dict(
  video="c_11586875.mp4", pmcid="PMC11586875",
  dx="DIABETIC STRIATOPATHY from non-ketotic hyperglycaemia in a woman with long-standing poorly "
     "controlled type 2 diabetes (case 2 of the report)",
  sign="continuous large writhing movements of both arms",
  correct=["diabetic striatopathy", "non-ketotic hyperglycaemic chorea",
           "hyperglycaemia-induced chorea"],
  partial=["chorea-ballism", "metabolic chorea", "hyperglycaemia"],
  who=dict(age=84, sex="female"),
  yes=["involuntary movements of both arms", "long-standing diabetes",
       "the diabetes has been poorly controlled", "excessive thirst and passing urine often",
       "the symptoms began about a week ago", "coronary artery disease",
       "previous stroke or cerebrovascular disease", "a urinary infection"],
  no=["a family history of chorea", "thyroid symptoms", "recent vaccination", "a rash",
      "confusion or behavioural change before the movements", "recent head injury",
      "the movements are on one side only", "heavy alcohol use", "fever"],
  inv={
   "blood glucose": {"v": "799 mg/dL (normal 74-106)", "p": "reported", "decisive": True},
   "HbA1c": {"v": "11%", "p": "reported", "decisive": True},
   "ketones (blood or urine)": {"v": "NEGATIVE - non-ketotic", "p": "reported", "decisive": True},
   "brain MRI with contrast": {"v": "HYPOSIGNAL involving the corpus striatum bilaterally, "
                                    "extending to the medial cerebral crus on T2 and FLAIR, with "
                                    "mild T1 HYPERSIGNAL in the basal nuclei", "p": "reported",
                               "decisive": True},
   "inflammatory markers (ESR, CRP)": {"v": "elevated, with leukocyturia", "p": "reported"},
   "trial of glucose correction with insulin": {"v": "diazepam and insulin gave partial "
                                                     "improvement, but the extrapyramidal symptoms "
                                                     "persisted; she was readmitted a year later "
                                                     "with a hyperosmolar episode", "p": "reported",
                                                "decisive": True},
  },
  dont_miss="Check a finger-prick glucose at the bedside in any new chorea - diabetic "
            "striatopathy is the second commonest cause after stroke and it improves with glucose "
            "control.",
  must_not="assuming the movements will fully resolve once the sugar is corrected; they persisted "
           "here"),

 dict(
  video="c_11973688.mp4", pmcid="PMC11973688",
  dx="Chorea due to GRAVES' HYPERTHYROIDISM - left lower limb chorea that resolved on "
     "methimazole",
  sign="involuntary movements of one lower limb, evident when the patient is distracted",
  correct=["Graves' disease", "thyrotoxic chorea", "hyperthyroidism"],
  partial=["thyrotoxicosis", "metabolic chorea", "hemichorea"],
  who=dict(age=73, sex="female"),
  yes=["involuntary movements of one leg", "the movements appear when distracted",
       "weight loss of about 4 kg over six months", "breathlessness on exertion",
       "fine finger tremor", "smoking", "the movements resolved on tablets for the thyroid"],
  no=["a family history of chorea or thyroid disease", "very high blood sugars",
      "recent vaccination", "a rash", "recent infection", "a palpable lump in the neck",
      "confusion or behavioural change", "weakness or sensory loss", "heavy alcohol use",
      "sudden onset"],
  inv={
   "TSH, free T4 and free T3": {"v": "TSH SUPPRESSED at <0.01 mIU/L (reference 0.50-5.00) and free "
                                     "thyroxine ELEVATED at 3.85 ng/dL (reference 0.90-1.70)",
                                "p": "reported", "decisive": True},
   "thyrotropin receptor antibodies (TRAb)": {"v": "ELEVATED at 7.4 IU/L (reference <2.0) - Graves' "
                                                   "disease", "p": "reported", "decisive": True},
   "thyroid ultrasound": {"v": "no nodules; estimated thyroid weight 13 g; 99mTc scintigraphy "
                               "showed diffuse uptake consistent with Graves' disease",
                          "p": "reported", "decisive": True},
   "CT head (non-contrast)": {"v": "unremarkable - excludes a structural cause", "p": "reported"},
   "blood glucose": {"v": "normal glucose and electrolytes - excludes hyperglycaemic chorea",
                     "p": "reported", "decisive": True},
   "effect of voluntary action and anxiety": {"v": "the movements were evident when the patient "
                                                   "became DISTRACTED", "p": "reported"},
   "trial of antithyroid treatment": {"v": "methimazole; the chorea resolved after about one month "
                                           "as thyroid function improved", "p": "reported",
                                      "tier": "bedside", "decisive": True},
  },
  dont_miss="Thyroid function belongs in every chorea work-up; thyrotoxic chorea is fully "
            "reversible with antithyroid treatment and the gland may not be palpably enlarged.",
  must_not="dismissing a normal-sized thyroid as evidence against thyrotoxicosis"),

 dict(
  video="c_9122005.mp4", pmcid="PMC9122005",
  dx="COVID-19 VACCINE-INDUCED hemichorea-hemiballismus after the second Pfizer-BioNTech dose, "
     "with putaminal hypermetabolism that normalised after corticosteroids",
  sign="large flinging movements of one arm and leg",
  correct=["vaccine-induced hemichorea-hemiballismus", "post-vaccination autoimmune chorea",
           "immune-mediated hemiballismus"],
  partial=["hemichorea-hemiballism", "autoimmune chorea", "hyperglycaemic chorea"],
  who=dict(age=90, sex="male"),
  yes=["large flinging movements of one arm and leg", "the face is involved on the same side",
       "the movements are worse with voluntary action", "the movements are worse with anxiety",
       "the movements decrease during sleep", "slurred speech",
       "a COVID-19 vaccination three weeks earlier", "this was the second dose",
       "high blood pressure", "an irregular heartbeat", "a previous heart attack",
       "the movements improved after a five-day treatment"],
  no=["very high blood sugars", "a family history of chorea", "a known cancer", "fever",
      "recent infection", "a rash", "thyroid symptoms", "weakness or numbness",
      "gradual onset over months"],
  inv={
   "medication and vaccination history": {"v": "second dose of the Pfizer-BioNTech COVID-19 "
                                               "vaccine 21 days after the first; symptoms began "
                                               "acutely afterwards", "p": "reported",
                                          "decisive": True},
   "FDG-PET brain": {"v": "INCREASED right putamen fixation compared with the left; NORMALISED "
                          "after corticosteroids, mirroring the clinical course", "p": "reported",
                     "decisive": True},
   "brain MRI with contrast": {"v": "no lesion and no abnormal signal in the basal ganglia",
                               "p": "reported", "decisive": True},
   "blood glucose": {"v": "NORMAL - no diabetes and no hyperglycaemia", "p": "reported",
                     "decisive": True},
   "lumbar puncture / CSF": {"v": "intrathecal immunoglobulin synthesis with oligoclonal bands; "
                                  "otherwise normal", "p": "reported", "decisive": True},
   "autoimmune encephalopathy / paraneoplastic antibody panel": {"v": "onconeuronal antibodies "
                                                                     "negative in serum and CSF",
                                                                 "p": "reported"},
   "trial of immunotherapy": {"v": "five days of intravenous corticosteroids with significant "
                                   "improvement; he could sit in a chair and start physiotherapy "
                                   "ten days later", "p": "reported", "decisive": True},
   "effect of sleep": {"v": "the movements decreased during sleep", "p": "reported"},
  },
  dont_miss="A new hemiballismus with normal glucose and normal structural imaging can still be "
            "immune-mediated; FDG-PET showed the striatal abnormality that MRI missed, and "
            "steroids reversed both.",
  must_not="attributing it to non-ketotic hyperglycaemia - the glucose is normal - or to a stroke, "
           "since the MRI shows no lesion"),

 dict(
  video="c_9815763.mp4", pmcid="PMC9815763",
  dx="Unilateral RIGHT upper limb chorea as a manifestation of GRAVES' HYPERTHYROIDISM, resolved "
     "with radioiodine",
  sign="continuous, rapid, irregular movements of one arm",
  correct=["hyperthyroid chorea", "Graves' disease", "thyrotoxicosis"],
  partial=["hemichorea", "metabolic chorea", "autoimmune thyroid disease"],
  who=dict(age=44, sex="female"),
  yes=["involuntary movements of the right arm", "the movements have lasted about a year",
       "the movements are continuous, rapid and irregular", "palpitations",
       "irritability", "anxiety", "a known overactive thyroid",
       "the thyroid problem has been poorly controlled", "taking a thyroid tablet already",
       "the movements resolved after definitive thyroid treatment"],
  no=["very high blood sugars", "a family history of chorea", "recent vaccination", "a rash",
      "a known cancer", "confusion or behavioural change", "recent infection", "fever",
      "the movements affect the legs", "sudden onset"],
  inv={
   "TSH, free T4 and free T3": {"v": "T3 8.26 nmol/L (normal 0.92-2.79) and free T4 58.13 pmol/L "
                                     "(normal 11.50-22.70) with suppressed TSH", "p": "reported",
                                "decisive": True},
   "thyrotropin receptor antibodies (TRAb)": {"v": "positive - Graves' disease diagnosed in April "
                                                   "2021 and treated with methimazole 10 mg daily",
                                              "p": "reported", "decisive": True},
   "trial of antithyroid treatment": {"v": "radioiodine (131-I); the chorea resolved",
                                      "p": "reported", "tier": "bedside", "decisive": True},
   "distribution of the movements (one side, both, face, limbs)": {"v": "unilateral right upper "
                                                                       "limb; chorea complicates "
                                                                       "under 2% of Graves' cases "
                                                                       "and the median age in the "
                                                                       "literature is 23",
                                                                  "p": "reported"},
  },
  dont_miss="Hyperthyroid chorea can be the presenting sign and persists while the thyroid stays "
            "uncontrolled; definitive treatment resolves it, so recheck thyroid function even "
            "when a diagnosis is already known.",
  must_not="treating the chorea symptomatically while leaving the thyrotoxicosis uncontrolled"),

 dict(
  video="hg_11283634.mp4", pmcid="PMC11283634",
  dx="BILATERAL chorea-ballism from non-ketotic hyperglycaemia in poorly controlled type 2 "
     "diabetes, with chronic kidney impairment",
  sign="violent generalized flinging movements, worse on one side",
  correct=["non-ketotic hyperglycaemic chorea", "diabetic striatopathy",
           "hyperglycaemia-induced chorea-ballism"],
  partial=["chorea-ballism", "metabolic chorea", "hyperglycaemia"],
  who=dict(age=66, sex="female"),
  yes=["violent flinging movements", "the movements affect both sides",
       "the movements are worse on the left", "type 2 diabetes on tablets",
       "high blood pressure", "a recent hospital admission for a diabetic emergency",
       "the movements came back after that admission",
       "the movements improved as the blood sugar came down"],
  no=["a family history of neurological disorders", "thyroid symptoms", "recent vaccination",
      "a rash", "confusion or behavioural change", "recent infection", "fever",
      "a known cancer", "heavy alcohol use", "one-sided movements only"],
  inv={
   "blood glucose": {"v": "2.25 g/L (normal 0.70-1.10) - non-ketotic hyperglycaemia",
                     "p": "reported", "decisive": True},
   "HbA1c": {"v": "7.8% with long-standing poor control", "p": "reported", "decisive": True},
   "ketones (blood or urine)": {"v": "negative - a treated ketoacidosis had preceded this "
                                     "admission", "p": "reported", "decisive": True},
   "renal function and eGFR": {"v": "creatinine 17 mg/L (normal 7-14) with eGFR 31 mL/min/1.73 m2",
                               "p": "reported"},
   "distribution of the movements (one side, both, face, limbs)": {"v": "generalized "
                                                                       "chorea-ballism, more "
                                                                       "severe on the LEFT",
                                                                  "p": "reported"},
   "gait and coordination": {"v": "right-sided dysmetria on finger-nose testing, difficult to "
                                  "assess given the severity of the movements", "p": "reported"},
   "trial of glucose correction with insulin": {"v": "symptoms improved significantly with "
                                                     "normalisation of blood glucose",
                                                "p": "reported", "decisive": True},
  },
  dont_miss="Hyperglycaemic chorea can be bilateral and violent; correcting the glucose is the "
            "treatment, and postmenopausal women are the group most often affected.",
  must_not="assuming bilateral chorea excludes a metabolic cause and jumping to Huntington "
           "disease"),

 dict(
  video="hg_7055013.mp4", pmcid="PMC7055013",
  dx="RIGHT hemichorea induced by non-ketotic hyperglycaemia in a Caucasian woman with type 2 "
     "diabetes; it settled on insulin",
  sign="continuous one-sided writhing movements of the limbs",
  correct=["non-ketotic hyperglycaemic hemichorea", "diabetic striatopathy",
           "hyperglycaemia-induced chorea"],
  partial=["hemichorea", "metabolic chorea", "stroke"],
  who=dict(age=76, sex="female"),
  yes=["one-sided involuntary movements", "the face is involved as well as the limbs",
       "slurred speech", "unsteady walking", "the symptoms developed over two to three weeks",
       "type 2 diabetes", "high blood pressure", "a previous stroke",
       "a previous breast cancer", "previous seizures",
       "the movements settled after insulin treatment"],
  no=["a family history of chorea", "thyroid symptoms", "recent vaccination", "a rash",
      "confusion or behavioural change", "recent infection", "fever", "heavy alcohol use",
      "sudden onset in a single moment", "the movements affect both sides equally"],
  inv={
   "blood glucose": {"v": "690 mg/dL with a NORMAL anion gap", "p": "reported", "decisive": True},
   "HbA1c": {"v": "14.7%", "p": "reported", "decisive": True},
   "ketones (blood or urine)": {"v": "negative - non-ketotic", "p": "reported", "decisive": True},
   "CT head (non-contrast)": {"v": "HYPERDENSITY in the LEFT basal ganglia with mild involvement "
                                   "of the right basal ganglia - contralateral to the chorea",
                              "p": "reported", "decisive": True},
   "trial of glucose correction with insulin": {"v": "insulin alleviated her symptoms",
                                                "p": "reported", "decisive": True},
   "distribution of the movements (one side, both, face, limbs)": {"v": "right-sided hemichorea of "
                                                                       "the face and limbs",
                                                                  "p": "reported"},
  },
  dont_miss="A hyperdense basal ganglion on plain CT with a very high glucose is diabetic "
            "striatopathy, not a haemorrhage; the treatment is insulin, not neurosurgery.",
  must_not="reading the basal-ganglia hyperdensity as an acute haemorrhage"),

 dict(
  video="hyperglycemic_hemichorea_PMC12596229.mp4", pmcid="PMC12596229",
  dx="Hemichorea-hemiballism from DIABETIC STRIATOPATHY occurring together with a LACUNAR STROKE - "
     "two causes in the same patient",
  sign="one-sided flinging and writhing movements of the arm and leg",
  correct=["diabetic striatopathy with lacunar stroke", "hyperglycaemic hemichorea-hemiballism",
           "hemichorea from combined metabolic and vascular causes"],
  partial=["hemichorea-hemiballism", "diabetic striatopathy", "lacunar stroke"],
  who=dict(age=62, sex="male"),
  yes=["involuntary movements of the right arm and leg", "acute onset",
       "very high blood sugars", "sugar in the urine", "excessive thirst",
       "the movements are on one side only", "high blood pressure",
       "the symptoms improved as the sugar came down"],
  no=["a family history of chorea", "thyroid symptoms", "recent vaccination", "a rash",
      "confusion or behavioural change", "recent infection", "fever", "a known cancer",
      "heavy alcohol use", "ketones in the urine"],
  inv={
   "blood glucose": {"v": "30.63 mmol/L (551.3 mg/dL) with glycosuria and NO ketonuria",
                     "p": "reported", "decisive": True},
   "HbA1c": {"v": "very high on admission; 5.73% at first follow-up once glucose was controlled",
             "p": "reported", "decisive": True},
   "CT head (non-contrast)": {"v": "HYPERDENSE LEFT caudate and lentiform nucleus - contralateral "
                                   "to the movements", "p": "reported", "decisive": True},
   "brain MRI with contrast": {"v": "a coexisting LACUNAR INFARCT in addition to the striatal "
                                    "signal change", "p": "reported", "decisive": True},
   "vital signs": {"v": "blood pressure 140/80 mmHg, pulse 78, oxygen saturation 98% on air",
                   "p": "reported"},
   "trial of glucose correction with insulin": {"v": "glucose fell to 5.9 mmol/L (106.2 mg/dL) at "
                                                     "follow-up with improvement in the movements",
                                                "p": "reported", "decisive": True},
  },
  dont_miss="Hyperglycaemia and a basal-ganglia stroke can coexist; finding one does not excuse "
            "you from looking for the other, and both need treating.",
  must_not="stopping at the hyperglycaemia and not imaging for the stroke, or vice versa"),
]

build(LINE, PANEL, CASES)
