"""Dystonia cases, rebuilt on documented aetiologies.

Three change disease entirely: the clip labelled Wilson disease is type-III GM1 gangliosidosis,
the clip labelled a basal-ganglia structural lesion is dystonia from longitudinally extensive
cervical myelitis, and the tardive clip is methotrexate-induced. A fourth, the blepharospasm
clip, is Meige syndrome - segmental, not the isolated focal dystonia it was labelled.

The single most important item in this panel is the levodopa trial: dopa-responsive dystonia is
the one cause here that a cheap oral drug reverses, and it is routinely missed for years.
"""
from genlib import build

LINE = "dystonia"

PANEL = {
    "distribution of the dystonia (focal, segmental, generalized)": {"tier": "bedside"},
    "sensory trick (geste antagoniste)": {"tier": "bedside"},
    "action specificity and task dependence": {"tier": "bedside"},
    "diurnal fluctuation (worse towards evening)": {"tier": "bedside"},
    "levodopa trial": {"tier": "bedside"},
    "medication and toxin exposure history": {"tier": "bedside"},
    "family history": {"tier": "bedside"},
    "speech assessment": {"tier": "bedside"},
    "eye movements and reflexes": {"tier": "bedside"},
    "cognitive screen": {"tier": "bedside"},
    "slit-lamp examination for Kayser-Fleischer rings": {"tier": "bedside"},
    "dystonia rating scale (BFM / OMDRS)": {"tier": "bedside"},
    "full blood count and biochemistry": {"tier": "blood"},
    "liver function": {"tier": "blood"},
    "copper / caeruloplasmin / 24 h urinary copper": {"tier": "blood"},
    "TSH / free T4": {"tier": "blood"},
    "calcium, phosphate and parathyroid hormone": {"tier": "blood"},
    "anti-aquaporin-4 and anti-MOG antibodies": {"tier": "blood"},
    "autoimmune and paraneoplastic antibody panel": {"tier": "blood"},
    "dystonia gene panel": {"tier": "blood"},
    "lysosomal enzyme assay (beta-galactosidase, hexosaminidase)": {"tier": "blood"},
    "ESR / CRP": {"tier": "blood"},
    "brain MRI": {"tier": "imaging"},
    "cervical and whole spine MRI": {"tier": "imaging"},
    "DAT-SPECT": {"tier": "imaging"},
    "needle EMG of the affected muscles": {"tier": "invasive"},
    "lumbar puncture / CSF": {"tier": "invasive"},
    "botulinum toxin trial": {"tier": "invasive"},
}

