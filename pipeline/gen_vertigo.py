"""Central eye-movement cases, rebuilt on documented aetiologies.

Every case here is diagnosed from where the eye sign localises, so the panel keeps the bedside
oculomotor examination as separate, individually orderable items - a doctor who asks the right
bedside question can get most of the way before ordering an MRI, which is the behaviour worth
measuring.

Three labels changed: the see-saw case is a pontine and thalamic infarct rather than a sellar
mass, the pseudo-INO case is orbital trauma rather than a brainstem lesion, and the flutter case
is anti-GT1a rather than anti-GQ1b.
"""
from genlib import build

LINE = "vertigo_central"

PANEL = {
    "nystagmus: direction and whether it changes with gaze": {"v": "no nystagmus", "p": "derived",
                                                              "tier": "bedside"},
    "smooth pursuit and saccades": {"v": "normal", "p": "derived", "tier": "bedside"},
    "adduction in horizontal gaze (each eye)": {"v": "full", "p": "derived", "tier": "bedside"},
    "abducting nystagmus of the fellow eye": {"v": "absent", "p": "derived", "tier": "bedside"},
    "vertical gaze and convergence": {"v": "normal", "p": "derived", "tier": "bedside"},
    "skew deviation / alternating cover test": {"v": "no vertical misalignment", "p": "derived",
                                                "tier": "bedside"},
    "ocular torsion and head tilt": {"v": "none", "p": "derived", "tier": "bedside"},
    "subjective visual vertical": {"v": "within normal limits", "p": "derived", "tier": "bedside"},
    "head impulse test": {"v": "normal - no corrective saccade", "p": "derived", "tier": "bedside"},
    "pupil size and light reaction": {"v": "equal and reactive", "p": "derived", "tier": "bedside"},
    "ptosis / lid position": {"v": "none", "p": "derived", "tier": "bedside"},
    "limb and truncal ataxia": {"v": "absent", "p": "derived", "tier": "bedside"},
    "gait and tandem walking": {"v": "normal", "p": "derived", "tier": "bedside"},
    "hearing and tinnitus": {"v": "normal", "p": "derived", "tier": "bedside"},
    "facial dysmorphism and general examination": {"v": "unremarkable", "p": "derived",
                                                   "tier": "bedside"},
    "full blood count and biochemistry": {"v": "normal", "p": "derived", "tier": "blood"},
    "glucose / HbA1c": {"v": "normal", "p": "derived", "tier": "blood"},
    "lipids and vascular risk assessment": {"v": "normal", "p": "derived", "tier": "blood"},
    "ESR / CRP": {"v": "normal", "p": "derived", "tier": "blood"},
    "anti-ganglioside antibodies (GQ1b, GT1a, GM1, GM2)": {"v": "all negative", "p": "derived",
                                                           "tier": "blood"},
    "paraneoplastic and autoimmune antibody panel (serum)": {"v": "negative", "p": "derived",
                                                             "tier": "blood"},
    "anti-acetylcholine receptor antibodies": {"v": "negative", "p": "derived", "tier": "blood"},
    "TSH / free T4": {"v": "normal", "p": "derived", "tier": "blood"},
    "genetic testing (exome)": {"v": "no pathogenic variant", "p": "derived", "tier": "blood"},
    "MRI brain with DWI": {"v": "no acute infarct, no lesion", "p": "derived", "tier": "imaging"},
    "MRI sella and orbits": {"v": "normal pituitary and orbits", "p": "derived", "tier": "imaging"},
    "CT head (non-contrast)": {"v": "normal", "p": "derived", "tier": "imaging"},
    "CT / MR angiography (posterior circulation)": {"v": "normal", "p": "derived",
                                                    "tier": "imaging"},
    "CT chest / abdomen / pelvis (occult tumour)": {"v": "no malignancy", "p": "derived",
                                                    "tier": "imaging"},
    "visual fields (perimetry)": {"v": "full", "p": "derived", "tier": "imaging"},
    "lumbar puncture / CSF": {"v": "normal cells and protein; no oligoclonal bands",
                              "p": "derived", "tier": "invasive"},
    "CSF metagenomic sequencing": {"v": "no pathogen sequences", "p": "derived",
                                   "tier": "invasive"},
    "EEG": {"v": "normal", "p": "derived", "tier": "invasive"},
    "forced duction test": {"v": "not performed", "p": "derived", "tier": "invasive"},
}

