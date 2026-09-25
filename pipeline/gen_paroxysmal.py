"""Paroxysmal-event cases, rebuilt on documented aetiologies.

Four labels change. The two clips called status epilepticus are not status at all - they are two
further patients from a series on ictal body turning in GENERALIZED epilepsy. The epilepsia
partialis continua clip is the presenting manifestation of familial Creutzfeldt-Jakob disease.
And the myoclonic-seizure clip is benign action myoclonus after general anaesthesia, which is
not epileptic.

Semiology is what this line tests, so the panel keeps the elements of a seizure description as
separate orderable items alongside the electrophysiology.
"""
from genlib import build

LINE = "paroxysmal"

PANEL = {
    "witnessed description of the event": {"v": "not obtained", "p": "derived", "tier": "bedside"},
    "duration of the events": {"v": "not recorded", "p": "derived", "tier": "bedside"},
    "time of day / relation to sleep": {"v": "no clear relation", "p": "derived",
                                        "tier": "bedside"},
    "trigger or provoking activity": {"v": "none identified", "p": "derived", "tier": "bedside"},
    "aura before the event": {"v": "none", "p": "derived", "tier": "bedside"},
    "awareness and recall during the event": {"v": "preserved", "p": "derived", "tier": "bedside"},
    "post-event confusion or sleepiness": {"v": "none", "p": "derived", "tier": "bedside"},
    "tongue biting, incontinence or injury": {"v": "none", "p": "derived", "tier": "bedside"},
    "stereotypy across events": {"v": "events are stereotyped", "p": "derived", "tier": "bedside"},
    "developmental and birth history": {"v": "unremarkable", "p": "derived", "tier": "bedside"},
    "family history of epilepsy or febrile convulsions": {"v": "none", "p": "derived",
                                                          "tier": "bedside"},
    "head injury history": {"v": "none", "p": "derived", "tier": "bedside"},
    "medication and anaesthetic exposure": {"v": "nothing relevant", "p": "derived",
                                            "tier": "bedside"},
    "cognitive screen (MMSE)": {"v": "normal", "p": "derived", "tier": "bedside"},
    "neurological examination between events": {"v": "normal", "p": "derived", "tier": "bedside"},
    "full blood count and biochemistry": {"v": "normal", "p": "derived", "tier": "blood"},
    "glucose, calcium, magnesium, sodium": {"v": "normal", "p": "derived", "tier": "blood"},
    "liver and renal function": {"v": "normal", "p": "derived", "tier": "blood"},
    "toxicology and drug levels": {"v": "negative", "p": "derived", "tier": "blood"},
    "metabolic screen (tandem mass spectrometry, urine organic acids)": {"v": "normal",
                                                                        "p": "derived",
                                                                        "tier": "blood"},
    "autoimmune and paraneoplastic antibody panel": {"v": "negative", "p": "derived",
                                                     "tier": "blood"},
    "genetic testing (exome / epilepsy panel)": {"v": "no pathogenic variant", "p": "derived",
                                                 "tier": "blood"},
    "chromosomal microarray": {"v": "no copy number abnormality", "p": "derived", "tier": "blood"},
    "brain MRI": {"v": "no epileptogenic lesion", "p": "derived", "tier": "imaging"},
    "advanced diffusion imaging / tractography": {"v": "not performed", "p": "derived",
                                                  "tier": "imaging"},
    "interictal EEG": {"v": "no epileptiform discharges", "p": "derived", "tier": "invasive"},
    "video-EEG monitoring of a typical event": {"v": "no ictal correlate captured",
                                                "p": "derived", "tier": "invasive"},
    "video-polygraphy (EEG with EMG)": {"v": "not performed", "p": "derived", "tier": "invasive"},
    "provocation testing (the suspected trigger)": {"v": "not performed", "p": "derived",
                                                    "tier": "invasive"},
    "lumbar puncture / CSF": {"v": "normal", "p": "derived", "tier": "invasive"},
    "CSF 14-3-3 / RT-QuIC (prion)": {"v": "negative", "p": "derived", "tier": "invasive"},
    "antiseizure medication trial": {"v": "not started", "p": "derived", "tier": "bedside"},
}

