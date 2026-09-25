"""Eyelid and ocular-motility cases, rebuilt on documented aetiologies.

Two of the six change disease entirely. The clip labelled chronic progressive external
ophthalmoplegia is a myasthenia gravis patient with extraocular muscle atrophy, and the clip
labelled giant cell arteritis is a genetically confirmed CMT1H with cranial nerve involvement -
which is why that video also contains a heel-walking segment.

The line therefore ends up with two myasthenia cases. They are kept apart deliberately: one is
recognised by fatigability at the bedside, the other by muscle atrophy on orbital MRI in a
patient whose ophthalmoparesis did NOT respond to treatment.
"""
from genlib import build

LINE = "ptosis"

PANEL = {
    "lid position and measurement (MRD1 both sides)": {"v": "not recorded", "p": "derived",
                                                       "tier": "bedside"},
    "sustained upgaze fatigability test": {"v": "no fatigable droop", "p": "derived",
                                           "tier": "bedside"},
    "ice-pack test": {"v": "negative", "p": "derived", "tier": "bedside"},
    "ocular motility examination": {"v": "full in all directions", "p": "derived",
                                    "tier": "bedside"},
    "pupil examination (size, light reaction)": {"v": "equal and reactive", "p": "derived",
                                                 "tier": "bedside"},
    "cover test / ocular alignment": {"v": "orthophoric", "p": "derived", "tier": "bedside"},
    "visual acuity and colour vision": {"v": "normal", "p": "derived", "tier": "bedside"},
    "fundoscopy": {"v": "normal discs", "p": "derived", "tier": "bedside"},
    "proptosis / exophthalmometry": {"v": "no proptosis", "p": "derived", "tier": "bedside"},
    "pain and periorbital inspection": {"v": "no pain, no swelling, no discolouration",
                                        "p": "derived", "tier": "bedside"},
    "limb and neck power": {"v": "normal", "p": "derived", "tier": "bedside"},
    "vital signs": {"v": "normal, afebrile", "p": "derived", "tier": "bedside"},
    "anti-acetylcholine receptor antibodies": {"v": "negative", "p": "derived", "tier": "blood"},
    "anti-MuSK antibodies": {"v": "negative", "p": "derived", "tier": "blood"},
    "ESR / CRP": {"v": "normal", "p": "derived", "tier": "blood"},
    "full blood count": {"v": "normal", "p": "derived", "tier": "blood"},
    "glucose / HbA1c": {"v": "normal", "p": "derived", "tier": "blood"},
    "TSH / free T4 / TRAb": {"v": "normal, TRAb negative", "p": "derived", "tier": "blood"},
    "creatine kinase and lactate": {"v": "normal", "p": "derived", "tier": "blood"},
    "mitochondrial genetics (mtDNA deletion)": {"v": "no deletion", "p": "derived",
                                                "tier": "blood"},
    "whole exome sequencing": {"v": "no pathogenic variant", "p": "derived", "tier": "blood"},
    "SARS-CoV-2 test": {"v": "negative", "p": "derived", "tier": "blood"},
    "fungal culture / KOH of nasal tissue": {"v": "not performed", "p": "derived",
                                             "tier": "blood"},
    "MRI orbits": {"v": "normal extraocular muscles, no mass", "p": "derived", "tier": "imaging"},
    "MRI brain with contrast": {"v": "no lesion, no cranial nerve enhancement", "p": "derived",
                                "tier": "imaging"},
    "CT / MR angiography (circle of Willis)": {"v": "no aneurysm", "p": "derived",
                                               "tier": "imaging"},
    "CT sinuses": {"v": "clear sinuses", "p": "derived", "tier": "imaging"},
    "CT chest (thymus)": {"v": "no thymic mass", "p": "derived", "tier": "imaging"},
    "temporal artery ultrasound": {"v": "no halo sign", "p": "derived", "tier": "imaging"},
    "repetitive nerve stimulation": {"v": "no decrement", "p": "derived", "tier": "invasive"},
    "single-fibre EMG": {"v": "normal jitter", "p": "derived", "tier": "invasive"},
    "nerve conduction studies": {"v": "normal", "p": "derived", "tier": "invasive"},
    "lumbar puncture / CSF": {"v": "normal protein and cells", "p": "derived", "tier": "invasive"},
    "temporal artery biopsy": {"v": "no giant cells, no arteritis", "p": "derived",
                               "tier": "invasive"},
    "neostigmine / edrophonium challenge": {"v": "no improvement", "p": "derived",
                                            "tier": "bedside"},
}