CASES = [
 dict(
  video="mild_1_seesaw_INO_PMC6883617.mp4", pmcid="PMC6883617",
  dx="See-saw nystagmus WITH internuclear ophthalmoplegia from bilateral dorsomedial pontine and "
     "left thalamic INFARCTION",
  sign="one eye rises and intorts while the other falls and extorts, alternating",
  correct=["brainstem/thalamic infarction", "pontine and thalamic stroke",
           "see-saw nystagmus from a brainstem infarct"],
  partial=["see-saw nystagmus", "internuclear ophthalmoplegia", "parasellar mass"],
  who=dict(age=62, sex="male"),
  yes=["sudden onset", "dizziness", "double vision", "difficulty walking",
       "high blood pressure for ten years", "diabetes",
       "one eye does not turn inwards on looking to the side",
       "the symptoms recovered almost completely"],
  no=["gradual onset over months", "loss of side vision", "headache",
      "a family history of a similar illness", "recent infection", "cancer", "hearing loss",
      "fever", "eye pain", "recent head injury"],
  inv={
   "nystagmus: direction and whether it changes with gaze": {"v": "see-saw nystagmus",
                                                             "p": "reported", "decisive": True},
   "adduction in horizontal gaze (each eye)": {"v": "adduction paresis of the LEFT eye with "
                                                    "dissociated abducting paresis of the right "
                                                    "eye on rightward gaze - internuclear "
                                                    "ophthalmoplegia", "p": "reported",
                                               "decisive": True},
   "MRI brain with DWI": {"v": "bilateral dorsomedial PONTINE and LEFT THALAMIC infarction",
                          "p": "reported", "decisive": True},
   "CT / MR angiography (posterior circulation)": {"v": "slender left anterior cerebral artery and "
                                                       "stenosis of the ipsilateral posterior "
                                                       "cerebral artery", "p": "reported"},
   "glucose / HbA1c": {"v": "fasting glucose 10.88 mmol/L (ref 3.89-6.11) and HbA1c 9% (ref 4-6) "
                            "- uncontrolled diabetes", "p": "reported"},
   "MRI sella and orbits": {"v": "normal - no parasellar or suprasellar mass", "p": "derived",
                            "decisive": True},
   "visual fields (perimetry)": {"v": "FULL - no bitemporal hemianopia, so no chiasmal "
                                      "compression", "p": "derived"},
  },
  dont_miss="See-saw nystagmus is central, and the accompanying INO localises it to the pons - "
            "this is a posterior-circulation stroke needing urgent DWI and secondary prevention, "
            "not a pituitary work-up.",
  must_not="attributing it to a suprasellar mass compressing the chiasm; a sellar lesion cannot "
           "produce the INO and the visual fields are full"),

 dict(
  video="mild_2_cerebellar_antiHomer3_PMC12833086.mp4", pmcid="PMC12833086",
  dx="Autoimmune cerebellar ataxia with anti-Homer3 antibodies, triggered by human herpesvirus 7 "
     "infection; relapsed and required rituximab",
  sign="gaze-evoked nystagmus with saccadic eye-movement abnormalities",
  correct=["anti-Homer3 autoimmune cerebellar ataxia", "autoimmune cerebellitis",
           "post-infectious autoimmune cerebellar ataxia"],
  partial=["cerebellar ataxia", "gaze-evoked nystagmus", "autoimmune encephalitis"],
  who=dict(age=15, sex="female"),
  yes=["dizziness", "unsteady walking", "symptoms progressed over a month",
       "generalized seizures", "the symptoms improved with immune treatment",
       "the symptoms came back after initially improving", "being a teenager"],
  no=["headache", "ringing in the ears", "hearing loss", "visual disturbance", "sudden onset",
      "a family history of a similar illness", "cancer", "high blood pressure",
      "double vision", "limb weakness"],
  inv={
   "paraneoplastic and autoimmune antibody panel (serum)": {"v": "anti-Homer3 antibodies POSITIVE",
                                                            "p": "reported", "decisive": True},
   "CSF metagenomic sequencing": {"v": "eight sequences of HUMAN HERPESVIRUS 7", "p": "reported",
                                  "decisive": True},
   "lumbar puncture / CSF": {"v": "inflammatory changes", "p": "reported"},
   "immunotherapy trial": {"v": "dizziness and gait improved with immunotherapy; relapse "
                                "prompted rituximab, with partial improvement", "p": "reported",
                           "tier": "invasive", "decisive": True},
   "EEG": {"v": "abnormal - three episodes of generalized seizures occurred", "p": "reported"},
   "hearing and tinnitus": {"v": "she specifically denied tinnitus and hearing impairment",
                            "p": "reported"},
  },
  dont_miss="Subacute cerebellar ataxia in a young patient is autoimmune until proven otherwise; "
            "send neuronal antibodies and CSF metagenomics, because immunotherapy works and "
            "relapse needs escalation.",
  must_not="calling it a post-viral labyrinthitis or a functional disorder - the antibody and the "
           "inflammatory CSF are the diagnosis"),

 dict(
  video="mild_3_joubert_apraxia_PMC8490194.mp4", pmcid="PMC8490194",
  dx="JOUBERT SYNDROME - cerebellar vermis hypoplasia with the molar tooth sign, presenting with "
     "ocular motor apraxia, facial dysmorphism and ataxia",
  sign="inability to start voluntary sideways eye movements, with compensatory head thrusts",
  correct=["Joubert syndrome", "molar tooth sign", "cerebellar vermis hypoplasia"],
  partial=["congenital ocular motor apraxia", "ciliopathy", "congenital ataxia"],
  who=dict(age=2, sex="male"),
  yes=["the eyes cannot start moving sideways on command", "the head jerks to help the eyes move",
       "unsteadiness", "developmental delay", "unusual facial features",
       "a broad nasal bridge", "low-set ears", "abnormal breathing pattern as a baby",
       "parents who are related to each other", "the problem has been present since infancy"],
  no=["sudden onset", "recent infection", "headache", "double vision", "hearing loss",
      "the symptoms fluctuate", "high blood pressure", "cancer", "limb weakness",
      "the symptoms improved with steroids"],
  inv={
   "MRI brain with DWI": {"v": "MOLAR TOOTH SIGN with cerebellar vermis hypoplasia and "
                               "horizontally aligned superior cerebellar peduncles",
                          "p": "reported", "decisive": True},
   "facial dysmorphism and general examination": {"v": "facial dysmorphism in all patients - broad "
                                                       "nasal bridge and low-set ears most common",
                                                  "p": "reported", "decisive": True},
   "smooth pursuit and saccades": {"v": "ocular motor apraxia - failure to initiate voluntary "
                                        "horizontal saccades with compensatory head thrusts",
                                   "p": "reported", "decisive": True},
   "skew deviation / alternating cover test": {"v": "ocular tilt reaction and alternate skew "
                                                    "deviation in 66% of the cohort",
                                               "p": "reported"},
   "genetic testing (exome)": {"v": "pathogenic variants in ciliopathy genes on exome sequencing",
                               "p": "reported", "decisive": True},
   "diffusion tensor imaging": {"v": "horizontally aligned superior cerebellar peduncles with "
                                     "lack of decussation", "p": "reported", "tier": "imaging"},
   "renal and retinal screening": {"v": "required - ciliopathies involve kidney and retina",
                                   "p": "derived", "tier": "imaging"},
  },
  dont_miss="Ocular motor apraxia with head thrusts in a developmentally delayed child means "
            "imaging for the molar tooth sign; Joubert syndrome needs kidney and retinal "
            "surveillance and genetic counselling.",
  must_not="calling it a benign delay in visual maturation - the imaging is diagnostic and the "
           "systemic screening matters"),

 dict(
  video="moderate_1_ocular_flutter_PMC12979508.mp4", pmcid="PMC12979508",
  dx="Anti-GT1a IgG antibody-associated ocular flutter with mild ataxia, following an upper "
     "respiratory tract infection - a Guillain-Barre spectrum disorder",
  sign="bursts of rapid horizontal back-to-back eye oscillations",
  correct=["anti-GT1a antibody-associated ocular flutter", "post-infectious ocular flutter",
           "Guillain-Barre spectrum disorder"],
  partial=["ocular flutter", "Miller Fisher syndrome", "opsoclonus-myoclonus syndrome"],
  who=dict(age=26, sex="female"),
  yes=["blurred vision of sudden onset", "dizziness", "difficulty focusing the eyes",
       "unsteady walking", "an upper respiratory infection shortly before",
       "the symptoms began about five days ago", "clumsiness of the limbs"],
  no=["limb weakness", "numbness", "difficulty swallowing", "slurred speech", "double vision",
      "seizures", "a family history of a similar illness", "cancer",
      "a previous autoimmune disease", "headache"],
  inv={
   "anti-ganglioside antibodies (GQ1b, GT1a, GM1, GM2)": {"v": "ISOLATED anti-GT1a IgG POSITIVE; "
                                                              "anti-GQ1b, anti-GM1 and anti-GM2 "
                                                              "all NEGATIVE", "p": "reported",
                                                          "decisive": True},
   "smooth pursuit and saccades": {"v": "rapid conjugate HORIZONTAL saccadic oscillations WITHOUT "
                                        "intersaccadic intervals - ocular flutter", "p": "reported",
                                   "decisive": True},
   "limb and truncal ataxia": {"v": "truncal ataxia, mild dysmetria and an ataxic gait",
                               "p": "reported"},
   "paraneoplastic and autoimmune antibody panel (serum)": {"v": "negative", "p": "reported"},
   "MRI brain with DWI": {"v": "no acute lesion", "p": "derived"},
   "CT chest / abdomen / pelvis (occult tumour)": {"v": "no malignancy - argues against a "
                                                       "paraneoplastic cause", "p": "derived",
                                                   "decisive": True},
  },
  dont_miss="Ocular flutter after an infection is a treatable immune-mediated syndrome; send the "
            "full ganglioside panel, because anti-GT1a can be positive when anti-GQ1b is not.",
  must_not="requiring anti-GQ1b positivity before accepting a Guillain-Barre spectrum diagnosis, "
           "or assuming a paraneoplastic cause without a tumour"),

 dict(
  video="moderate_2_opsoclonus_PMC13135425.mp4", pmcid="PMC13135425",
  dx="IDIOPATHIC opsoclonus-myoclonus syndrome in an adult, diagnosed only after three emergency "
     "department visits in five days; treated with methylprednisolone and immunoglobulin",
  sign="chaotic multidirectional back-to-back eye movements",
  correct=["opsoclonus-myoclonus syndrome", "idiopathic opsoclonus-myoclonus"],
  partial=["opsoclonus", "ocular flutter", "paraneoplastic opsoclonus"],
  who=dict(age=53, sex="female"),
  yes=["the eyes dart back and forth", "trouble focusing the vision",
       "difficulty walking", "needing family help to walk", "symptoms worsened over five days",
       "having been to the emergency department more than once for this",
       "jerky movements of the body", "a history of migraine",
       "the symptoms improved with steroids and immunoglobulin"],
  no=["a known cancer", "weight loss", "night sweats", "fever", "recent infection",
      "a family history of a similar illness", "limb weakness", "double vision", "hearing loss",
      "sudden onset in a single moment"],
  inv={
   "smooth pursuit and saccades": {"v": "opsoclonus - chaotic multidirectional saccades without "
                                        "intersaccadic intervals", "p": "reported",
                                   "decisive": True},
   "CT head (non-contrast)": {"v": "no acute findings", "p": "reported"},
   "MRI brain with DWI": {"v": "no acute findings", "p": "reported"},
   "lumbar puncture / CSF": {"v": "unremarkable", "p": "reported"},
   "paraneoplastic and autoimmune antibody panel (serum)": {"v": "unremarkable", "p": "reported",
                                                            "decisive": True},
   "CT chest / abdomen / pelvis (occult tumour)": {"v": "no tumour found - idiopathic rather than "
                                                       "paraneoplastic", "p": "reported",
                                                   "decisive": True},
   "immunotherapy trial": {"v": "IV methylprednisolone and IV immunoglobulin followed by oral "
                                "prednisone; myoclonus and ataxia resolved and opsoclonus "
                                "improved; about 80% back to baseline at three months",
                           "p": "reported", "tier": "invasive", "decisive": True},
   "propranolol trial": {"v": "improved the residual end-point tremor", "p": "reported",
                         "tier": "bedside"},
  },
  dont_miss="Adult opsoclonus-myoclonus averages eleven weeks to diagnosis and is commonly sent "
            "home as vertigo; recognise the eye movement, search for a tumour, and start "
            "immunotherapy without waiting for antibodies.",
  must_not="calling it nystagmus and discharging the patient - normal CT and MRI do not exclude "
           "this diagnosis"),

 dict(
  video="moderate_3_pendular_antiMa2_PMC11102397.mp4", pmcid="PMC11102397",
  dx="Anti-Ma2 paraneoplastic encephalitis presenting with ISOLATED pendular torsional nystagmus, "
     "in a woman with non-small cell lung cancer on the checkpoint inhibitor durvalumab",
  sign="a continuous to-and-fro torsional oscillation of the eyes",
  correct=["anti-Ma2 encephalitis", "paraneoplastic encephalitis",
           "checkpoint inhibitor neurological adverse event"],
  partial=["pendular nystagmus", "paraneoplastic nystagmus", "brainstem encephalitis"],
  who=dict(age=71, sex="female"),
  yes=["the world seems to move or oscillate", "imbalance",
       "the symptoms worsened over about three weeks", "lung cancer",
       "being treated with an immunotherapy drug for the cancer",
       "the symptoms began after several cycles of that drug", "a cough and breathlessness "
       "before the cancer was found", "coughing up blood"],
  no=["clumsiness on finger-to-nose testing", "unsteadiness of the trunk when sitting",
      "double vision", "limb weakness", "headache", "seizures", "fever", "recent infection",
      "a family history of a similar illness", "hearing loss"],
  inv={
   "nystagmus: direction and whether it changes with gaze": {"v": "PENDULAR TORSIONAL nystagmus, "
                                                                 "isolated", "p": "reported",
                                                             "decisive": True},
   "paraneoplastic and autoimmune antibody panel (serum)": {"v": "ANTI-MA2 antibodies detected in "
                                                                "BOTH serum and CSF, with the "
                                                                "typical neuronal nucleolar "
                                                                "staining pattern", "p": "reported",
                                                            "decisive": True},
   "lumbar puncture / CSF": {"v": "CSF-restricted oligoclonal bands", "p": "reported",
                             "decisive": True},
   "limb and truncal ataxia": {"v": "finger-to-nose and heel-to-shin NORMAL and no truncal ataxia "
                                    "- the nystagmus is isolated", "p": "reported"},
   "CT chest / abdomen / pelvis (occult tumour)": {"v": "bulky perihilar mass in the left upper "
                                                       "lung with vascular and mediastinal "
                                                       "invasion and ipsilateral lymphadenopathy",
                                                   "p": "reported", "decisive": True},
   "medication and oncology history": {"v": "anti-PD-L1 durvalumab; symptoms began suddenly after "
                                            "the seventh administration", "p": "reported",
                                       "tier": "bedside", "decisive": True},
  },
  dont_miss="A new eye-movement disorder in a patient on a checkpoint inhibitor is a neurological "
            "immune-related adverse event until proven otherwise - send paired serum and CSF "
            "antibodies and stop the drug.",
  must_not="dismissing an isolated nystagmus as benign because the limb coordination is normal"),

 dict(
  video="severe_1_ocular_tilt_PMC8061496.mp4", pmcid="PMC8061496",
  dx="Left PONTO-MESENCEPHALIC INFARCTION producing the complete ocular tilt reaction with "
     "ipsilesional torsional nystagmus, internuclear ophthalmoplegia and lateral alternating skew "
     "deviation, from a top-of-the-basilar occlusion",
  sign="vertical misalignment of the eyes with ocular torsion and a head tilt",
  correct=["brainstem infarction", "ponto-mesencephalic stroke", "ocular tilt reaction from a "
           "brainstem infarct"],
  partial=["ocular tilt reaction", "skew deviation", "vestibular syndrome"],
  who=dict(age=64, sex="male"),
  yes=["sudden onset", "the head tilts to one side", "double vision",
       "clumsiness of the left limbs", "dizziness", "the world seems tilted"],
  no=["hearing loss", "ringing in the ears", "gradual onset over months", "headache",
      "recent infection", "fever", "a family history of a similar illness", "cancer",
      "recent head injury", "eye pain"],
  inv={
   "skew deviation / alternating cover test": {"v": "skew deviation with LATERAL ALTERNATION - "
                                                    "right eye hypotropic, left eye hypertropic",
                                               "p": "reported", "decisive": True},
   "ocular torsion and head tilt": {"v": "RIGHT-sided head tilt; right eye excyclotorted and left "
                                         "eye incyclotorted - the complete ocular tilt reaction",
                                    "p": "reported", "decisive": True},
   "subjective visual vertical": {"v": "deviated by about 4 degrees", "p": "reported"},
   "nystagmus: direction and whether it changes with gaze": {"v": "ipsilesional torsional "
                                                                 "nystagmus", "p": "reported",
                                                             "decisive": True},
   "limb and truncal ataxia": {"v": "left-sided limb ataxia", "p": "reported"},
   "MRI brain with DWI": {"v": "LEFT rostral pontine infarct and a caudal mesencephalic infarct "
                               "extending along the paramedian line to the midline",
                          "p": "reported", "decisive": True},
   "CT / MR angiography (posterior circulation)": {"v": "TOP-OF-THE-BASILAR OCCLUSION; "
                                                       "thrombectomy was deferred as he was well "
                                                       "preserved", "p": "reported",
                                                   "decisive": True},
  },
  dont_miss="Skew deviation with ocular torsion and a head tilt is a brainstem sign, not "
            "peripheral vertigo; this patient had a basilar occlusion and needed immediate "
            "vascular imaging.",
  must_not="treating it as vestibular neuritis - a head impulse test alone will not exclude a "
           "brainstem stroke when skew is present"),

 dict(
  video="severe_2_pseudoINO_PMC13186686.mp4", pmcid="PMC13186686",
  dx="TRAUMATIC PSEUDO-internuclear ophthalmoplegia from a suspected medial rectus injury with a "
     "medial orbital wall fracture, after a motor vehicle accident; it resolved conservatively "
     "over two weeks",
  sign="one eye fails to adduct while the other shows abducting nystagmus, with a dressing over "
       "the nose",
  correct=["traumatic pseudo-internuclear ophthalmoplegia", "medial rectus injury",
           "orbital wall fracture"],
  partial=["internuclear ophthalmoplegia", "orbital trauma", "brainstem lesion"],
  who=dict(age=34, sex="male"),
  yes=["double vision when looking to one side", "a recent motor vehicle accident",
       "severe head injury with loss of consciousness", "a dressing on the face",
       "the right eye will not turn inwards", "the problem improved over about two weeks"],
  no=["gradual onset", "the droop gets worse through the day", "limb weakness",
      "slurred speech", "a previous similar episode", "a family history of a similar illness",
      "recent infection", "fever", "cancer", "any other neurological symptom"],
  inv={
   "adduction in horizontal gaze (each eye)": {"v": "limited adduction of the RIGHT eye that fails "
                                                   "to cross the midline, with abducting nystagmus "
                                                   "of the left eye on left gaze - mimics an INO",
                                              "p": "reported", "decisive": True},
   "CT head (non-contrast)": {"v": "multiple skull fractures and epidural haemorrhage; NO evidence "
                                   "of brainstem injury", "p": "reported", "decisive": True},
   "MRI sella and orbits": {"v": "subtle MEDIAL ORBITAL WALL FRACTURE with medial rectus "
                                 "involvement; no brainstem pathology", "p": "reported",
                            "decisive": True},
   "forced duction test": {"v": "restriction consistent with a mechanical cause", "p": "derived",
                           "decisive": True},
   "anti-acetylcholine receptor antibodies": {"v": "negative - excludes ocular myasthenia, the "
                                                  "commonest cause of pseudo-INO", "p": "derived"},
   "clinical course": {"v": "managed conservatively with gradual improvement in motility and "
                            "resolution of diplopia over two weeks", "p": "reported",
                       "tier": "bedside"},
   "Glasgow Coma Scale on arrival": {"v": "E1V1M1, improving to E1VTM4 after resuscitation",
                                     "p": "reported", "tier": "bedside"},
  },
  dont_miss="An INO pattern is not automatically central: ask about trauma, look at the face, and "
            "image the ORBIT - a medial wall fracture reproduces the sign exactly and needs no "
            "stroke pathway.",
  must_not="diagnosing a brainstem MLF lesion - imaging shows no brainstem injury, and the "
           "recovery over two weeks fits a mechanical cause"),

 dict(
  video="severe_3_oculomotor_palsy_PMC12745546.mp4", pmcid="PMC12745546",
  dx="PUPIL-SPARING partial oculomotor palsy from a small dorsal paramedian MIDBRAIN INFARCT with "
     "ipsilateral medial longitudinal fasciculus involvement - not diabetic microvascular palsy",
  sign="partial ptosis with impaired adduction and equally reactive pupils",
  correct=["midbrain infarction", "brainstem stroke",
           "pupil-sparing third nerve palsy from a midbrain infarct"],
  partial=["oculomotor nerve palsy", "diabetic third nerve palsy", "internuclear ophthalmoplegia"],
  who=dict(age=63, sex="male"),
  yes=["sudden onset", "horizontal double vision", "a drooping eyelid",
       "the eye will not turn inwards", "the double vision is painless",
       "difficulty focusing on near objects"],
  no=["eye pain", "the worst headache of her life", "neck stiffness", "unequal pupils",
      "the droop gets worse through the day", "recent head injury", "fever", "recent infection",
      "a previous similar episode", "cancer"],
  inv={
   "pupil size and light reaction": {"v": "pupils EQUALLY REACTIVE - pupil-sparing", "p": "reported",
                                     "decisive": True},
   "adduction in horizontal gaze (each eye)": {"v": "on left gaze the right eye fails to adduct, "
                                                   "and the contralateral eye shows NO abducting "
                                                   "nystagmus - unlike a classic INO",
                                              "p": "reported", "decisive": True},
   "ptosis / lid position": {"v": "partial ptosis", "p": "reported"},
   "vertical gaze and convergence": {"v": "mild vertical limitation and mildly impaired "
                                          "convergence", "p": "reported"},
   "MRI brain with DWI": {"v": "small DORSAL PARAMEDIAN MIDBRAIN INFARCT on diffusion-weighted "
                               "imaging", "p": "reported", "decisive": True},
   "diffusion tensor tractography": {"v": "reduced integrity of the IPSILATERAL medial "
                                          "longitudinal fasciculus", "p": "reported",
                                     "tier": "imaging", "decisive": True},
   "CT / MR angiography (circle of Willis)": {"v": "no aneurysm", "p": "derived", "decisive": True},
   "treatment": {"v": "dual antiplatelet therapy", "p": "reported", "tier": "bedside"},
  },
  dont_miss="Pupil-sparing does not mean microvascular: a small midbrain infarct produces the same "
            "pattern, so image with DWI rather than observing a presumed diabetic palsy.",
  must_not="attributing it to diabetic microvascular ischaemia and not imaging, or to an aneurysm "
           "- the pupil is spared and the angiogram is clear"),
]

build(LINE, PANEL, CASES)
