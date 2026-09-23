"""Functional movement disorder cases - the one line whose diagnosis lives at the bedside.

Every other line in this benchmark can in principle be settled by a test: an antibody, a gene, a
scan. This one cannot. Functional movement disorder is diagnosed by POSITIVE dynamic signs -
distractibility, entrainment, co-activation, suggestibility, the anticipatory jerk - each of which
is a manoeuvre the examiner performs and the video records. A model that only knows how to order
investigations will get a full sheet of normal results and no diagnosis.

The line therefore inverts the usual cost gradient: the decisive entries are almost all bedside,
and MRI / DaTSCAN / genetics are deliberately normal in six of seven cases.

The seventh case is the trap. Video 11 of PMC7455329 is a deliberately slow, broad-based, cautious
gait that reads as functional on sight - and is stiff-person syndrome, where anti-GAD65 and needle
EMG are decisive and missing it costs the patient an effective treatment. A model that has learned
"looks odd, walks strangely, therefore functional" from the other six is expected to fail here,
which is the point of including it.

Ages and sexes marked "not stated in source" are exactly that: PMC7455329 is a sign-based review
and PMC13206381 a teaching video, neither of which gives demographics. They are not invented.
"""
from genlib import build

LINE = "functional"

PANEL = {
    # bedside - the diagnostic core of this line
    "distractibility testing (complex motor task with the unaffected side)":
        {"tier": "bedside"},
    "entrainment testing (tap to an externally paced rhythm)":
        {"tier": "bedside"},
    "co-activation sign on passive movement of the affected limb":
        {"tier": "bedside"},
    "'whack-a-mole' sign (restrain the affected limb and watch the others)":
        {"tier": "bedside"},
    "anticipatory jerk to a feigned tendon-hammer approach (Hallett sign)":
        {"tier": "bedside"},
    "suggestibility / sham stimulus (tuning fork or vibration applied as 'treatment')":
        {"tier": "bedside"},
    "variability of amplitude, frequency and axis over the examination":
        {"tier": "bedside"},
    "Hoover sign / hip-abductor sign": {"tier": "bedside"},
    "tandem gait": {"tier": "bedside"},
    "walking backward": {"tier": "bedside"},
    "running": {"tier": "bedside"},
    "gait with a distracting or automatic task (dancing, counting backwards)":
        {"tier": "bedside"},
    "Romberg test, repeated with distraction": {"tier": "bedside"},
    "observation for excessive slowness or uneconomic posture":
        {"tier": "bedside"},
    "knee buckling / astasia-abasia on walking": {"tier": "bedside"},
    "muscle tone (spasticity, rigidity, paratonia)": {"tier": "bedside"},
    "deep tendon reflexes and plantar responses": {"tier": "bedside"},
    "cerebellar examination (finger-nose, dysdiadochokinesis, nystagmus)":
        {"tier": "bedside"},
    "finger-tapping for bradykinesia and decrement": {"tier": "bedside"},
    "MRC power in all four limbs": {"tier": "bedside"},
    "sensory examination (including midline splitting, allodynia)":
        {"tier": "bedside"},
    "cranial nerve examination": {"tier": "bedside"},
    "cognitive screen": {"tier": "bedside"},
    "psychosocial history (stressors, prior functional symptoms, illness beliefs)":
        {"tier": "bedside"},
    "trial of physiotherapy / motor retraining": {"tier": "bedside"},
    "trial of benzodiazepine (diazepam)": {"tier": "bedside"},
    "levodopa challenge": {"tier": "bedside"},
    # blood
    "full blood count, renal and liver profile": {"tier": "blood"},
    "TSH / free T4": {"tier": "blood"},
    "copper and ceruloplasmin": {"tier": "blood"},
    "creatine kinase": {"tier": "blood"},
    "vitamin B12 and vitamin E": {"tier": "blood"},
    "glucose / HbA1c": {"tier": "blood"},
    "anti-GAD65 antibodies": {"tier": "blood"},
    "neuronal surface / paraneoplastic antibody panel (amphiphysin, glycine receptor, DPPX)":
        {"tier": "blood"},
    "coeliac serology": {"tier": "blood"},
    "HIV and syphilis serology": {"tier": "blood"},
    "hereditary ataxia / repeat-expansion panel": {"tier": "blood"},
    "dystonia gene panel (including TOR1A)": {"tier": "blood"},
    "drug and toxin screen (neuroleptics, lithium, stimulants)": {"tier": "blood"},
    # imaging
    "MRI brain": {"tier": "imaging"},
    "MRI cervical and thoracic spine": {"tier": "imaging"},
    "DaTSCAN (dopamine transporter SPECT)": {"tier": "imaging"},
    "FDG-PET brain": {"tier": "imaging"},
    "CT chest / abdomen / pelvis (tumour search)": {"tier": "imaging"},
    # invasive / neurophysiology
    "surface EMG tremor analysis with accelerometry (frequency, coherence)":
        {"tier": "invasive"},
    "needle EMG (continuous motor unit activity at rest)":
        {"tier": "invasive"},
    "nerve conduction studies": {"tier": "invasive"},
    "back-averaged EEG for a Bereitschaftspotential before the movements":
        {"tier": "invasive"},
    "somatosensory evoked potentials (giant SEP, C-reflex)": {"tier": "invasive"},
    "jerk latency and burst-duration measurement": {"tier": "invasive"},
    "lumbar puncture / CSF (cells, protein, oligoclonal bands)": {"tier": "invasive"},
    "video-EEG monitoring with limb surface electrodes": {"tier": "invasive"},
}

