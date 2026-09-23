# Prompts

Every prompt used in the benchmark is reproduced below, verbatim except that runtime substitutions are shown as angle-bracketed placeholders. They fall into four groups: what the model under evaluation is asked (section *model*), what the environment is asked in order to answer it from the case record (section *env*), what builds the retrieved candidate space (section *retrieval*), and what grades the result (section *grading*).

## The model under evaluation

### Part 1, from the video alone

Sent with K frames as interleaved images.

```text
You are a doctor. Below are <K> frame(s) sampled in order across a ~<duration>
second video of a patient.

Describe what you see, then give your primary guess of the disease. You may list
several possible diagnoses.
```

### Part 2, turn 1: the history

The opening clause carries the role under test (*You are a neurologist seeing a new patient* or *You are a doctor seeing a new patient*); all reported runs use the latter. The candidate block is present only in the retrieval arm.

```text
<role> Above are <K> frames sampled across a <duration>-second video of the
consultation, in order.

<candidate block, retrieval arm only>You may now take a history, but under one
constraint: **Ask yes/no questions. The environment returns yes, no, or unknown
when the record does not establish the answer**, and the patient will answer only
yes, no, or unknown. Anything you do not ask, you do not learn.

Ask as many or as few questions as you judge this patient needs. Stop when you
believe another question would not change what you think is wrong. Put them in the
order you would ask them - most informative first.

One question per line, numbered. Nothing else.
```

In the blinded arm the frames are omitted and the first paragraph is replaced by:

```text
You are a doctor. A new patient has been referred to you and you have not yet seen
or examined them. You know nothing about them at all.
```

The candidate block, when present, precedes the constraint:

```text
A literature search on the signs visible in this video returned the following
reported causes. The list is not guaranteed to contain this patient's cause, and
most entries in it are wrong for this patient:

<candidate causes>
```

### Part 2, turn 2: the investigations

```text
The patient answered:

<numbered questions, each with yes or no>

You may now investigate. There is no fixed list to choose from - name whatever you
would actually order, in your own words: bedside examination manoeuvres, blood
tests, imaging, electrophysiology, invasive procedures, or a therapeutic trial. A
therapeutic trial is returned only if you name that specific trial; asking to "try
treatment" returns nothing.

Order as many or as few investigations as you judge this patient needs. Stop when
another test would not change what you think is wrong. Most likely to settle the
diagnosis first.

One investigation per line, numbered. Name the test, not what you expect it to
show. Nothing else.
```

### Part 2, turn 3: the diagnosis

```text
The results are:

<one block per order: the order as written, then the chart entries it covered with
their values, or "not performed / not available">

For orders marked "not performed / not available", no documented result is
available in this environment. Do not infer a result.

Now give your diagnosis. State the single diagnosis you believe is correct - the
disease entity and its cause, as specifically as the evidence allows - then, on
separate lines, up to three alternatives you would still consider.

Begin with "DIAGNOSIS:" followed by the single answer on one line.
```

## The environment

Both prompts below align free text with the case record. The patient prompt returns yes/no/unknown responses based only on documented features. The chart prompt returns matching entry names, and the harness retrieves their recorded results. Neither prompt is permitted to invent clinical findings.

### The patient

The environment answers each question from the documented symptom table: `yes` for an established finding, `no` for an explicitly absent finding, and `unknown` when the record is insufficient. Omission from the table indicates unreported information, not a negative finding. Missing documentation never implies `no`; a compound question receives `yes` or `no` only when the evidence resolves the whole question.

```text
A doctor asked a patient these yes/no questions:

<numbered questions>

The patient's documented features are:

<the case's symptom table>

Answer each question using only the documented features above.

Use exactly one of the following responses:
- "yes" if the documented features explicitly establish that the complete
  statement is true;
- "no" if the documented features explicitly establish that the complete
  statement is false;
- "unknown" if the documented features do not provide enough information
  to determine whether the complete statement is true or false.

Do not infer unreported features. Absence from the documented feature table
does not imply absence of the clinical finding and must not by itself produce
a "no" response.

For compound questions, return yes or no only when the documented
evidence determines the truth of the complete statement.
Otherwise, return unknown.

Reply with ONLY a JSON object:

{"<question number>": "yes"|"no"|"unknown", ...}
```

### The chart

```text
A doctor ordered these investigations. A numbered line may bundle several tests.

<numbered orders>

This chart holds results for exactly these entries:

<the case's investigation menu, therapeutic trials marked [NAMED-ONLY]>

For each numbered order, list the chart entries it covers - matching on what the
test is, not on wording. An order covers an entry only if it genuinely asks for
that test. Entries marked [NAMED-ONLY] are therapeutic trials: list one only if
that specific trial is named, never for a general request to try treatment.

Reply with ONLY a JSON object mapping each order number to a list of chart entry
names, exactly as written above: {"1": ["..."], "2": [], ...}
```

## Retrieval

### Normalisation