CASES = [
 dict(
  video="mild_cpeo_mitochondrial_PMC9350803.mp4", pmcid="PMC9350803",
  dx="Generalized myasthenia gravis with EXTRAOCULAR MUSCLE ATROPHY - the ptosis and limb "
     "weakness responded to treatment but the ophthalmoparesis did not",
  sign="droopy eyelids with restricted eye movements",
  correct=["myasthenia gravis", "generalized myasthenia gravis",
           "myasthenia with extraocular muscle atrophy"],
  partial=["neuromuscular junction disorder", "ocular myasthenia",
           "chronic progressive external ophthalmoplegia"],
  who=dict(age=24, sex="male"),
  yes=["drooping eyelids", "restricted eye movements", "generalised weakness",
       "the droop and the weakness improved with medication",
       "the eye movement restriction did NOT improve with medication",
       "symptoms fluctuate", "double vision"],
  no=["eye pain", "bulging eyes", "headache", "a family history of a similar illness",
      "recent infection", "fever", "hearing loss", "swallowing difficulty at onset",
      "gradual onset since childhood", "a thymus tumour"],
  inv={
   "ice-pack test": {"v": "POSITIVE", "p": "reported", "decisive": True},
   "repetitive nerve stimulation": {"v": "decremental response", "p": "reported",
                                    "decisive": True},
   "anti-acetylcholine receptor antibodies": {"v": "10.32 nmol/L (normal <0.50) - strongly "
                                                   "POSITIVE", "p": "reported", "decisive": True},
   "MRI orbits": {"v": "SEVERE THINNING of all extraocular muscles; exotropia of the right eye",
                  "p": "reported", "decisive": True},
   "CT chest (thymus)": {"v": "no thymic abnormality", "p": "reported"},
   "trial of pyridostigmine and prednisolone": {"v": "ptosis and limb weakness improved; the "
                                                     "ophthalmoparesis did NOT", "p": "reported",
                                                "tier": "bedside", "decisive": True},
   "mitochondrial genetics (mtDNA deletion)": {"v": "no deletion - excludes chronic progressive "
                                                    "external ophthalmoplegia", "p": "derived"},
  },
  dont_miss="Fixed ophthalmoparesis does not exclude myasthenia; long-standing disease can atrophy "
            "the extraocular muscles, so send antibodies and do the ice-pack test before calling "
            "it a mitochondrial myopathy.",
  must_not="diagnosing chronic progressive external ophthalmoplegia - the antibodies, the "
           "decrement and the positive ice-pack test all say myasthenia"),

 dict(
  video="moderate_gca_ophthalmoplegia_PMC12960836.mp4", pmcid="PMC12960836",
  dx="CMT1H (Charcot-Marie-Tooth type 1H) from a recurring FBLN5 variant, presenting with cranial "
     "nerve involvement and diplopia - the first such report",
  sign="limitation of eye abduction with double vision, and difficulty walking on the heels",
  correct=["CMT1H", "Charcot-Marie-Tooth disease", "hereditary demyelinating neuropathy"],
  partial=["cranial neuropathy", "hereditary neuropathy", "chronic inflammatory demyelinating "
           "polyneuropathy"],
  who=dict(age=45, sex="female"),
  yes=["double vision", "the double vision has lasted years", "difficulty moving the eyes outwards",
       "double vision in all directions of gaze", "never being able to run properly",
       "a sister who falls frequently", "difficulty walking on the heels",
       "the visual problem began as vague visual disturbance five years ago"],
  no=["eye pain", "jaw pain when chewing", "scalp tenderness", "sudden visual loss",
      "headache over the temples", "weight loss", "fever", "childhood squint",
      "fatigable weakness", "improvement with rest"],
  inv={
   "whole exome sequencing": {"v": "heterozygous likely pathogenic FBLN5 c.1117C>T (p.Arg373Cys) "
                                   "- CMT1H", "p": "reported", "decisive": True},
   "MRI brain with contrast": {"v": "bilateral contrast enhancement and THICKENING of cranial "
                                    "nerves III through XII", "p": "reported", "decisive": True},
   "nerve conduction studies": {"v": "demyelinating sensorimotor neuropathy", "p": "reported",
                                "decisive": True},
   "lumbar puncture / CSF": {"v": "protein mildly raised at 73 mg/dL", "p": "reported"},
   "MRI spine": {"v": "symmetrical thickening of the lumbosacral nerve roots", "p": "reported",
                 "tier": "imaging", "decisive": True},
   "ocular motility examination": {"v": "bilateral limitation of abduction, worse on the right, "
                                        "with diplopia in all directions", "p": "reported"},
   "ESR / CRP": {"v": "normal - against giant cell arteritis", "p": "derived"},
   "temporal artery ultrasound": {"v": "no halo sign", "p": "derived"},
  },
  dont_miss="Years of diplopia with thickened, enhancing cranial nerves and a family history of "
            "poor running is an inherited demyelinating neuropathy, not an inflammatory "
            "arteritis; genetic testing is the answer.",
  must_not="treating this as giant cell arteritis - the course is five years, inflammatory "
           "markers are normal, and the family history points to CMT"),

 dict(
  video="moderate_postsurgical_lidretraction_PMC11495012.mp4", pmcid="PMC11495012",
  dx="Temporary unilateral LEFT upper-eyelid retraction after closed-approach structural "
     "rhinoplasty, giving the appearance of ptosis in the fellow eye; it resolved with "
     "conservative treatment",
  sign="one upper eyelid sits high with white sclera visible above the iris",
  correct=["post-surgical eyelid retraction", "rhinoplasty complication",
           "eyelid retraction after nasal surgery"],
  partial=["eyelid retraction", "pseudo-ptosis", "thyroid eye disease"],
  who=dict(age=40, sex="female"),
  yes=["one eyelid sits higher than the other", "the other eye looks droopy by comparison",
       "recent nose surgery", "the eyelid changed within a week of the operation",
       "it improved over about four weeks"],
  no=["eye pain", "bulging eyes", "double vision", "weight loss", "palpitations",
      "heat intolerance", "tremor", "difficulty closing the eye", "dry or gritty eyes",
      "fatigable droop", "a childhood squint", "headache"],
  inv={
   "lid position and measurement (MRD1 both sides)": {"v": "MRD1 raised on the LEFT (retraction); "
                                                           "right lid height normal - the right "
                                                           "eye is NOT ptotic", "p": "reported",
                                                      "decisive": True},
   "surgical history": {"v": "closed-approach structural rhinoplasty; retraction noted on "
                             "postoperative day 6", "p": "reported", "tier": "bedside",
                        "decisive": True},
   "pain and periorbital inspection": {"v": "no lagophthalmos and no corneal erosion",
                                       "p": "reported"},
   "TSH / free T4 / TRAb": {"v": "normal, TRAb negative - excludes thyroid eye disease",
                            "p": "derived", "decisive": True},
   "MRI orbits": {"v": "no extraocular muscle enlargement, no mass", "p": "derived"},
   "MRI brain with contrast": {"v": "no dorsal midbrain lesion - excludes Collier sign",
                               "p": "derived"},
   "clinical course": {"v": "resolved after four weeks of conservative treatment", "p": "reported",
                       "tier": "bedside"},
  },
  dont_miss="Measure both lids before deciding which one is abnormal; here the retracted lid is "
            "the problem and the fellow eye needs no ptosis surgery, and the cause is a recent "
            "operation.",
  must_not="working up or operating on the eye that merely looks droopy, or labelling it thyroid "
           "eye disease without thyroid tests"),

 dict(
  video="severe_iiipalsy_aneurysm_PMC12606889.mp4", pmcid="PMC12606889",
  dx="CONGENITAL oculomotor nerve palsy with aberrant regeneration, causing irregular involuntary "
     "pupillary spasms and aberrant eyelid movements",
  sign="unequal pupils with restricted eye movement and abnormal eyelid movement",
  correct=["congenital oculomotor nerve palsy", "aberrant regeneration of the third nerve",
           "congenital third nerve palsy"],
  partial=["oculomotor nerve palsy", "anisocoria", "posterior communicating artery aneurysm"],
  who=dict(age=24, sex="female"),
  yes=["unequal pupil sizes", "one pupil does not react in dim light",
       "involuntary pupil spasms that come and go irregularly",
       "the eye turns outwards and downwards", "restricted eye movement",
       "previous squint surgery", "previous eyelid surgery",
       "the problem has been present as long as she can remember"],
  no=["sudden onset", "severe headache", "the worst headache of her life", "neck stiffness",
      "eye pain", "nausea and vomiting", "recent head injury", "double vision of recent onset",
      "fever", "any other neurological symptom"],
  inv={
   "pupil examination (size, light reaction)": {"v": "mild anisocoria; the RIGHT pupil is "
                                                     "unreactive to dim light, with involuntary "
                                                     "pupillary spasms that are irregular in both "
                                                     "frequency and duration and unrelated to eye "
                                                     "position", "p": "reported",
                                                "decisive": True},
   "ocular motility examination": {"v": "exotropia, hypotropia and motility impairment - a right "
                                        "oculomotor nerve palsy", "p": "reported"},
   "MRI orbits": {"v": "atrophy of the extraocular muscles, particularly the medial rectus - a "
                       "long-standing, not acute, palsy", "p": "reported", "decisive": True},
   "CT / MR angiography (circle of Willis)": {"v": "NO aneurysm", "p": "derived",
                                              "decisive": True},
   "ocular surgical history": {"v": "previous strabismus surgery and levator muscle surgery",
                               "p": "reported", "tier": "bedside", "decisive": True},
  },
  dont_miss="A pupil-involving third nerve palsy of ACUTE onset is an aneurysm until proven "
            "otherwise and needs angiography the same day; the discriminator here is that the "
            "palsy is long-standing, with muscle atrophy and aberrant regeneration.",
  must_not="assuming an acute posterior communicating artery aneurysm - the angiogram is clear "
           "and the muscle atrophy shows the palsy is congenital"),

 dict(
  video="severe_mg_ptosis_PMC8064859.mp4", pmcid="PMC8064859",
  dx="Myasthenia gravis presenting with neck weakness and asymmetrical ptosis, showing the "
     "'pronounced ptosis' bedside sign on sustained loud counting",
  sign="a drooping upper eyelid that worsens as the patient keeps talking",
  correct=["myasthenia gravis", "ocular myasthenia", "neuromuscular junction disorder"],
  partial=["fatigable ptosis", "generalized myasthenia", "Lambert-Eaton syndrome"],
  who=dict(age=75, sex="male"),
  yes=["drooping eyelids", "the droop is worse on one side",
       "the droop gets worse the longer he talks", "neck weakness",
       "the neck is weaker on extension than on flexion", "symptoms of about two weeks",
       "the droop improved after an injection in clinic"],
  no=["eye pain", "headache", "bulging eyes", "sudden onset", "a family history of a similar "
      "illness", "recent head injury", "unequal pupils", "fever", "limb numbness",
      "symptoms present since childhood"],
  inv={
   "sustained upgaze fatigability test": {"v": "'PRONOUNCED PTOSIS' on counting 1 to 100 - the "
                                               "right eye closed completely while the left droop "
                                               "increased", "p": "reported", "decisive": True},
   "repetitive nerve stimulation": {"v": "decremental response in facial and spinal accessory "
                                         "nerves", "p": "reported", "decisive": True},
   "anti-acetylcholine receptor antibodies": {"v": "16.63 nmol/L - elevated", "p": "reported",
                                              "decisive": True},
   "neostigmine / edrophonium challenge": {"v": "ptosis improved (partially right, completely "
                                                "left) with improvement in neck muscle power",
                                           "p": "reported", "decisive": True},
   "limb and neck power": {"v": "neck weakness, extensors more than flexors", "p": "reported"},
   "ice-pack test": {"v": "partial improvement", "p": "reported"},
   "CT chest (thymus)": {"v": "no thymoma", "p": "derived"},
  },
  dont_miss="Ask the patient to count aloud and watch the lid; neck extensor weakness with "
            "fatigable ptosis is myasthenia, and it is treatable - but generalized disease can "
            "progress to a respiratory crisis.",
  must_not="calling it age-related aponeurotic ptosis and not testing for fatigability"),

 dict(
  video="severe_orbital_mucor_PMC10414977.mp4", pmcid="PMC10414977",
  dx="Rhino-orbital-cerebral mucormycosis in a COVID-19 positive patient with newly diagnosed "
     "diabetes, whose eye pain had been treated with steroid drops",
  sign="a painful, swollen eye with restricted movement and a drooping lid",
  correct=["mucormycosis", "rhino-orbital-cerebral mucormycosis", "invasive fungal sinusitis"],
  partial=["orbital cellulitis", "orbital apex syndrome", "cavernous sinus thrombosis"],
  who=dict(age=46, sex="female"),
  yes=["constant sharp eye pain", "pain for about a week", "the pain got much worse",
       "a drooping eyelid", "the eye will not turn inwards", "having been given steroid eye drops",
       "excessive thirst and passing urine often", "a recent respiratory infection",
       "no previous medical diagnoses"],
  no=["gradual painless onset", "double vision for years", "a family history of a similar "
      "illness", "fatigable droop", "improvement with rest", "recent eye surgery",
      "a childhood squint", "weight gain"],
  inv={
   "glucose / HbA1c": {"v": "non-fasting glucose 385 mg/dL - NEWLY DIAGNOSED diabetes",
                       "p": "reported", "decisive": True},
   "full blood count": {"v": "leukocytosis, white cells 21.4 x10^9/L", "p": "reported"},
   "SARS-CoV-2 test": {"v": "POSITIVE", "p": "reported", "decisive": True},
   "CT sinuses": {"v": "invasive sinus disease extending to the orbit", "p": "reported",
                  "decisive": True},
   "fungal culture / KOH of nasal tissue": {"v": "non-septate broad hyphae - Mucorales",
                                            "p": "derived", "decisive": True},
   "ocular motility examination": {"v": "failure to adduct the right eye", "p": "reported"},
   "pain and periorbital inspection": {"v": "severe constant pain; the eye had been treated with "
                                            "steroid drops at two outside clinics", "p": "reported"},
   "MRI orbits": {"v": "orbital involvement with apical disease", "p": "derived"},
  },
  dont_miss="A painful eye with new ophthalmoplegia in a diabetic or immunocompromised patient is "
            "mucormycosis until proven otherwise - it needs urgent biopsy, amphotericin and "
            "surgical debridement, and steroids make it worse.",
  must_not="continuing steroid eye drops for presumed inflammation, which is what delayed this "
           "diagnosis"),
]

build(LINE, PANEL, CASES)