CASES = [
 dict(
  video="functional_tremor_entrainment_PMC7713151.mp4", pmcid="PMC7713151",
  dx="Functional (psychogenic) tremor of the right arm, arising after years of pain and repeated "
     "surgery on that limb - entrainment, distractibility, co-activation and 'whack-a-mole' signs "
     "all positive, with normal neurophysiology and normal copper studies",
  sign="a coarse, high-amplitude, irregular right-arm tremor whose amplitude and rhythm change "
       "when the examiner moves, paces or restrains the other side",
  correct=["functional tremor", "psychogenic tremor", "functional movement disorder"],
  partial=["functional neurological disorder", "complex regional pain syndrome with tremor",
           "peripherally induced tremor"],
  who=dict(age=48, sex="female"),
  yes=["shaking of the right arm", "the shaking is coarse and large in amplitude",
       "the arm was operated on several times before the shaking began",
       "constant burning pain in the hand and forearm",
       "the skin of the hand hurts when it is lightly touched",
       "the tremor gets much worse with stress or physical effort",
       "the tremor stops completely during sleep",
       "the tremor stops while the other hand is busy with a task",
       "the tremor started suddenly rather than creeping on over years",
       "holding the shaking hand still makes the shoulder start moving instead",
       "the arm is hard to use in daily activities"],
  no=["alcohol makes the tremor better", "a family history of tremor",
      "slowness of movement", "a shuffling walk", "swelling or colour change of the hand",
      "sweating changes or temperature change in the hand", "hair or nail changes of the hand",
      "the tremor is present in the legs", "the tremor is present in the head",
      "double vision", "difficulty swallowing", "memory problems",
      "the tremor improved with pregabalin or gabapentin"],
  inv={
   "distractibility testing (complex motor task with the unaffected side)":
       {"v": "POSITIVE - the tremor decreases or stops when the left arm performs a task such as "
             "drinking from a cup", "p": "reported", "decisive": True},
   "entrainment testing (tap to an externally paced rhythm)":
       {"v": "POSITIVE - amplitude falls and the rhythm becomes irregular under repetitive "
             "voluntary movement of the other side", "p": "reported", "decisive": True},
   "co-activation sign on passive movement of the affected limb":
       {"v": "POSITIVE - movement of the contralateral arm co-activates the hand with an increase "
             "in tremor intensity", "p": "reported", "decisive": True},
   "'whack-a-mole' sign (restrain the affected limb and watch the others)":
       {"v": "POSITIVE - passive fixation of the hand increases movement in the arm and shoulder",
        "p": "reported", "decisive": True},
   "variability of amplitude, frequency and axis over the examination":
       {"v": "irregular, variable frequency around 4-6 Hz, at times combined with myoclonic jerks",
        "p": "reported", "decisive": True},
   "video-EEG monitoring with limb surface electrodes":
       {"v": "24 h recording with right-arm surface electrodes: irregular tremor, relatively high "
             "frequency with irregularities, no epileptiform correlate", "p": "reported",
        "decisive": True},
   "copper and ceruloplasmin": {"v": "normal - excludes Wilson disease", "p": "reported"},
   "nerve conduction studies": {"v": "unremarkable; carpal tunnel syndrome excluded",
                                "p": "reported"},
   "surface EMG tremor analysis with accelerometry (frequency, coherence)":
       {"v": "no abnormality of the kind seen in organic tremor", "p": "reported"},
   "sensory examination (including midline splitting, allodynia)":
       {"v": "burning pain with pronounced sensitivity to touch, fulfilling allodynia criteria",
        "p": "reported"},
   "observation for excessive slowness or uneconomic posture":
       {"v": "no bradykinesia, no parkinsonian features", "p": "reported"},
   "psychosocial history (stressors, prior functional symptoms, illness beliefs)":
       {"v": "years of intractable pain with pronounced psychosocial stress", "p": "reported"},
  },
  dont_miss="A limb with this surgical history genuinely can develop complex regional pain "
            "syndrome or a peripherally induced tremor, and the pain itself needs treating "
            "whatever the tremor turns out to be - but the trophic, sudomotor and vasomotor "
            "changes that would support CRPS are absent here.",
  must_not="calling this Parkinson disease, dystonic tremor or essential tremor and escalating to "
           "dopaminergic drugs or deep brain stimulation - the tremor entrains, distracts away and "
           "moves to the shoulder when the hand is held"),

 dict(
  video="functional_jerks_hallett_sign_PMC13206381.mp4", pmcid="PMC13206381",
  dx="Functional jerky movement disorder (functional myoclonus) demonstrating the 'Hallett sign' - "
     "an anticipatory jerk produced by the sight of the tendon hammer approaching, without the "
     "hammer ever striking the tendon",
  sign="the limb jerks as the examiner brings the tendon hammer towards it and stops short of "
       "contact, so the movement is triggered by the visual stimulus alone",
  correct=["functional myoclonus", "functional jerky movement disorder",
           "psychogenic myoclonus", "functional movement disorder"],
  partial=["functional neurological disorder", "stimulus-sensitive myoclonus",
           "startle syndrome"],
  who=dict(age="not stated in source (adult)", sex="not stated in source"),
  yes=["sudden jerks of the limbs", "the jerks happen when the doctor reaches towards the limb",
       "the jerks happen even when nothing touches the limb",
       "the jerks are triggered by seeing something coming",
       "the jerks vary from one moment to the next",
       "the jerks are distractible", "the rest of the neurological examination is normal"],
  no=["loss of consciousness with the jerks", "the jerks occur out of sleep",
      "the jerks are triggered by touch alone with the eyes closed",
      "a progressive decline in walking or memory", "seizures", "fever or recent severe illness",
      "cardiac arrest in the past", "a family history of jerks", "vision loss",
      "the jerks respond to levetiracetam or clonazepam"],
  inv={
   "anticipatory jerk to a feigned tendon-hammer approach (Hallett sign)":
       {"v": "POSITIVE - the jerk occurs when the hammer is stopped just short of the tendon, "
             "provoked by the visual stimulus alone", "p": "reported", "decisive": True},
   "jerk latency and burst-duration measurement":
       {"v": "long and VARIABLE latency with a long duration of muscle contraction - the pattern "
             "of voluntary movement, not of cortical myoclonus", "p": "reported",
        "decisive": True},
   "variability of amplitude, frequency and axis over the examination":
       {"v": "the jerks are inconsistent in size and timing", "p": "reported"},
   "cranial nerve examination": {"v": "normal - 'neurologic exam otherwise normal'",
                                 "p": "reported"},
  },
  dont_miss="Stimulus-sensitive myoclonus is also the presentation of cortical myoclonus and of "
            "post-hypoxic myoclonus, both of which are progressive and treatable - the "
            "back-averaged EEG and the SEP are what separate them, not the appearance of the jerk.",
  must_not="calling this cortical or reflex myoclonus and starting an antiepileptic escalation or "
           "a prion / encephalitis workup - the jerk fires when the hammer never lands, and it is "
           "preceded by a readiness potential"),

 dict(
  video="functional_head_tremor_vibration_PMC12999016.mp4", pmcid="PMC12999016",
  dx="Functional head tremor: a 'no-no' head tremor with functional upper-limb tremor that is "
     "triggered and modulated by an applied vibratory stimulus (suggestibility)",
  sign="a horizontal 'no-no' head tremor, with hand tremor, that appears or changes when the "
       "examiner applies a vibrating device to the patient",
  correct=["functional head tremor", "functional tremor", "functional movement disorder"],
  partial=["functional neurological disorder", "essential tremor with head tremor",
           "cervical dystonia with dystonic head tremor"],
  who=dict(age=83, sex="male"),
  yes=["the head shakes from side to side", "the hands also shake",
       "the head tremor comes on when a vibrating device is placed on the body",
       "the direction of the head tremor changes over time",
       "the tremor varies a lot from minute to minute",
       "the tremor lessens when attention is drawn elsewhere",
       "the tremor began abruptly"],
  no=["alcohol makes the tremor better", "a family history of tremor",
      "the head is pulled or held to one side", "neck pain", "a sensory trick helps the head",
      "slowness of movement", "a shuffling walk", "unsteadiness when walking",
      "double vision", "the voice shakes", "swallowing difficulty",
      "the tremor has crept on slowly over decades"],
  inv={
   "suggestibility / sham stimulus (tuning fork or vibration applied as 'treatment')":
       {"v": "POSITIVE - vibration triggers and modulates the head and limb tremor",
        "p": "reported", "decisive": True},
   "variability of amplitude, frequency and axis over the examination":
       {"v": "CHANGE IN TREMOR DIRECTIONALITY - specificity 0.91 for functional head tremor in "
             "the source cohort", "p": "reported", "decisive": True},
   "distractibility testing (complex motor task with the unaffected side)":
       {"v": "POSITIVE - marked decrease in tremor amplitude with distraction", "p": "reported",
        "decisive": True},
  },
  dont_miss="Head tremor in an 83-year-old is far more often essential tremor or dystonic head "
            "tremor, and functional tremor can sit on top of either - the positive signs are what "
            "make the call, not the absence of another diagnosis.",
  must_not="calling this essential tremor or cervical dystonia and offering botulinum toxin or "
           "thalamic surgery - the tremor is switched on by a vibrating device and changes axis"),

 dict(
  video="functional_head_tremor_distractibility_PMC12999016.mp4", pmcid="PMC12999016",
  dx="Functional head tremor: a 'no-no' head tremor with prominent distractibility, the tremor "
     "abating when the patient performs an unrelated non-finger motor task",
  sign="a side-to-side head tremor that dies away while the patient is occupied with another "
       "task and returns when the task stops",
  correct=["functional head tremor", "functional tremor", "functional movement disorder"],
  partial=["functional neurological disorder", "essential tremor with head tremor",
           "cervical dystonia with dystonic head tremor"],
  who=dict(age=61, sex="male"),
  yes=["the head shakes from side to side",
       "the head tremor stops while doing something else with the body",
       "the tremor returns as soon as the other task stops",
       "the tremor varies a lot from minute to minute",
       "the tremor changes direction at times", "the tremor began abruptly",
       "the tremor is worse when being watched"],
  no=["alcohol makes the tremor better", "a family history of tremor",
      "the head is pulled or held to one side", "neck pain", "a sensory trick helps the head",
      "slowness of movement", "unsteadiness when walking", "the voice shakes",
      "double vision", "swallowing difficulty", "weakness of the arms or legs",
      "the tremor has crept on slowly over decades"],
  inv={
   "distractibility testing (complex motor task with the unaffected side)":
       {"v": "POSITIVE and prominent - the head tremor abates during a non-finger motor task",
        "p": "reported", "decisive": True},
   "variability of amplitude, frequency and axis over the examination":
       {"v": "amplitude and directionality both vary during the examination", "p": "reported",
        "decisive": True},
  },
  dont_miss="A third of patients with functional tremor have head tremor and they carry greater "
            "overall functional-disorder severity - the head tremor is a marker to act on, not an "
            "isolated cosmetic complaint.",
  must_not="calling this essential tremor and starting propranolol or primidone, or calling it "
           "cervical dystonia and injecting botulinum toxin"),

 dict(
  video="functional_gait_incongruent_falling_PMC7455329.mp4", pmcid="PMC7455329",
  dx="Functional gait disorder with INCONGRUENT FALLING - the patient sinks to the floor twice "
     "during a short corridor walk, slowly and without a protective reaction, sustains no injury, "
     "and gets up and walks on unaided",
  sign="the patient collapses to the ground while walking, slowly and controlled, lies there, "
       "then rises and walks on with no injury - and does it again",
  correct=["functional gait disorder", "functional movement disorder",
           "psychogenic gait disorder"],
  partial=["functional neurological disorder", "syncope / drop attacks", "cataplexy"],
  who=dict(age="not stated in source (adult)", sex="male (apparent on the video)"),
  yes=["falling to the ground while walking", "falling repeatedly in a short time",
       "sinking down slowly rather than dropping", "never being injured by the falls",
       "getting up unaided after each fall", "being fully aware throughout the fall",
       "the problem began suddenly", "the legs feel as if they will not hold"],
  no=["loss of consciousness", "confusion after the fall", "tongue biting or incontinence",
      "the falls are triggered by laughter or emotion", "daytime sleep attacks",
      "palpitations or chest pain before the fall", "vertigo or spinning",
      "the falls happen backward without warning", "double vision", "slurred speech",
      "the problem has worsened steadily over years"],
  inv={
   "knee buckling / astasia-abasia on walking":
       {"v": "POSITIVE - the patient sinks to the floor twice during one corridor walk, slowly "
             "and without a protective reaction", "p": "reported", "decisive": True},
   "observation for excessive slowness or uneconomic posture":
       {"v": "INCONGRUENT - repeated falls with no injury at all, and an unaided recovery each "
             "time", "p": "reported", "decisive": True},
  },
  dont_miss="Repeated falls are also syncope, cardiac arrhythmia, cataplexy and atonic seizures - "
            "all of which injure the patient sooner or later, and the first two of which kill. "
            "The absence of any injury after repeated falls is the observation that separates "
            "them, not the appearance of the fall itself.",
  must_not="admitting this as recurrent syncope or atonic seizures and starting an antiepileptic "
           "or a pacemaker workup - the descent is slow and controlled, awareness is preserved "
           "throughout, and nothing is ever hurt"),

 dict(
  video="functional_gait_scissoring_PMC7455329.mp4", pmcid="PMC7455329",
  dx="Functional gait disorder producing a scissoring pattern - the scissoring disappears on "
     "walking backward, whereas true spastic scissoring persists in both directions",
  sign="the legs cross over each other on walking forward in a scissoring pattern that is not "
       "present when the same patient walks backward",
  correct=["functional gait disorder", "functional movement disorder"],
  partial=["functional neurological disorder", "psychogenic gait disorder",
           "spastic paraparesis"],
  who=dict(age="not stated in source (adult)", sex="female (apparent on the video)"),
  yes=["the legs cross over each other when walking", "the crossing is absent when walking "
       "backward", "the walking pattern changes from one attempt to the next",
       "the problem began suddenly", "walking is effortful and slow",
       "the legs feel stiff to the patient"],
  no=["stiffness that the examiner can feel in the legs", "leg spasms at night",
      "loss of bladder control", "numbness with a level on the trunk",
      "a family history of stiff or spastic legs", "back pain",
      "the problem has worsened steadily over years", "difficulty with the arms",
      "slurred speech", "double vision", "the legs are wasted"],
  inv={
   "walking backward":
       {"v": "the scissoring DISAPPEARS on walking backward; in spasticity it persists",
        "p": "reported", "decisive": True},
  },
  dont_miss="Hereditary spastic paraplegia, cervical myelopathy, B12 deficiency and multiple "
            "sclerosis all scissor - all of them keep scissoring when the patient walks backward, "
            "and all of them raise tone and reflexes on examination.",
  must_not="diagnosing hereditary spastic paraplegia or a cord compression and proceeding to "
           "decompressive surgery or baclofen escalation in a patient with normal tone, normal "
           "reflexes and flexor plantars"),

 dict(
  video="mimic_stiff_person_gait_PMC7455329.mp4", pmcid="PMC7455329",
  dx="STIFF-PERSON SYNDROME - a deliberately slow, broad-based, cautious gait that looks "
     "functional at the bedside; the characteristic lumbar hyperlordosis is absent in this "
     "patient, which is exactly why the gait is mistaken for a functional one",
  sign="an extremely slow, wide-based, guarded walk with crutches, held rigid, with no lumbar "
       "hyperlordosis to give the diagnosis away",
  correct=["stiff-person syndrome", "stiff person syndrome", "anti-GAD65 stiff-person syndrome"],
  partial=["autoimmune encephalomyelitis", "progressive encephalomyelitis with rigidity and "
           "myoclonus", "spastic paraparesis"],
  who=dict(age="not stated in source (adult)", sex="male (apparent on the video)"),
  yes=["walking is extremely slow and wide-based", "the legs and trunk feel stiff",
       "painful muscle spasms", "the spasms are triggered by sudden noise or being startled",
       "the spasms are triggered by emotional upset", "falling like a statue without protecting",
       "fear of walking in open spaces", "the stiffness has worsened over months to years",
       "diazepam eases the stiffness", "there is another autoimmune disease (type 1 diabetes)"],
  no=["the walking is normal when running", "the walking is normal when walking backward",
      "the walking is normal in tandem", "the pattern changes when distracted",
      "the problem began suddenly", "double vision", "memory loss",
      "loss of bladder control", "numbness in the legs", "weakness of the arms"],
  inv={
   "walking backward": {"v": "the slow, guarded, wide-based pattern PERSISTS", "p": "reported",
                        "decisive": True},
   "running": {"v": "cannot run; the pattern does not normalise", "p": "reported",
               "decisive": True},
   "observation for excessive slowness or uneconomic posture":
       {"v": "deliberately slow and broad-based; lumbar hyperlordosis is LACKING in this patient",
        "p": "reported"},
  },
  dont_miss="This is the treatable one. High-dose benzodiazepines, and then IVIG or rituximab, "
            "change the course of stiff-person syndrome; a patient labelled functional loses all "
            "of it and is sent to physiotherapy for a disease that physiotherapy alone does not "
            "touch.",
  must_not="calling this a functional gait disorder because the walk looks exaggerated - it does "
           "not distract away, it does not normalise on running or walking backward, and the tone "
           "is genuinely raised"),
]

if __name__ == "__main__":
    build(LINE, PANEL, CASES)