The model's description is rewritten into canonical terms before it is matched against HPO. The step is a vocabulary translation and is never shown the diagnosis.

```text
Rewrite the clinical description below as a list of standard neurological
phenomenology terms, the kind used as headings in a movement-disorder textbook.

Rules:
- one term per line, nothing else, no numbering, no explanation
- use the canonical noun form: "Gait ataxia", "Chorea", "Resting tremor",
  "Ptosis", "Nystagmus", "Bradykinesia", "Dystonia", "Myoclonus", "Facial palsy",
  "Spasticity"
- include the body region as a separate term when the description gives one
- when the description states a side or a distribution, add it on its own line
  using exactly one of: Unilateral, Bilateral, Left, Right, Generalized, Focal,
  Multifocal, Axial, Proximal, Distal, Alternating laterality
- include only what the description actually states; do not infer a diagnosis
- if the description states no abnormality, output the single line NONE

Description:
<the model's own description of the sign>
```

### Extraction

Applied to the titles and abstract openings returned by the Europe PMC query.

```text
Below are published papers, all retrieved because they describe the same clinical
sign. Each entry is a title followed by the start of its abstract.

For each entry, name the underlying CAUSE or DISEASE it was about, in four words
or fewer. If the paper is a review that enumerates several causes, list them
separated by " ; ". One entry per line, in the same order, nothing else. Write
SKIP if no cause is named.

<titles and abstract openings>
```

## Grading

### Part 1: the sign and the differential

```text
You are grading a vision model that was shown a short clinical video of one
patient and asked, with NO history and NO test results, to describe what it saw
and name the disease. It answered in free prose, so read the whole answer and
extract its position.

GROUND TRUTH
  true diagnosis : <true diagnosis>
  the sign a competent viewer should name from the clip : <reference sign>
  answers to score as CORRECT (the actual disease entity) : <accept-as-correct>
  answers to score as PARTIAL (right syndrome or category, but not the cause) :
    <accept-as-partial>

THE MODEL'S ANSWER (free prose)
<the answer>

Grade on two axes, using the same standard you would apply to a structured answer.

SIGN - did it name the visible abnormality correctly?
  correct : names the same phenomenology as the ground-truth sign anywhere in the
            prose (synonyms count: "ataxic gait" for "unsteady wide-based walking")
  partial : describes the abnormality in the right body region but names the wrong
            phenomenology, or describes it only vaguely without naming a sign
  wrong   : names a different phenomenology, wrong body region, or says nothing
            abnormal is visible

DIAGNOSIS - the prose may list several. Treat the one it presents first or most
confidently as dx1, the next two as dx2 and dx3, and leave a slot "wrong" if it
offered fewer.
  correct : the same disease entity as the true diagnosis or as one of the CORRECT
            list, at comparable specificity. A strictly vaguer answer is NOT
            correct.
  partial : matches the PARTIAL list, or is the right syndrome/category but not the
            cause, or is the correct entity named too vaguely.
  wrong   : anything else.

Reply with ONLY this JSON, no prose around it:
{"sign":"correct|partial|wrong",
 "dx1":"correct|partial|wrong",
 "dx2":"correct|partial|wrong",
 "dx3":"correct|partial|wrong",
 "best":"correct|partial|wrong",
 "reason":"<= 12 words"}
```

### Part 1: the uncapped rank probe

Models list more diagnoses than the three slots above admit, so the aetiology reported in \S comes from this probe, which reads the whole answer and returns the rank of the first entry judged correct.

```text
A model was shown frames from a video of one patient and asked to describe what it
saw and to name the disease, listing as many alternative diagnoses as it wished.

TRUE DIAGNOSIS: <true diagnosis>
Also acceptable as correct: <accept-as-correct>

THE MODEL'S ANSWER:
<the answer>

Read the whole answer and list, in the order the model presents them, every
distinct diagnosis it offers. Then give the position of the first one that is
correct - the same disease entity as the truth or as an acceptable answer, at
comparable specificity. A strictly vaguer answer is not correct. Use 0 if none of
them is correct.

Reply with ONLY {"n_listed": <int>, "rank": <int>}
```

### Part 2: the committed diagnosis

Only the primary diagnosis is graded; the alternatives the model is allowed to append are recorded but not credited.

```text
You are grading a doctor who watched a video of a patient, took a yes/no history,
ordered investigations, and then named a diagnosis.

GROUND TRUTH
  true diagnosis : <true diagnosis>
  count as CORRECT (the actual disease entity) : <accept-as-correct>
  count as PARTIAL (right syndrome or category, not the cause) : <accept-as-partial>

THE DOCTOR'S PRIMARY DIAGNOSIS
<the diagnosis>

Grade the primary diagnosis alone.
  exact    : the same disease entity as the truth or the CORRECT list, at
             comparable specificity
  core     : the right syndrome or the right cause but not both, or the correct
             entity named too vaguely to act on
  category : only the right broad family of disease
  none     : anything else

Reply with ONLY {"grade":"exact|core|category|none","reason":"<= 12 words"}
```
