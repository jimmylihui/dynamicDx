"""Atypical parkinsonism - the line where half the cases are reversible.

The old parkinson line was withdrawn on 2026-07-30: its nine clips were gait-dataset patients
relabelled as nine syndromes they did not have. This rebuilds the slot from documented case
reports, and it is deliberately weighted so that the phenotype does not settle the aetiology.

Three of the six are reversible. Three of the six look like progressive supranuclear palsy or
something near it, and only one of them is a tauopathy. The Wilson case has the whole PSP picture - unprovoked backward falls,
vertical downgaze palsy, axial rigidity, midbrain atrophy with a midbrain-to-pons ratio of 0.20 -
and is cured by chelation. The anti-IgLON5 case presents as Pisa syndrome and responds to
rituximab. The hornet-sting case is a levodopa-unresponsive freezing syndrome with a normal DaT
scan that methylprednisolone abolished. A model that reads the phenotype off the video and stops
has failed the three patients who could have been treated.

Faces: the PSP, hornet-sting and Pisa cases are redacted by the source authors; the Wilson case
is not, and its clip is the only open-access video in which the vertical gaze examination is
actually visible - every redacted PSP video hides the eyes, which is where the sign lives.
"""
from genlib import build

LINE = "parkinsonism"

PANEL = {
    # bedside
    "vertical saccades and gaze range (up and down)": {"tier": "bedside"},
    "doll's head (oculocephalic) manoeuvre": {"tier": "bedside"},
    "smooth pursuit and saccade velocity": {"tier": "bedside"},
    "eyelid function (apraxia of lid opening, blepharospasm, lid retraction)":
        {"tier": "bedside"},
    "slit-lamp examination for Kayser-Fleischer rings": {"tier": "bedside"},
    "pull test / retropulsion": {"tier": "bedside"},
    "gait observation including turning and doorways": {"tier": "bedside"},
    "freezing-of-gait provocation (doorway, turning, dual task)": {"tier": "bedside"},
    "applause sign (three-clap test)": {"tier": "bedside"},
    "limb rigidity and axial (neck) rigidity": {"tier": "bedside"},
    "finger tapping for bradykinesia and decrement": {"tier": "bedside"},
    "tremor characterisation (rest, postural, action)": {"tier": "bedside"},
    "wing-beating tremor on sustained shoulder abduction": {"tier": "bedside"},
    "cerebellar testing (dysmetria, dysdiadochokinesia, tandem gait)": {"tier": "bedside"},
    "alien limb / limb levitation with the eyes closed": {"tier": "bedside"},
    "cortical sensory testing (astereognosis, sensory inattention)": {"tier": "bedside"},
    "ideomotor apraxia (imitation of meaningless gestures)": {"tier": "bedside"},
    "myoclonus or stimulus-sensitive jerks in the affected limb": {"tier": "bedside"},
    "dystonic posturing of the hand or foot": {"tier": "bedside"},
    "speech assessment (hypophonia, strained-strangled voice, scanning dysarthria)":
        {"tier": "bedside"},
    "swallowing assessment": {"tier": "bedside"},
    "lying-and-standing blood pressure": {"tier": "bedside"},
    "bladder, bowel and erectile history": {"tier": "bedside"},
    "REM-sleep behaviour history (acting out dreams)": {"tier": "bedside"},
    "cognitive screen (MoCA / MMSE / frontal assessment battery)": {"tier": "bedside"},
    "reflexes, plantar responses and frontal release signs": {"tier": "bedside"},
    "levodopa trial (dose and response)": {"tier": "bedside"},
    "trunk posture: lateral flexion (Pisa) and antecollis, standing versus supine":
        {"tier": "bedside"},
    "medication review (neuroleptics, antiemetics, valproate, calcium-channel blockers, lithium)":
        {"tier": "bedside"},
    # blood
    "serum ceruloplasmin": {"tier": "blood"},
    "24-hour urinary copper": {"tier": "blood"},
    "full blood count, renal and liver profile": {"tier": "blood"},
    "TSH / free T4": {"tier": "blood"},
    "vitamin B12": {"tier": "blood"},
    "HIV, hepatitis B and hepatitis C serology": {"tier": "blood"},
    "paraneoplastic / onconeural antibody panel": {"tier": "blood"},
    "neuronal surface antibody panel including anti-IgLON5": {"tier": "blood"},
    "ATP7B sequencing": {"tier": "blood"},
    "MAPT / GRN / C9orf72 testing": {"tier": "blood"},
    "whole exome / genome sequencing": {"tier": "blood"},
    "serum neurofilament light chain": {"tier": "blood"},
    "drug and toxin screen": {"tier": "blood"},
    # imaging
    "MRI brain - midbrain (hummingbird sign, midbrain-to-pons ratio)":
        {"tier": "imaging"},
    "MRI brain - putamen (atrophy, rim sign, hot cross bun, SWI hypointensity)":
        {"tier": "imaging"},
    "MRI brain - cortical atrophy pattern": {"tier": "imaging"},
    "MRI brain - white matter and ventricles (small-vessel disease, ventriculomegaly)":
        {"tier": "imaging"},
    "MRI whole spine": {"tier": "imaging"},
    "DAT-SPECT / FP-CIT PET": {"tier": "imaging"},
    "FDG-PET brain": {"tier": "imaging"},
    "abdominal ultrasound and liver elastography": {"tier": "imaging"},
    "CT chest / abdomen / pelvis (tumour search)": {"tier": "imaging"},
    # invasive / neurophysiology
    "lumbar puncture / CSF (cells, protein, Abeta42/40, total tau, p-tau)":
        {"tier": "invasive"},
    "polysomnography": {"tier": "invasive"},
    "EEG": {"tier": "invasive"},
    "autonomic function testing (tilt table, sympathetic skin response)":
        {"tier": "invasive"},
    "urodynamics / post-void residual": {"tier": "invasive"},
    "surface EMG and accelerometry of the tremor": {"tier": "invasive"},
    "liver biopsy with copper quantification": {"tier": "invasive"},
}