STATUS_SHARED = {
   "video-EEG monitoring of a typical event": {"v": "ictal BODY TURNING, often preceded by head "
                                                    "version, but the EEG shows classic "
                                                    "GENERALIZED spike-wave or polyspike "
                                                    "discharges WITHOUT consistent lateralization",
                                               "p": "reported", "decisive": True},
   "interictal EEG": {"v": "runs of generalized polyspikes and spike-wave discharges at 2-3 Hz "
                           "lasting 3-4 s, predominating bifrontally and occasionally shifting "
                           "laterally", "p": "reported", "decisive": True},
   "brain MRI": {"v": "no focal epileptogenic lesion", "p": "reported"},
   "family history of epilepsy or febrile convulsions": {"v": "family history of epilepsy in 25% "
                                                              "of the series; three patients had "
                                                              "personal febrile convulsions",
                                                         "p": "reported"},
}

CASES = [
 dict(
  video="mild_1_EPC_PMC13276695.mp4", pmcid="PMC13276695",
  dx="EPILEPSIA PARTIALIS CONTINUA as the presenting manifestation of FAMILIAL "
     "Creutzfeldt-Jakob disease",
  sign="continuous small rhythmic jerking of one hand, with the rest of the body still",
  correct=["Creutzfeldt-Jakob disease", "familial CJD presenting with epilepsia partialis "
           "continua", "prion disease"],
  partial=["epilepsia partialis continua", "focal motor status epilepticus",
           "focal epilepsy"],
  who=dict(age=48, sex="male"),
  yes=["continuous small twitching of one hand", "the twitching does not stop",
       "the twitching is on the left side", "the twitching involves the wrist and fingers",
       "the events are not followed by confusion", "thinking and memory are still normal",
       "a relative with a similar rapidly progressive illness"],
  no=["loss of awareness during the events", "tongue biting", "incontinence",
      "the jerks stop with sleep", "a head injury", "recent infection", "fever",
      "the jerks are triggered by movement", "generalized shaking", "a new medication"],
  inv={
   "video-polygraphy (EEG with EMG)": {"v": "lateralized periodic discharges over the RIGHT "
                                            "fronto-central-temporal region, TIME-LOCKED with "
                                            "brief EMG bursts under 100 ms in the LEFT wrist "
                                            "flexors and extensors - electrophysiological proof "
                                            "of epilepsia partialis continua", "p": "reported",
                                       "decisive": True},
   "brain MRI": {"v": "restricted diffusion with matching T2/FLAIR hyperintensity in the right "
                      "caudate, anterior lentiform nucleus, cingulate gyrus and insula, and less "
                      "prominently the right frontal, parietal and temporal cortex",
                 "p": "reported", "decisive": True},
   "interictal EEG": {"v": "generalized periodic discharges recurring every 1-2 seconds as the "
                           "illness progressed", "p": "reported", "decisive": True},
   "cognitive screen (MMSE)": {"v": "26 - cognition still preserved at presentation",
                               "p": "reported"},
   "genetic testing (exome / epilepsy panel)": {"v": "PRNP mutation - familial CJD, which accounts "
                                                    "for about 10-15% of cases and is most often "
                                                    "E200K", "p": "reported", "decisive": True},
   "CSF 14-3-3 / RT-QuIC (prion)": {"v": "positive", "p": "derived", "decisive": True},
   "antiseizure medication trial": {"v": "epilepsia partialis continua in CJD is typically "
                                         "refractory to antiseizure drugs", "p": "derived"},
  },
  dont_miss="Epilepsia partialis continua that resists antiseizure drugs, with basal-ganglia and "
            "cortical restricted diffusion, is prion disease; the family history changes "
            "counselling for relatives.",
  must_not="treating it as ordinary focal status epilepticus and escalating antiseizure drugs "
           "without imaging and prion testing"),

 dict(
  video="mild_2_myoclonus_PMC12798911.mp4", pmcid="PMC12798911",
  dx="Delayed-onset BENIGN ACTION MYOCLONUS following general anaesthesia with propofol and "
     "thiopentone - NOT an epileptic seizure",
  sign="brief shock-like jerks of the trunk and upper limbs",
  correct=["benign action myoclonus after anaesthesia", "post-anaesthetic myoclonus",
           "propofol-related myoclonus"],
  partial=["cortical-reflex myoclonus", "myoclonic seizures", "drug-induced myoclonus"],
  who=dict(age=78, sex="female"),
  yes=["jerky movements of the trunk and arms", "the jerks came on days after an operation",
       "recent heart surgery", "having had a general anaesthetic",
       "the jerks are brought on by movement", "the jerks are limited to part of the body",
       "the jerks resolved within days of starting treatment", "no relapse afterwards"],
  no=["loss of awareness during the jerks", "tongue biting", "incontinence",
      "confusion afterwards", "a family history of epilepsy", "a head injury", "fever",
      "cognitive decline", "the jerks continue during sleep", "a previous seizure"],
  inv={
   "medication and anaesthetic exposure": {"v": "propofol and thiopentone for coronary artery "
                                                "bypass grafting with aortic valve replacement; "
                                                "jerks began 6 days later (day 3 in the second "
                                                "case)", "p": "reported", "decisive": True},
   "interictal EEG": {"v": "occasional OCCIPITAL SHARP WAVES only (normal in the second patient) "
                           "- no ictal pattern", "p": "reported", "decisive": True},
   "trigger or provoking activity": {"v": "action-induced and restricted to a few body segments, "
                                          "suggesting cortical-reflex myoclonus", "p": "reported",
                                     "decisive": True},
   "antiseizure medication trial": {"v": "complete resolution within 4 days on clonazepam 0.25 mg "
                                         "twice daily and levetiracetam 500 mg twice daily, with "
                                         "no relapse on follow-up", "p": "reported",
                                    "decisive": True},
   "brain MRI": {"v": "no acute lesion", "p": "derived"},
  },
  dont_miss="Myoclonus appearing days after an anaesthetic is usually benign and self-limiting; "
            "recognise it so the patient is not labelled epileptic for life.",
  must_not="diagnosing a myoclonic epilepsy - awareness is preserved, the EEG shows no ictal "
           "pattern, and it resolved in four days without recurrence"),

 dict(
  video="mild_3_neonatal_PMC12440885.mp4", pmcid="PMC12440885",
  dx="Poirier-Bienvenu neurodevelopmental syndrome from a CSNK2B missense variant "
     "(c.268A>C, p.Thr90Pro), manifesting primarily as EYELID MYOCLONIA (Jeavons syndrome)",
  sign="subtle eyelid fluttering and brief behavioural arrest in a young child",
  correct=["Poirier-Bienvenu neurodevelopmental syndrome", "CSNK2B-related epilepsy",
           "genetic developmental and epileptic encephalopathy"],
  partial=["Jeavons syndrome", "eyelid myoclonia with absences", "developmental epileptic "
           "encephalopathy"],
  who=dict(age=4, sex="female"),
  yes=["fluttering of the eyelids", "brief pauses in activity", "developmental delay",
       "the events happen many times a day", "the events are very short",
       "the events started in early childhood", "the eyes roll upwards during the events"],
  no=["a family history of epilepsy", "a head injury", "recent infection", "fever with the events",
      "tongue biting", "incontinence", "the events last minutes", "a recent anaesthetic",
      "the events only happen during sleep", "loss of previously acquired skills"],
  inv={
   "genetic testing (exome / epilepsy panel)": {"v": "missense variant in exon 4 of CSNK2B "
                                                    "(NM_001320.7 c.268A>C, p.Thr90Pro), likely "
                                                    "pathogenic by ACMG; threonine 90 is "
                                                    "evolutionarily conserved", "p": "reported",
                                                "decisive": True},
   "brain MRI": {"v": "punctate FLAIR hyperintensities in the local white matter of both frontal "
                      "lobes", "p": "reported"},
   "chromosomal microarray": {"v": "no copy number abnormality", "p": "reported"},
   "metabolic screen (tandem mass spectrometry, urine organic acids)": {"v": "no abnormality",
                                                                       "p": "reported"},
   "video-EEG monitoring of a typical event": {"v": "eyelid myoclonia with absences - the Jeavons "
                                                    "phenotype", "p": "reported", "decisive": True},
   "developmental and birth history": {"v": "neurodevelopmental delay", "p": "reported"},
  },
  dont_miss="Eyelid myoclonia with developmental delay warrants an epilepsy gene panel; a "
            "CSNK2B result names the syndrome, guides drug choice and ends the diagnostic "
            "odyssey.",
  must_not="calling the eyelid fluttering a tic or a behaviour - it is an ictal phenomenon on "
           "video-EEG"),

 dict(
  video="moderate_1_hypermotor_PMC5786569.mp4", pmcid="PMC5786569",
  dx="ACQUIRED sleep-related hypermotor epilepsy with disrupted white matter tracts, following "
     "repetitive mild traumatic brain injury",
  sign="an abrupt, short burst of vigorous thrashing arising from sleep, with vocalisation",
  correct=["sleep-related hypermotor epilepsy", "frontal lobe epilepsy",
           "post-traumatic hypermotor epilepsy"],
  partial=["nocturnal frontal lobe epilepsy", "parasomnia", "REM sleep behaviour disorder"],
  who=dict(age=36, sex="male"),
  yes=["the events happen at night out of sleep", "the events start abruptly",
       "the events are short, about fifteen seconds", "vigorous thrashing movements",
       "unstructured noises during the events", "the events are the same every time",
       "the events have been happening for two years",
       "repeated mild head injuries in the past", "military service"],
  no=["the events happen during the day", "a family history of epilepsy",
      "tongue biting", "incontinence", "prolonged confusion afterwards",
      "the events last several minutes", "acting out dreams that can be recalled",
      "a recent anaesthetic", "fever", "cognitive decline"],
  inv={
   "video-EEG monitoring of a typical event": {"v": "the diagnosis was made on SEMIOLOGY from "
                                                    "clinically documented video-EEG; there was NO "
                                                    "interpretable ictal EEG correlate because of "
                                                    "movement artefact", "p": "reported",
                                               "decisive": True},
   "duration of the events": {"v": "about 15 seconds", "p": "reported", "decisive": True},
   "time of day / relation to sleep": {"v": "predominantly out of sleep at night", "p": "reported",
                                       "decisive": True},
   "head injury history": {"v": "mild repetitive non-penetrating traumatic brain injury, none "
                                "requiring hospitalisation", "p": "reported", "decisive": True},
   "advanced diffusion imaging / tractography": {"v": "multishell diffusion MRI showed disrupted "
                                                     "white matter tracts", "p": "reported",
                                                 "decisive": True},
   "awareness and recall during the event": {"v": "anamnestic - the patient has no recall",
                                             "p": "reported"},
  },
  dont_miss="A normal ictal EEG does not exclude sleep-related hypermotor epilepsy - up to 30% "
            "are extrafrontal and movement artefact obscures the trace, so the diagnosis rests "
            "on the semiology.",
  must_not="dismissing it as a parasomnia or a functional event because the EEG shows no ictal "
           "correlate"),

 dict(
  video="moderate_2_shadowbox_PMC9062418.mp4", pmcid="PMC9062418",
  dx="SHADOWBOXING-INDUCED REFLEX SEIZURES in focal epilepsy - a movement-induced (praxis) reflex "
     "epilepsy of left frontal to anterior temporal onset",
  sign="a vigorous stereotyped hyperkinetic seizure triggered by punching movements",
  correct=["reflex epilepsy", "exercise-induced reflex seizures",
           "shadowboxing-induced focal seizures"],
  partial=["focal epilepsy", "hyperkinetic seizure", "movement-induced seizure"],
  who=dict(age=26, sex="male"),
  yes=["the events only happen during a specific activity",
       "the events happen when shadowboxing or punching",
       "the events start about 10 to 20 seconds after starting the activity",
       "a sensation in the head just before the event", "speech stops during the event",
       "behaviour freezes during the event", "the head and body turn during the event",
       "the events happen about once a week", "the events have increased in frequency"],
  no=["a family history of epilepsy", "febrile convulsions as a child", "a head injury",
      "the events happen at rest", "the events happen during sleep", "learning difficulties",
      "tongue biting", "incontinence", "a recent anaesthetic", "fever"],
  inv={
   "provocation testing (the suspected trigger)": {"v": "supervised shadowboxing of 3 minutes per "
                                                       "trial reproduced the seizures, with "
                                                       "induction latencies of about 11 seconds "
                                                       "and durations around 18 seconds",
                                                   "p": "reported", "decisive": True},
   "interictal EEG": {"v": "intermittent sharp waves from the LEFT FRONTAL to anterior temporal "
                           "regions", "p": "reported", "decisive": True},
   "video-EEG monitoring of a typical event": {"v": "moderate-amplitude rhythmic THETA waves "
                                                    "intermittently during the versive seizures",
                                               "p": "reported", "decisive": True},
   "aura before the event": {"v": "a cephalic aura immediately before speech and behavioural "
                                  "arrest", "p": "reported"},
   "trigger or provoking activity": {"v": "exclusively provoked by shadowboxing; exercise-induced "
                                          "seizures occur in about 2% of people with epilepsy",
                                     "p": "reported"},
   "head injury history": {"v": "no head trauma", "p": "reported"},
   "family history of epilepsy or febrile convulsions": {"v": "none, including febrile seizures",
                                                         "p": "reported"},
  },
  dont_miss="Ask what the patient was doing: seizures locked to one specific activity are reflex "
            "epilepsy, and supervised provocation under video-EEG confirms it rather than months "
            "of ambulatory monitoring.",
  must_not="labelling vigorous activity-triggered events as functional or as exercise-induced "
           "syncope without provocation testing"),

 dict(
  video="moderate_3_reaching_PMC6230673.mp4", pmcid="PMC6230673",
  dx="POST-TRAUMATIC epilepsy with seizures manifesting as a stereotyped REACHING/GRASPING "
     "movement of the hemiplegic arm, of left frontal origin",
  sign="a repeated stereotyped reaching and grasping movement of one arm",
  correct=["post-traumatic epilepsy", "frontal lobe seizure with reaching/grasping",
           "focal epilepsy after traumatic brain injury"],
  partial=["hyperkinetic seizure", "frontal lobe epilepsy", "automatism"],
  who=dict(age=23, sex="male"),
  yes=["a repeated reaching movement of the arm", "the movement is the same every time",
       "weakness of the right side of the body", "a serious head injury in the past",
       "having been thrown from a horse", "the arm takes a twisted posture during the movement",
       "no memory of the events"],
  no=["a family history of epilepsy", "the events happen only in sleep",
      "the events are triggered by exercise", "recent infection", "fever",
      "a recent anaesthetic", "cognitive decline since childhood", "tongue biting",
      "the events last several minutes", "the events stopped on their own"],
  inv={
   "interictal EEG": {"v": "repetitive sharp waves predominantly in the LEFT FRONTAL area during "
                           "sleep, with pseudocontinuous 3 Hz slow waves in the same region on "
                           "awakening", "p": "reported", "decisive": True},
   "head injury history": {"v": "traumatic brain injury after being thrown from a horse",
                           "p": "reported", "decisive": True},
   "neurological examination between events": {"v": "right-sided hemiplegia, manual muscle testing "
                                                    "grade 1", "p": "reported", "decisive": True},
   "witnessed description of the event": {"v": "the right arm reaches and grasps and takes a "
                                               "DYSTONIC posture during the movement, despite a "
                                               "manual muscle testing score of 1 - the movement is "
                                               "ictal, not voluntary", "p": "reported",
                                          "decisive": True},
   "awareness and recall during the event": {"v": "the patient could not recall the events",
                                             "p": "reported"},
   "brain MRI": {"v": "post-traumatic encephalomalacia", "p": "derived"},
  },
  dont_miss="A purposeful-looking movement in a limb that is too weak to perform it voluntarily "
            "is an ictal automatism; the mismatch between MMT 1 and the reaching movement is the "
            "clue.",
  must_not="interpreting the reaching as voluntary behaviour or as a functional movement"),

 dict(
  video="severe_1_generalized_PMC13101308.mp4", pmcid="PMC13101308",
  dx="GENERALIZED epilepsy with ictal BODY TURNING and head version - the turning has no "
     "lateralizing value here, because the EEG shows generalized discharges",
  sign="a generalized convulsion with the body turning during the seizure",
  correct=["generalized epilepsy", "genetic generalized epilepsy with ictal body turning",
           "generalized tonic-clonic seizure"],
  partial=["focal seizure with secondary generalization", "gyratory seizure",
           "tonic-clonic seizure"],
  who=dict(age=26, sex="female"),
  yes=["the body turns during the seizure", "the head turns first",
       "generalized shaking", "brief blank spells as well",
       "a family history of epilepsy in a more distant relative", "being born prematurely",
       "mild developmental delay", "loss of awareness during the events"],
  no=["the events are triggered by a specific activity", "the events only occur in sleep",
      "a head injury", "a recent anaesthetic", "recent infection", "fever",
      "continuous twitching of one hand", "the seizure lasted more than five minutes",
      "failure to wake up between seizures"],
  inv=dict(STATUS_SHARED, **{
   "video-EEG monitoring of a typical event": {"v": "ictal body turning preceded by head version; "
                                                    "although the clinical onset looked focal, the "
                                                    "EEG showed generalized beta fast activity for "
                                                    "0.5 s followed by a generalized 2.5-3 Hz "
                                                    "spike-wave discharge with maximum bifrontal "
                                                    "amplitude", "p": "reported", "decisive": True},
   "developmental and birth history": {"v": "preterm birth with mild developmental delay",
                                       "p": "reported"},
   "family history of epilepsy or febrile convulsions": {"v": "epilepsy in a second-degree "
                                                              "relative", "p": "reported"},
  }),
  dont_miss="Body turning and head version look focal but do not localise in generalized epilepsy; "
            "getting this wrong sends the patient down a surgical work-up instead of onto a "
            "broad-spectrum antiseizure drug.",
  must_not="calling it a focal seizure with secondary generalization on the turning alone - the "
           "EEG is generalized from the outset"),

 dict(
  video="severe_status_real_PMC13101308c2.mp4", pmcid="PMC13101308",
  dx="GENERALIZED epilepsy with ictal body turning - the second patient of the series; NOT "
     "refractory status epilepticus",
  sign="convulsive activity with the body rotating during the seizure",
  correct=["generalized epilepsy", "genetic generalized epilepsy with ictal body turning",
           "gyratory generalized seizure"],
  partial=["focal seizure with secondary generalization", "convulsive seizure",
           "status epilepticus"],
  who=dict(age=24, sex="female"),
  yes=["the body rotates during the seizure", "the head turns before the body",
       "generalized shaking", "loss of awareness during the events",
       "febrile convulsions as a young child", "the seizures respond to medication"],
  no=["the seizure continued for more than thirty minutes",
      "failure to regain consciousness between seizures",
      "needing intensive care and anaesthetic infusions",
      "the events are triggered by a specific activity", "a head injury", "recent infection",
      "fever now", "continuous twitching of one hand", "a recent anaesthetic"],
  inv=dict(STATUS_SHARED, **{
   "family history of epilepsy or febrile convulsions": {"v": "personal history of febrile "
                                                              "convulsions", "p": "reported"},
   "antiseizure medication trial": {"v": "responded to appropriate broad-spectrum antiseizure "
                                         "medication - NOT refractory", "p": "derived",
                                    "decisive": True},
  }),
  dont_miss="Ictal body turning in a generalized epilepsy is a semiological curiosity, not "
            "evidence of a focal onset; the treatment is a broad-spectrum drug.",
  must_not="diagnosing refractory or super-refractory status epilepticus - the seizures are "
           "self-limiting and respond to medication"),

 dict(
  video="severe_status_real_PMC13101308c3.mp4", pmcid="PMC13101308",
  dx="GENERALIZED epilepsy with ictal body turning - the third patient of the series; NOT "
     "convulsive status epilepticus",
  sign="repeated convulsive activity with turning of the trunk",
  correct=["generalized epilepsy", "genetic generalized epilepsy with ictal body turning",
           "gyratory generalized seizure"],
  partial=["convulsive seizure", "status epilepticus", "focal seizure with secondary "
           "generalization"],
  who=dict(age=29, sex="male"),
  yes=["turning of the trunk during the seizure", "the head turns first",
       "generalized shaking", "loss of awareness during the events",
       "a family history of epilepsy", "recovery of awareness between seizures"],
  no=["the seizure continued for more than thirty minutes",
      "failure to regain consciousness between seizures",
      "needing intensive care and anaesthetic infusions", "a head injury",
      "the events are triggered by a specific activity", "recent infection", "fever now",
      "continuous twitching of one hand", "a recent anaesthetic"],
  inv=dict(STATUS_SHARED, **{
   "awareness and recall during the event": {"v": "awareness recovers between seizures - this is "
                                                  "not status epilepticus", "p": "derived",
                                             "decisive": True},
   "family history of epilepsy or febrile convulsions": {"v": "family history of epilepsy",
                                                         "p": "reported"},
  }),
  dont_miss="Status epilepticus is defined by duration and by failure to recover between "
            "seizures; neither is present here, and the label changes the whole emergency "
            "pathway.",
  must_not="treating this as convulsive status epilepticus - awareness returns between events"),
]

build(LINE, PANEL, CASES)
