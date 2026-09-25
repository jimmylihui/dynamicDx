"""Facial palsy, on documented aetiologies.

Two more cases were added and then withdrawn on 2026-07-30 - fp_diplegia_acidp_PMC9532814 and
fp_bilateral_neuritis_PMC13166995 - because both clips were under-severe for the House-Brackmann
grade their case claimed; see withdrawn/2026-07-30_facialpalsy_undersevere.tar.gz. The line is
back to one case.

Eight of the line's original nine clips were withdrawn: they came from a dataset that supplies a
severity grade and a side and no aetiology at all, so the causes attached to them could not be
checked against anything. Two cases were added on 2026-07-30 and both are BILATERAL, which is not
an accident. Open-access facial-palsy video is dominated by surgical reanimation series, and among
the diagnostic clips the usable ones were the bilateral cases - a unilateral clip is only safe if
the affected side in the video can be matched to the side in the text, and a selfie-recorded clip
that may be mirrored cannot be matched at all.

The two bilateral cases are deliberately kept together because they are each other's differential.
Both are a face that will not move on either side. One is a demyelinating polyneuropathy -
albuminocytological dissociation, absent ankle reflexes, sensory loss, demyelinating conduction
studies - and needs immunotherapy and a watch on the vital capacity. The other is an isolated
facial neuritis with a normal CSF, normal reflexes and no limb involvement, and it resolved on
prednisolone. Telling them apart is the whole task.
"""
from genlib import build

LINE = "facialpalsy"

PANEL = {
    "facial nerve examination (House-Brackmann)": {"v": "not graded", "p": "derived",
                                                   "tier": "bedside"},
    "forehead movement": {"v": "symmetrical", "p": "derived", "tier": "bedside"},
    "eye closure": {"v": "complete both sides", "p": "derived", "tier": "bedside"},
    "smile symmetry": {"v": "symmetrical", "p": "derived", "tier": "bedside"},
    "synkinesis assessment (eye closure with platysma/frontalis)": {"v": "no co-contraction",
                                                                    "p": "derived",
                                                                    "tier": "bedside"},
    "palpebral fissure width both sides": {"v": "equal", "p": "derived", "tier": "bedside"},
    "ear and mastoid examination": {"v": "normal, no vesicles", "p": "derived", "tier": "bedside"},
    "parotid and neck palpation": {"v": "no mass", "p": "derived", "tier": "bedside"},
    "hearing and taste": {"v": "normal", "p": "derived", "tier": "bedside"},
    "other cranial nerves": {"v": "normal", "p": "derived", "tier": "bedside"},
    "limb power and reflexes": {"v": "normal", "p": "derived", "tier": "bedside"},
    "vital signs": {"v": "normal, afebrile", "p": "derived", "tier": "bedside"},
    "family history": {"v": "no relatives affected", "p": "derived", "tier": "bedside"},
    "Lyme serology (ELISA and immunoblot)": {"v": "negative", "p": "derived", "tier": "blood"},
    "serum ACE": {"v": "normal", "p": "derived", "tier": "blood"},
    "HbA1c / fasting glucose": {"v": "normal", "p": "derived", "tier": "blood"},
    "full blood count and ESR/CRP": {"v": "normal", "p": "derived", "tier": "blood"},
    "HIV and syphilis serology": {"v": "negative", "p": "derived", "tier": "blood"},
    "varicella-zoster serology / PCR": {"v": "negative", "p": "derived", "tier": "blood"},
    "anti-acetylcholine receptor antibodies": {"v": "negative", "p": "derived", "tier": "blood"},
    "MRI brain and internal auditory canal with contrast": {"v": "no lesion, no nerve "
                                                                "enhancement", "p": "derived",
                                                            "tier": "imaging"},
    "MRI or CT parotid": {"v": "no mass", "p": "derived", "tier": "imaging"},
    "chest imaging (sarcoidosis)": {"v": "no lymphadenopathy", "p": "derived", "tier": "imaging"},
    "electroneuronography / facial EMG": {"v": "normal", "p": "derived", "tier": "invasive"},
    "lumbar puncture / CSF": {"v": "normal", "p": "derived", "tier": "invasive"},
    # added 2026-07-30 for the two bilateral cases - the differential for a face that will not
    # move on either side is a polyneuropathy versus an isolated facial neuritis, and the panel
    # has to be able to tell them apart
    "recent vaccination or infection history": {"v": "nothing in the preceding weeks",
                                                "p": "derived", "tier": "bedside"},
    "voice and hoarseness assessment": {"v": "normal voice", "p": "derived", "tier": "bedside"},
    "gait, ability to run, and limb sensation": {"v": "normal", "p": "derived",
                                                 "tier": "bedside"},
    "trial of corticosteroids (response)": {"v": "not tried", "p": "derived", "tier": "bedside"},
    "trial of IVIG or plasma exchange (response)": {"v": "not tried", "p": "derived",
                                                    "tier": "bedside"},
    "clinical course": {"v": "not recorded", "p": "derived", "tier": "bedside"},
    "antiganglioside antibodies (serum and CSF)": {"v": "negative", "p": "derived",
                                                   "tier": "blood"},
    "EBV and herpes simplex serology": {"v": "negative", "p": "derived", "tier": "blood"},
    "autoimmune screen and vasculitis markers": {"v": "negative", "p": "derived",
                                                 "tier": "blood"},
    "nerve conduction studies (limbs)": {"v": "normal", "p": "derived", "tier": "invasive"},
    "blink reflex study": {"v": "normal", "p": "derived", "tier": "invasive"},
}