CASES = [
 dict(
  video="psp_richardson_PMC11082598.mp4", pmcid="PMC11082598",
  dx="Progressive supranuclear palsy, Richardson syndrome (a 4-repeat tauopathy), in a woman "
     "carrying a heterozygous loss-of-function SMPD1 variant (p.P332R) - falls from about 18 "
     "months after onset, vertical-worse-than-horizontal supranuclear gaze palsy overcome by the "
     "doll's head manoeuvre, severe neck rigidity, positive applause sign",
  sign="severe axial rigidity with the patient unable to rise or stand unsupported, held upright "
       "by the examiner, and a 'gunslinger' posture of the arm",
  correct=["progressive supranuclear palsy", "PSP", "PSP-Richardson syndrome"],
  partial=["atypical parkinsonism", "tauopathy", "Parkinson-plus syndrome"],
  who=dict(age="symptom onset at 67; filmed about six years later", sex="female"),
  yes=["repeated falls", "the falls began within about eighteen months of the first symptom",
       "falling backward", "difficulty looking downward", "a staring expression",
       "stiffness of the neck", "slurred speech", "coughing when drinking",
       "needing a wheelchair", "talking and laughing during sleep",
       "levodopa gave only a small improvement in strength"],
  no=["visual hallucinations", "involuntary writhing movements on levodopa",
      "fainting on standing", "urinary incontinence early in the illness",
      "one arm feeling as if it acts on its own", "a family history of a similar illness",
      "tremor of the hands at rest as the first symptom", "a rash or fever",
      "double vision", "leaning to one side when walking"],
  inv={
   "vertical saccades and gaze range (up and down)":
       {"v": "both upgaze and downgaze RESTRICTED, vertical worse than horizontal; horizontal "
             "gaze preserved", "p": "reported", "decisive": True},
   "doll's head (oculocephalic) manoeuvre":
       {"v": "the gaze restriction is OVERCOME - this is supranuclear, not a nerve or muscle "
             "palsy", "p": "reported", "decisive": True},
   "applause sign (three-clap test)": {"v": "POSITIVE", "p": "reported", "decisive": True},
   "limb rigidity and axial (neck) rigidity":
       {"v": "SEVERE in the neck, mild in the upper limbs - axial predominance", "p": "reported",
        "decisive": True},
   "MRI brain - midbrain (hummingbird sign, midbrain-to-pons ratio)":
       {"v": "mild hummingbird sign with cerebral atrophy", "p": "reported", "decisive": True},
   "levodopa trial (dose and response)":
       {"v": "levodopa 750 mg/day plus amantadine 300 mg/day - subjective benefit only, and NO "
             "levodopa-induced dyskinesia ever developed", "p": "reported"},
   "cognitive screen (MoCA / MMSE / frontal assessment battery)":
       {"v": "MoCA 24/30, frontal assessment battery 13/18 - mild impairment", "p": "reported"},
   "whole exome / genome sequencing":
       {"v": "heterozygous SMPD1 NM_000543.5:c.995C>G p.P332R loss-of-function variant, found in "
             "two further unrelated PSP patients of Chinese ancestry", "p": "reported"},
   "swallowing assessment": {"v": "coughing when drinking; speech largely unintelligible by 2023",
                             "p": "reported"},
   "speech assessment (hypophonia, strained-strangled voice, scanning dysarthria)":
       {"v": "slurred, progressively unintelligible", "p": "reported"},
  },
  dont_miss="Wilson disease and anti-IgLON5 disease both reproduce this picture down to the "
            "downgaze palsy and the midbrain atrophy, and both are treatable - send ceruloplasmin "
            "and the antibody panel before settling on a tauopathy that has no treatment.",
  must_not="calling this Parkinson disease and escalating levodopa - the falls came within the "
           "first two years, the rigidity is axial, and no dyskinesia ever appeared"),

 dict(
  video="msa_oculogyric_crisis_PMC13175740.mp4", pmcid="PMC13175740",
  dx="Multiple system atrophy, parkinsonian type (MSA-P), with LEVODOPA-INDUCED OCULOGYRIC CRISES "
     "- painless conjugate upward eye deviation with prominent blepharospasm beginning about 30 "
     "minutes after each dose and remitting completely by 3 hours; the first documented report of "
     "this in MSA",
  sign="the eyes are pulled conjugately upward and held there, with forced eyelid closure, while "
       "the patient is otherwise alert and able to speak",
  correct=["multiple system atrophy", "MSA-P", "multiple system atrophy parkinsonian type"],
  partial=["atypical parkinsonism", "oculogyric crisis", "levodopa-induced dystonia"],
  who=dict(age=58, sex="female"),
  yes=["the eyes are pulled upward in attacks", "the attacks start about half an hour after a "
       "levodopa tablet", "the attacks pass within a few hours",
       "the eyelids squeeze shut during the attacks", "the attacks are not painful",
       "fainting or near-fainting on standing", "urinary incontinence",
       "constipation from early on", "acting out dreams during sleep",
       "a strained, high-pitched voice", "repeated falls", "needing a wheelchair",
       "the stiffness and slowness are worse on the right"],
  no=["visual hallucinations", "difficulty looking downward before treatment started",
      "one arm feeling as if it acts on its own", "a family history of a similar illness",
      "brown rings around the coloured part of the eye", "leaning to one side when walking",
      "the eye attacks happened before any medication was started",
      "loss of awareness during the attacks", "fever", "weakness of a limb"],
  inv={
   "levodopa trial (dose and response)":
       {"v": "levodopa/carbidopa escalated 375 -> 750 -> 1125 mg/day; motor symptoms improved, "
             "and the oculogyric crises appeared about 30 MINUTES AFTER EACH DOSE and remitted "
             "completely by 3 hours", "p": "reported", "decisive": True},
   "lying-and-standing blood pressure":
       {"v": "130 mmHg systolic seated falling to 100 mmHg standing WITHOUT a compensatory rise "
             "in pulse rate", "p": "reported", "decisive": True},
   "MRI brain - putamen (atrophy, rim sign, hot cross bun, SWI hypointensity)":
       {"v": "putaminal atrophy with the rim sign and putaminal hypointensity on "
             "susceptibility-weighted imaging", "p": "reported", "decisive": True},
   "bladder, bowel and erectile history":
       {"v": "overt urinary incontinence requiring pads; constipation from onset", "p": "reported",
        "decisive": True},
   "REM-sleep behaviour history (acting out dreams)":
       {"v": "motor activity and vocalisation during sleep", "p": "reported"},
   "speech assessment (hypophonia, strained-strangled voice, scanning dysarthria)":
       {"v": "slurred, high-pitched, strangled speech with mild stammering", "p": "reported",
        "decisive": True},
   "vertical saccades and gaze range (up and down)":
       {"v": "NO baseline oculomotor abnormality before levodopa - the upward deviation is "
             "drug-induced, not a supranuclear palsy", "p": "reported", "decisive": True},
   "limb rigidity and axial (neck) rigidity":
       {"v": "moderate-to-severe bradykinesia and asymmetric rigidity, worse on the right, with "
             "hyperreflexia", "p": "reported"},
   "medication review (neuroleptics, antiemetics, valproate, calcium-channel blockers, lithium)":
       {"v": "trazodone, paroxetine, hydrocortisone and verapamil - no dopamine blocker",
        "p": "reported", "decisive": True},
  },
  dont_miss="Oculogyric crisis is far more often caused by a dopamine BLOCKER - an antipsychotic "
            "or metoclopramide - and it is also seen in autoimmune encephalitis; ask what else "
            "the patient is taking before attributing it to levodopa.",
  must_not="diagnosing idiopathic Parkinson disease - the orthostatic drop without a pulse rise, "
           "the incontinence, the early falls and the putaminal rim sign are all MSA; and do not "
           "call the eye deviation a seizure or a functional attack"),

 dict(
  video="cbd_apraxic_hand_PMC12371612.mp4", pmcid="PMC12371612",
  dx="Corticobasal syndrome meeting criteria for probable corticobasal degeneration (a 4-repeat "
     "tauopathy) - jerky, dystonic, apraxic right hand with posterior-variant alien limb; a "
     "decade of annual surveillance MRIs done for an unrelated pituitary tumour had already "
     "captured the prodrome",
  sign="the right hand jerks at rest, the fingers adopt fixed abnormal postures, and the examiner "
       "manipulates the hand while it resists and moves aimlessly",
  correct=["corticobasal degeneration", "corticobasal syndrome", "CBD", "CBS"],
  partial=["atypical parkinsonism", "tauopathy", "Parkinson-plus syndrome",
           "frontotemporal dementia spectrum disorder"],
  who=dict(age=54, sex="male"),
  yes=["a jerky tremor of the right hand", "the tremor has been getting worse for two years",
       "it interferes with typing and with using chopsticks",
       "the fingers take up abnormal postures on their own",
       "the right hand makes aimless movements when the eyes are closed",
       "difficulty finding words", "a change in behaviour and in judgement about money",
       "still able to cycle without falling"],
  no=["loss of the sense of smell", "acting out dreams during sleep",
      "fainting on standing", "visual hallucinations", "falls", "difficulty looking downward",
      "a family history of a similar illness", "double vision", "urinary incontinence",
      "the symptoms are on both sides equally", "brown rings around the coloured part of the eye"],
  inv={
   "alien limb / limb levitation with the eyes closed":
       {"v": "POSITIVE - aimless movements of the right side with the eyes closed, "
             "posterior-variant alien limb", "p": "reported", "decisive": True},
   "cortical sensory testing (astereognosis, sensory inattention)":
       {"v": "sensory inattention and astereognosis on the right", "p": "reported",
        "decisive": True},
   "ideomotor apraxia (imitation of meaningless gestures)":
       {"v": "apraxia to meaningless gestures", "p": "reported", "decisive": True},
   "myoclonus or stimulus-sensitive jerks in the affected limb":
       {"v": "myoclonic jerks in the right hand at rest", "p": "reported", "decisive": True},
   "dystonic posturing of the hand or foot":
       {"v": "dystonic posturing of the right fingers", "p": "reported", "decisive": True},
   "MRI brain - cortical atrophy pattern":
       {"v": "moderate global atrophy with MARKEDLY ASYMMETRICAL atrophy of the superior parietal "
             "lobules and posterior frontal lobes, left hemisphere worse", "p": "reported",
        "decisive": True},
   "FDG-PET brain": {"v": "hypometabolism in the same asymmetric distribution", "p": "reported",
                     "decisive": True},
   "lumbar puncture / CSF (cells, protein, Abeta42/40, total tau, p-tau)":
       {"v": "Abeta42/40 ratio LOW at 0.044 (abnormal <0.065) but total tau NORMAL at 384 pg/mL "
             "(146-595) - not the profile of Alzheimer-pathology CBS", "p": "reported"},
   "serum neurofilament light chain":
       {"v": "blood pTau-217 comparable to frontotemporal dementia patients and healthy controls",
        "p": "reported"},
   "whole exome / genome sequencing": {"v": "no genetic aetiology identified", "p": "reported"},
   "reflexes, plantar responses and frontal release signs":
       {"v": "brisk on the right with a pectoral jerk and a positive Hoffman sign", "p": "reported"},
   "cognitive screen (MoCA / MMSE / frontal assessment battery)":
       {"v": "MoCA 19/30 with constructional apraxia, reduced fluency and poor delayed recall",
        "p": "reported"},
  },
  dont_miss="Alzheimer pathology is a common cause of a corticobasal syndrome and is worth "
            "identifying; the CSF here shows a low amyloid ratio but normal tau, which does not "
            "fit it. A jerky, variable, unilateral hand also brings up functional tremor - the "
            "cortical signs and the asymmetric parietal atrophy are what exclude it.",
  must_not="diagnosing Parkinson disease and escalating levodopa - this is asymmetric cortical "
           "disease with alien limb, astereognosis and apraxia, none of which belongs to it"),

 dict(
  video="hornet_sting_parkinsonism_PMC11021691.mp4", pmcid="PMC11021691",
  dx="ACUTE ACQUIRED PARKINSONISM AFTER A HORNET STING - anaphylaxis, then over days a "
     "levodopa-unresponsive akinetic-rigid syndrome dominated by start hesitation and freezing, "
     "with necrotic bilateral putaminal and caudate lesions and a NORMAL DaT-SPECT; the patient's "
     "serum bound rat putamen and substantia nigra, and intravenous methylprednisolone abolished "
     "the freezing (MDS-UPDRS III 35 -> 18). The line's third reversible case.",
  sign="the patient stands with the feet planted together and cannot get started, then moves off "
       "in small hesitant steps, worst at the doorway",
  correct=["acute acquired parkinsonism after a hornet sting",
           "post-hymenoptera-sting parkinsonism", "immune-mediated striatal parkinsonism",
           "acquired striatal parkinsonism"],
  partial=["atypical parkinsonism", "autoimmune encephalitis", "vascular parkinsonism",
           "toxic parkinsonism"],
  who=dict(age=70, sex="male"),
  yes=["the feet get stuck when starting to walk", "the sticking is worst going through a door",
       "the sticking is worst when turning", "the steps are small",
       "the whole illness began within days of a hornet sting",
       "there was a collapse with low blood pressure right after the sting",
       "the walking has got worse over about two months", "speaking less and answering slowly",
       "the voice has become quiet", "words or phrases get repeated",
       "levodopa made no difference at all"],
  no=["tremor", "the symptoms are worse on one side", "difficulty looking downward",
      "fainting on standing", "urinary incontinence", "acting out dreams during sleep",
      "visual hallucinations", "a family history of a similar illness",
      "leaning to one side when walking", "brown rings around the coloured part of the eye",
      "the illness came on slowly over years"],
  inv={
   "DAT-SPECT / FP-CIT PET":
       {"v": "NORMAL - the lesion is postsynaptic and striatal, not a presynaptic dopaminergic "
             "degeneration", "p": "reported", "decisive": True},
   "MRI brain - putamen (atrophy, rim sign, hot cross bun, SWI hypointensity)":
       {"v": "BILATERAL PUTAMEN AND CAUDATE hyperintensity on T2 and FLAIR with patchy restricted "
             "diffusion suggesting NECROSIS, and T1 hyperintensity in the ventral putamen; the "
             "lesions progressed over serial scans", "p": "reported", "decisive": True},
   "levodopa trial (dose and response)":
       {"v": "levodopa/carbidopa titrated to 1000 mg/day over three weeks with NO appreciable "
             "improvement; subsequently withdrawn", "p": "reported", "decisive": True},
   "freezing-of-gait provocation (doorway, turning, dual task)":
       {"v": "start hesitation and freezing, worst on turning and on passing through a doorway; "
             "MDS-UPDRS III 35, Hoehn and Yahr 2.5", "p": "reported", "decisive": True},
   "lumbar puncture / CSF (cells, protein, Abeta42/40, total tau, p-tau)":
       {"v": "protein mildly raised at 0.548 g/L (0.170-0.370) with normal cell count, NO "
             "oligoclonal bands and no intrathecal synthesis; anti-NMDAR, AMPA-R1/2, GABA-B, LGI1 "
             "and CASPR2 all negative", "p": "reported"},
   "neuronal surface antibody panel including anti-IgLON5":
       {"v": "the named panel is negative, but the patient's SERUM bound rat brain tissue in the "
             "putamen, substantia nigra, hippocampus, cerebellum and pontine reticular formation "
             "on immunohistochemistry - an unidentified antibody", "p": "reported",
        "decisive": True},
   "limb rigidity and axial (neck) rigidity":
       {"v": "SYMMETRIC rigidity of neck and limbs with mild symmetric bradykinesia and NO tremor",
        "p": "reported", "decisive": True},
   "pull test / retropulsion": {"v": "recovers in 2-3 steps", "p": "reported"},
   "speech assessment (hypophonia, strained-strangled voice, scanning dysarthria)":
       {"v": "impassive face, hypophonic speech, palilalia", "p": "reported"},
   "reflexes, plantar responses and frontal release signs":
       {"v": "reflexes brisk, plantar responses normal", "p": "reported"},
  },
  dont_miss="Intravenous methylprednisolone 250 mg/day for five days, tapered over two weeks, "
            "stopped the freezing outright and halved the motor score. Subacute symmetric "
            "parkinsonism with striatal lesions and a normal DaT scan is acquired until proven "
            "otherwise - image the striatum, take the exposure history, and treat it as immune.",
  must_not="diagnosing Parkinson disease or an atypical degenerative parkinsonism and pushing "
           "levodopa to 1000 mg - the onset was over days, the signs are symmetric, the DaT scan "
           "is normal, and the striatum is visibly damaged on MRI"),

 dict(
  video="mimic_wilson_psp_phenotype_PMC12962431.mp4", pmcid="PMC12962431",
  dx="LATE-ONSET WILSON DISEASE presenting as a progressive supranuclear palsy phenotype - one "
     "year of unprovoked backward falls, vertical downgaze palsy, axial rigidity and midbrain "
     "atrophy with a midbrain-to-pons ratio of 0.20, all of which reads as PSP; ceruloplasmin was "
     "6.2 mg/dL, 24-hour urinary copper 265.77 ug/day, and exome sequencing found a homozygous "
     "ATP7B variant. Chelation treats it.",
  sign="the examiner steadies the head and tests vertical gaze; downgaze is restricted, pursuit "
       "is broken and the saccades are slow and hypometric",
  correct=["Wilson disease", "late-onset Wilson disease", "Wilson's disease"],
  partial=["atypical parkinsonism", "metabolic parkinsonism", "progressive supranuclear palsy"],
  who=dict(age=52, sex="male"),
  yes=["repeated falls backward", "the falls come without warning",
       "there is no fainting or loss of consciousness with the falls",
       "slowness that now affects bathing and dressing", "tremor of the head",
       "slurred speech", "tremor of both arms, the right before the left",
       "difficulty looking downward", "the arms flap like wings when held out to the sides",
       "unsteadiness on walking heel to toe", "losing five kilograms without trying",
       "low mood and thoughts of self-harm"],
  no=["visual hallucinations", "acting out dreams during sleep", "fainting on standing",
      "urinary incontinence", "one arm feeling as if it acts on its own",
      "a family history of a similar illness", "the parents were related to each other",
      "jaundice or swelling of the abdomen", "fever", "double vision",
      "involuntary writhing movements after medication"],
  inv={
   "slit-lamp examination for Kayser-Fleischer rings":
       {"v": "KAYSER-FLEISCHER RINGS PRESENT in both eyes", "p": "reported", "decisive": True},
   "serum ceruloplasmin":
       {"v": "MARKEDLY REDUCED at 6.2 mg/dL", "p": "reported", "decisive": True},
   "24-hour urinary copper":
       {"v": "ELEVATED at 265.77 ug/day", "p": "reported", "decisive": True},
   "ATP7B sequencing":
       {"v": "homozygous pathogenic ATP7B c.2145C>T p.Tyr715* in exon 8 on whole exome "
             "sequencing - confirms Wilson disease", "p": "reported", "decisive": True},
   "wing-beating tremor on sustained shoulder abduction":
       {"v": "PRESENT and asymmetric, right worse than left - this does not belong to PSP",
        "p": "reported", "decisive": True},
   "cerebellar testing (dysmetria, dysdiadochokinesia, tandem gait)":
       {"v": "dysmetria, dysdiadochokinesia and abnormal tandem gait; Severity of Ataxia Rating "
             "Scale 20 - cerebellar signs do not belong to PSP either", "p": "reported",
        "decisive": True},
   "MRI brain - midbrain (hummingbird sign, midbrain-to-pons ratio)":
       {"v": "predominant midbrain atrophy with midbrain-to-pons ratio 0.20 (normal >0.52), plus "
             "mild cerebral and cerebellar atrophy - THIS LOOKS LIKE PSP AND IS NOT",
        "p": "reported"},
   "vertical saccades and gaze range (up and down)":
       {"v": "vertical DOWNGAZE PALSY with broken smooth pursuit and slow hypometric saccades",
        "p": "reported"},
   "abdominal ultrasound and liver elastography":
       {"v": "mildly altered hepatic echotexture; ARFI elastography shows portal fibrosis",
        "p": "reported", "decisive": True},
   "speech assessment (hypophonia, strained-strangled voice, scanning dysarthria)":
       {"v": "scanning dysarthria", "p": "reported"},
   "limb rigidity and axial (neck) rigidity":
       {"v": "bilateral asymmetric rigidity, right worse than left; UPDRS part III 71",
        "p": "reported"},
   "cognitive screen (MoCA / MMSE / frontal assessment battery)":
       {"v": "MMSE 26/28, MoCA 19/24 with executive dysfunction, apathy and bradyphrenia",
        "p": "reported"},
   "full blood count, renal and liver profile": {"v": "liver and kidney function normal",
                                                 "p": "reported"},
  },
  dont_miss="This is the one to catch. Chelation and zinc arrest late-onset Wilson disease and "
            "partly reverse it; progressive supranuclear palsy has no treatment at all. Any "
            "atypical parkinsonism under about 55, and any with cerebellar signs or a "
            "wing-beating tremor, gets a ceruloplasmin, a 24-hour urinary copper and a slit lamp.",
  must_not="diagnosing progressive supranuclear palsy from the backward falls, the downgaze palsy "
           "and the midbrain atrophy - the Kayser-Fleischer rings, the wing-beating tremor and "
           "the cerebellar signs are not PSP, and stopping at PSP costs this patient a treatable "
           "disease"),

 dict(
  video="mimic_iglon5_pisa_PMC13080482.mp4", pmcid="PMC13080482",
  dx="ANTI-IgLON5 DISEASE presenting as Pisa syndrome - two months of progressive lateral trunk "
     "flexion to the left with head drop, dysphagia and dysarthria, chorea and orofacial "
     "dyskinesia, WITHOUT the sleep or cognitive disturbance the disease is known for; MRI normal, "
     "polysomnography normal, serum anti-IgLON5 strongly positive, and rituximab produced marked "
     "improvement sustained at 24 months",
  sign="the trunk tilts steeply to the left while walking, with the head drooping forward and "
       "reduced arm swing on the left",
  correct=["anti-IgLON5 disease", "IgLON5 antibody disease", "autoimmune IgLON5 tauopathy"],
  partial=["atypical parkinsonism", "autoimmune encephalitis", "Pisa syndrome",
           "multiple system atrophy"],
  who=dict(age=50, sex="male"),
  yes=["leaning over to the left when walking", "the lean disappears when lying down",
       "the head droops forward", "difficulty swallowing", "quiet, slow and slurred speech",
       "excessive sweating over the face and trunk", "restless movements of all four limbs",
       "involuntary movements around the mouth and of the tongue",
       "the whole illness has taken only two months", "reduced arm swing on the left"],
  no=["acting out dreams during sleep", "snoring or breathing trouble at night",
      "memory or concentration problems", "fainting on standing", "urinary incontinence",
      "difficulty looking downward", "a family history of a similar illness",
      "weakness of the limbs or neck", "fever", "numbness", "recent antipsychotic medication"],
  inv={
   "neuronal surface antibody panel including anti-IgLON5":
       {"v": "STRONGLY POSITIVE for anti-IgLON5 (3+ on semi-quantitative grading, 1:10 serum "
             "dilution, transfected-cell assay)", "p": "reported", "decisive": True},
   "trunk posture: lateral flexion (Pisa) and antecollis, standing versus supine":
       {"v": "about 70 degrees of leftward trunk tilt on walking, with a normal stance; the tilt "
             "DISAPPEARS when recumbent", "p": "reported", "decisive": True},
   "MRI brain - cortical atrophy pattern": {"v": "MRI brain and whole spine NORMAL",
                                            "p": "reported", "decisive": True},
   "polysomnography":
       {"v": "NORMAL - the characteristic sleep architecture abnormality of anti-IgLON5 disease is "
             "absent here, which is why the diagnosis is missed", "p": "reported"},
   "paraneoplastic / onconeural antibody panel": {"v": "negative", "p": "reported"},
   "HIV, hepatitis B and hepatitis C serology": {"v": "negative", "p": "reported"},
   "cognitive screen (MoCA / MMSE / frontal assessment battery)":
       {"v": "conscious and oriented with normal attention and memory; normal Addenbrooke's score",
        "p": "reported"},
   "smooth pursuit and saccade velocity": {"v": "broken pursuit eye movements", "p": "reported"},
   "reflexes, plantar responses and frontal release signs":
       {"v": "normal power in limb and neck muscles, normal reflexes, flexor plantars",
        "p": "reported", "decisive": True},
   "full blood count, renal and liver profile":
       {"v": "haemogram, glucose, renal, liver, electrolytes and thyroid all normal",
        "p": "reported"},
   "MRI whole spine": {"v": "normal", "p": "reported"},
  },
  dont_miss="Rituximab arrested this illness and the patient was still improved at two years. "
            "Rapidly progressive extrapyramidal disease over weeks to months, with a normal MRI, "
            "is autoimmune until proven otherwise - send the neuronal surface antibody panel.",
  must_not="calling this multiple system atrophy or progressive supranuclear palsy with a Pisa "
           "syndrome, or blaming a drug, and not sending the antibody - the MRI is normal, the "
           "tilt resolves lying down, and the whole thing took two months"),
]

if __name__ == "__main__":
    build(LINE, PANEL, CASES)