CASES = [
 dict(
  video="mild_blepharospasm_idiopathic_PMC13049410.mp4", pmcid="PMC13049410",
  dx="MEIGE SYNDROME - segmental cranial dystonia combining blepharospasm with oromandibular "
     "dystonia; drug-refractory for 16 years and treated with botulinum toxin",
  sign="forceful involuntary eye closure",
  correct=["Meige syndrome", "segmental cranial dystonia",
           "blepharospasm with oromandibular dystonia"],
  partial=["blepharospasm", "focal dystonia", "oromandibular dystonia"],
  who=dict(age=59, sex="female"),
  yes=["involuntary squeezing of the eyes", "frowning that cannot be controlled",
       "twitching around the mouth", "the spasms are worse when speaking",
       "the spasms are worse when eating", "headaches at night",
       "the problem has been present for 16 years", "it has got worse over the years",
       "previous drug treatments did not work", "the smile shows too much gum",
       "the mouth pulls to one side"],
  no=["a family history of the same illness", "taking an antipsychotic",
      "taking a nausea medication", "tremor", "limb involvement", "sudden onset",
      "improvement during sleep only", "cognitive problems", "liver disease",
      "eye pain", "visual loss"],
  inv={
   "distribution of the dystonia (focal, segmental, generalized)": {"v": "SEGMENTAL - eyelids "
                                                                        "plus perioral and jaw "
                                                                        "muscles, not isolated "
                                                                        "blepharospasm",
                                                                   "p": "reported",
                                                                   "decisive": True},
   "dystonia rating scale (BFM / OMDRS)": {"v": "gingival exposure on maximal involuntary smile "
                                                ">4 mm (severe), reduced to 1 mm after treatment",
                                           "p": "reported", "decisive": True},
   "action specificity and task dependence": {"v": "spasms provoked by speech and eating",
                                              "p": "reported"},
   "botulinum toxin trial": {"v": "marked improvement in facial spasms within one week; nocturnal "
                                  "headaches resolved and facial asymmetry corrected",
                             "p": "reported", "decisive": True},
   "medication and toxin exposure history": {"v": "no dopamine-blocking drug exposure - not "
                                                  "tardive", "p": "reported"},
  },
  dont_miss="Look below the eyes: blepharospasm that comes with perioral and jaw spasms is Meige "
            "syndrome, and botulinum toxin works within a week where oral drugs had failed for "
            "years.",
  must_not="calling it isolated blepharospasm - the perioral and jaw involvement makes it "
           "segmental, which changes where the toxin is injected"),

 dict(
  video="moderate_genetic_DYT_PMC9982172.mp4", pmcid="PMC9982172",
  dx="Late-onset DYT6 dystonia from a pathogenic THAP1 variant (c.505C>T, p.Arg169*, "
     "heterozygous), with severe retrocollis, perioral dystonia and spasmodic speech",
  sign="sustained twisting postures of the neck and upper limbs",
  correct=["DYT6 dystonia", "THAP1-related dystonia", "inherited isolated dystonia"],
  partial=["genetic dystonia", "segmental dystonia", "cervical dystonia"],
  who=dict(age=42, sex="male"),
  yes=["the head pulls backwards", "twisting of the neck", "twisting of both arms",
       "strained, spasmodic speech", "twisting around the mouth",
       "the problem started later than childhood"],
  no=["taking an antipsychotic", "taking a nausea medication", "a stroke", "recent head injury",
      "liver disease", "rings around the coloured part of the eye", "diurnal fluctuation",
      "improvement with a small dose of levodopa", "cognitive decline", "limb weakness",
      "abnormal eye movements"],
  inv={
   "dystonia gene panel": {"v": "pathogenic THAP1 variant c.505C>T (p.Arg169*), heterozygous - "
                                "DYT6", "p": "reported", "decisive": True},
   "distribution of the dystonia (focal, segmental, generalized)": {"v": "perioral dystonia, "
                                                                        "severe retrocollis from "
                                                                        "the upper back to the "
                                                                        "neck, and bilateral "
                                                                        "upper limb dystonia",
                                                                   "p": "reported"},
   "speech assessment": {"v": "spasmodic speech", "p": "reported", "decisive": True},
   "dystonia rating scale (BFM / OMDRS)": {"v": "Burke-Fahn-Marsden score 34", "p": "reported"},
   "eye movements and reflexes": {"v": "normal saccades and pursuit; normal deep tendon and "
                                       "plantar reflexes", "p": "reported"},
   "deep brain stimulation (GPi)": {"v": "performed in three patients in this series, two improved",
                                    "p": "reported", "tier": "invasive"},
  },
  dont_miss="Speech involvement with cranio-cervical dystonia points at THAP1; send the gene "
            "panel, because DYT6 has about 60% penetrance and the result matters for the family.",
  must_not="assuming a tardive dystonia without any dopamine-blocker exposure, or missing a "
           "levodopa trial before committing to surgery"),

 dict(
  video="moderate_secondary_structural_PMC12962376.mp4", pmcid="PMC12962376",
  dx="Generalized dystonia secondary to LONGITUDINALLY EXTENSIVE TRANSVERSE MYELITIS confined to "
     "the cervical spinal cord, of uncertain aetiology (AQP4 and MOG negative)",
  sign="fixed twisting postures of the trunk, neck and limbs",
  correct=["dystonia secondary to cervical myelitis",
           "longitudinally extensive transverse myelitis", "spinal cord lesion causing dystonia"],
  partial=["secondary dystonia", "structural dystonia", "neuromyelitis optica spectrum disorder"],
  who=dict(age=62, sex="female"),
  yes=["twisting of the neck to one side", "the neck also rotates", "twisting of the trunk",
       "abnormal posturing of the limbs", "the symptoms improved after steroid treatment"],
  no=["taking an antipsychotic", "taking a nausea medication", "a family history of the same "
      "illness", "rings around the coloured part of the eye", "liver disease",
      "cognitive problems", "abnormal eye movements", "diurnal fluctuation",
      "improvement with a small dose of levodopa", "optic nerve symptoms", "visual loss"],
  inv={
   "cervical and whole spine MRI": {"v": "LONGITUDINALLY EXTENSIVE T2 lesion confined to the "
                                         "cervical cord", "p": "reported", "decisive": True},
   "needle EMG of the affected muscles": {"v": "prolonged bursts, overflow activation and "
                                               "simultaneous agonist-antagonist contraction, with "
                                               "NO denervation or myopathy - confirms dystonic "
                                               "hypertonia", "p": "reported", "decisive": True},
   "anti-aquaporin-4 and anti-MOG antibodies": {"v": "BOTH NEGATIVE - not neuromyelitis optica or "
                                                     "MOG-antibody disease", "p": "reported",
                                                "decisive": True},
   "distribution of the dystonia (focal, segmental, generalized)": {"v": "laterocollis and "
                                                                        "rotacollis with "
                                                                        "generalized involvement",
                                                                   "p": "reported"},
   "eye movements and reflexes": {"v": "normal higher mental function and intact cranial nerves",
                                  "p": "reported"},
   "corticosteroid trial": {"v": "high-dose intravenous methylprednisolone 1 g/day for five days "
                                 "followed by an oral taper", "p": "reported", "tier": "invasive",
                            "decisive": True},
  },
  dont_miss="Image the SPINAL CORD in unexplained generalized dystonia; a cervical myelitis is "
            "treatable with steroids and would be missed by brain imaging alone.",
  must_not="attributing it to a basal-ganglia stroke or tumour - the brain is normal and the "
           "lesion is in the cervical cord"),

 dict(
  video="moderate_tardive_PMC10656108.mp4", pmcid="PMC10656108",
  dx="METHOTREXATE-induced oromandibular dystonia, misdiagnosed as Meige syndrome for five and a "
     "half years; it improved when methotrexate was switched to sulfasalazine",
  sign="sustained jaw, lip and tongue spasms",
  correct=["methotrexate-induced dystonia", "drug-induced oromandibular dystonia",
           "medication-induced dystonia"],
  partial=["oromandibular dystonia", "Meige syndrome", "tardive dystonia"],
  who=dict(age=70, sex="male"),
  yes=["spasms of the jaw and mouth", "the tongue pushes out involuntarily",
       "the spasms start when he begins to speak", "no spasms at rest",
       "the problem has lasted more than five years", "psoriatic arthritis",
       "taking a weekly tablet for the arthritis for six years",
       "the spasms improved after that tablet was changed"],
  no=["taking an antipsychotic long term", "taking a nausea medication",
      "a family history of the same illness", "rings around the coloured part of the eye",
      "liver disease", "limb involvement", "cognitive decline", "abnormal eye movements",
      "diurnal fluctuation", "tremor"],
  inv={
   "medication and toxin exposure history": {"v": "methotrexate 15 mg weekly for six years for "
                                                  "psoriatic arthritis; the dystonia improved "
                                                  "after switching to sulfasalazine",
                                             "p": "reported", "decisive": True},
   "dystonia rating scale (BFM / OMDRS)": {"v": "Oromandibular Dystonia Rating Scale 177 at "
                                                "baseline, 103 three months after the drug switch, "
                                                "75 after adding botulinum toxin", "p": "reported",
                                           "decisive": True},
   "action specificity and task dependence": {"v": "dystonia appears on INITIATING SPEECH; "
                                                   "asymptomatic at rest", "p": "reported",
                                              "decisive": True},
   "brain MRI": {"v": "cranioencephalic MRI showed no abnormality", "p": "reported"},
   "botulinum toxin trial": {"v": "added at eight weeks with further improvement", "p": "reported"},
   "trial of risperidone": {"v": "4 mg gave moderate improvement but was stopped for adverse "
                                 "effects", "p": "reported", "tier": "bedside"},
  },
  dont_miss="Review every long-term drug, not just antipsychotics; a disease-modifying "
            "antirheumatic drug caused this, and switching it improved a dystonia that had been "
            "called idiopathic for five years.",
  must_not="accepting the referral diagnosis of Meige syndrome without taking a full drug history"),

 dict(
  video="severe_dopa_responsive_PMC9357509.mp4", pmcid="PMC9357509",
  dx="DOPA-RESPONSIVE DYSTONIA presenting as isolated foot dystonia, with a dramatic response "
     "within four days of starting levodopa and no treatment-related fluctuations",
  sign="abnormal inward posturing of the feet with difficulty walking",
  correct=["dopa-responsive dystonia", "Segawa disease", "GTP cyclohydrolase deficiency"],
  partial=["isolated foot dystonia", "juvenile dystonia", "juvenile parkinsonism"],
  who=dict(age=19, sex="female"),
  yes=["abnormal posturing of both feet", "increasing difficulty walking",
       "the problem came on gradually over two months",
       "the symptoms improved dramatically within days of starting a tablet",
       "being a young woman"],
  no=["taking an antipsychotic", "taking a nausea medication", "a family history of the same "
      "illness", "rings around the coloured part of the eye", "liver disease",
      "arm or neck involvement", "cognitive problems", "abnormal eye movements",
      "recent head injury", "tremor at rest", "movement fluctuations on treatment"],
  inv={
   "levodopa trial": {"v": "DRAMATIC improvement within FOUR DAYS, sustained, with no "
                           "treatment-related fluctuations", "p": "reported", "decisive": True},
   "distribution of the dystonia (focal, segmental, generalized)": {"v": "isolated dystonia of "
                                                                        "both feet",
                                                                   "p": "reported"},
  },
  dont_miss="Every young person with unexplained dystonia deserves a levodopa trial; this one "
            "reversed within four days, and untreated dopa-responsive dystonia is routinely "
            "mislabelled as cerebral palsy for years.",
  must_not="proceeding to botulinum toxin or surgery without first trying levodopa"),

 dict(
  video="severe_wilson_PMC12904113.mp4", pmcid="PMC12904113",
  dx="Type-III (adult/chronic) GM1 GANGLIOSIDOSIS presenting as a combined dystonic movement "
     "disorder - a late-onset lysosomal storage disease with 5-10% residual beta-galactosidase "
     "activity",
  sign="generalized twisting postures of the limbs and trunk",
  correct=["GM1 gangliosidosis", "type-III GM1 gangliosidosis", "lysosomal storage disorder"],
  partial=["generalized dystonia", "young-onset dystonia", "Wilson disease"],
  who=dict(age=17, sex="male"),
  yes=["twisting postures of the limbs", "twisting of the trunk", "slurred speech",
       "the problem began in adolescence", "it has progressed slowly",
       "short stature or skeletal changes", "parents who are related to each other"],
  no=["rings around the coloured part of the eye", "liver disease", "jaundice",
      "taking an antipsychotic", "taking a nausea medication", "sudden onset",
      "improvement with a small dose of levodopa", "recent infection", "a stroke",
      "diurnal fluctuation"],
  inv={
   "lysosomal enzyme assay (beta-galactosidase, hexosaminidase)": {"v": "REDUCED "
                                                                       "beta-galactosidase, with "
                                                                       "5-10% residual activity - "
                                                                       "type-III GM1 "
                                                                       "gangliosidosis",
                                                                  "p": "reported",
                                                                  "decisive": True},
   "dystonia gene panel": {"v": "biallelic GLB1 variants", "p": "reported", "decisive": True},
   "brain MRI": {"v": "bilateral putaminal signal change typical of type-III GM1 gangliosidosis",
                 "p": "reported"},
  },
  dont_miss="Young-onset generalized dystonia with normal copper studies is not Wilson disease - "
            "send lysosomal enzymes, because type-III GM1 gangliosidosis presents exactly this "
            "way and the diagnosis changes counselling and family screening.",
  must_not="diagnosing Wilson disease on the phenotype alone - copper studies are normal and "
           "there are no Kayser-Fleischer rings"),
]

build(LINE, PANEL, CASES)