CASES = [
 dict(
  video="fp_recurrent_synkinesis_PMC12572359.mp4", pmcid="PMC12572359",
  dx="Familial recurrent Bell's palsy with BILATERAL SEQUENTIAL involvement and post-paralytic "
     "synkinesis - left palsy in his fifties leaving left synkinesis, then a contralateral right "
     "palsy at 64 leaving right synkinesis",
  sign="an asymmetric face with unequal palpebral fissures, and abnormal co-movement when the "
       "eyes close or the brows are raised",
  correct=["recurrent Bell's palsy", "familial Bell's palsy",
           "post-paralytic facial synkinesis"],
  partial=["facial synkinesis", "bilateral facial palsy", "Bell's palsy"],
  who=dict(age=53, sex="male"),
  yes=["one eye opening looks narrower than the other",
       "the cheek pulls when the eyes are closed", "a band tightens in the neck on closing the eyes",
       "the lower lip curls while speaking or chewing", "cheek pain when chewing",
       "the face went weak on one side years ago", "the face later went weak on the OTHER side",
       "pain behind the ear before the second episode", "sounds seemed too loud on one side",
       "a change in taste", "several brothers and sisters have had a facial palsy",
       "high blood pressure", "each episode recovered incompletely"],
  no=["a lump in front of the ear", "a rash or blisters in the ear", "hearing loss",
      "gradual painless weakness over months", "limb weakness", "double vision",
      "difficulty swallowing", "recent tick bite", "fever", "cancer",
      "numbness of the face that persists"],
  inv={
   "family history": {"v": "five of fourteen siblings have had a facial palsy; two affected "
                           "brothers had recurrent episodes with synkinesis", "p": "reported",
                      "decisive": True},
   "synkinesis assessment (eye closure with platysma/frontalis)":
       {"v": "co-contraction of eye closure with the left platysma and left frontalis; right "
             "lower-lip curling on speech and mastication", "p": "reported", "decisive": True},
   "palpebral fissure width both sides": {"v": "narrowed LEFT palpebral fissure from established "
                                               "synkinesis", "p": "reported", "decisive": True},
   "clinical course": {"v": "left facial palsy treated with acyclovir 400 mg five times daily for "
                            "10 days and prednisone 50 mg for five days with taper; right palsy "
                            "at age 64 with retroauricular pain, hyperacusis and dysgeusia; right "
                            "synkinesis appeared five months later", "p": "reported",
                       "tier": "bedside", "decisive": True},
   "MRI brain and internal auditory canal with contrast": {"v": "no tumour, no perineural "
                                                                "enhancement, no central lesion",
                                                           "p": "derived", "decisive": True},
   "Lyme serology (ELISA and immunoblot)": {"v": "negative", "p": "derived"},
   "serum ACE": {"v": "normal; chest imaging shows no lymphadenopathy", "p": "derived"},
   "electroneuronography / facial EMG": {"v": "chronic reinnervation with synkinetic "
                                              "co-activation; no active denervation",
                                         "p": "derived"},
  },
  dont_miss="Facial palsy that recurs or alternates sides is not simple Bell's - exclude Lyme "
            "disease, sarcoidosis and a facial-nerve or parotid tumour, and take a family "
            "history, because familial recurrent Bell's palsy is described.",
  must_not="treating the abnormal co-movement as a fresh palsy and giving repeated steroid "
           "courses; synkinesis is a sequela treated with facial retraining and botulinum toxin"),

]

build(LINE, PANEL, CASES)
