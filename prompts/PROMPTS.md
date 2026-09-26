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

<numbered questions, each with yes, no, or unknown>

You may now investigate. There is no fixed list to choose from.
Name whatever you would actually order, in your own words:
bedside examination manoeuvres, blood tests, imaging,
electrophysiology, invasive procedures, or a therapeutic trial.
A therapeutic trial is returned only if you name that specific
trial. Asking to "try treatment" returns nothing.

Order as many or as few investigations as you judge this patient
needs. Stop when another test would not change what you think is
wrong. Put the investigations most likely to settle the diagnosis
first.

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
and propose possible diagnoses.

Evaluate two separate outcomes:
(1) recognition of the visible phenomenology;
(2) coverage of a diagnostic hypothesis compatible with the reference case.

Diagnostic coverage does NOT require exact identification of the confirmed
disease. A clinically appropriate syndrome or broader aetiological category
may qualify under the case-specific acceptance criteria below.

GROUND TRUTH
  confirmed diagnosis : <true diagnosis>
  reference visible phenomenology : <reference sign>
  additional hypotheses accepted as COVERAGE, including qualifying syndromes
  and broader aetiological categories : <accept-as-coverage>
  related but insufficient hypotheses, NOT accepted as coverage :
    <related-but-not-covered>

THE MODEL'S ANSWER (free prose)
<the answer>

Read the whole answer. Grade SIGN and DIAGNOSIS independently.
Correct sign recognition does not by itself establish diagnostic coverage,
and an incorrect sign description does not rule out diagnostic coverage.

SIGN - did it identify the visible abnormality?
  correct : identifies the reference phenomenology or an equivalent physical
            description anywhere in the answer; clinical synonyms count.
  partial : describes a relevant abnormality in the correct body region,
            but the description is incomplete or too vague to establish
            the reference phenomenology.
  wrong   : identifies an incompatible phenomenology or the wrong body
            region, or does not describe a relevant visible abnormality.

DIAGNOSIS - does a proposed hypothesis cover the reference case?
  correct : identifies the confirmed disease or an equivalent diagnosis,
            OR identifies a syndrome or broader aetiological category
            included in the case-specific COVERAGE list.
            Equivalent clinical terminology is accepted.
            Exact disease identification and equal specificity to the
            confirmed diagnosis are NOT required for accepted hypotheses.
  partial : proposes a clinically related hypothesis that does not satisfy
            the COVERAGE criteria, including an entry in the
            related-but-not-covered list.
  wrong   : proposes an incompatible or unrelated hypothesis, or does not
            propose a diagnostic hypothesis.

Apply these rules:
- Do not reject an accepted hypothesis merely because it is broader than
  the confirmed disease.
- Do not automatically accept every broad syndrome or disease category.
  Broad hypotheses must match the case-specific COVERAGE list or an
  equivalent clinical expression.
- Merely repeating the visible sign does not establish coverage unless
  that expression also names an explicitly accepted diagnostic syndrome.
- Count hypotheses the model proposes as possibilities, even if they are
  not its leading diagnosis.
- Do not count a diagnosis mentioned only to deny or explicitly rule it out.
- Do not infer a diagnostic hypothesis that the model did not express.

Assign dx1 to the explicitly designated primary diagnosis, if present;
otherwise use the first proposed diagnosis. Assign dx2 and dx3 to the next
two distinct proposed diagnoses in presentation order.
Use "wrong" for missing slots.

Assign best using ALL distinct proposed diagnoses in the complete answer,
including diagnoses beyond dx3:
  correct : at least one hypothesis is graded correct.
  partial : none is correct, but at least one is partial.
  wrong   : all are wrong, or no diagnostic hypothesis is proposed.

The binary aetiological-coverage outcome is 1 if best is "correct",
and 0 otherwise. Partial hypotheses do not receive coverage credit.

Reply with ONLY this JSON:
{"sign":"correct|partial|wrong",
 "dx1":"correct|partial|wrong",
 "dx2":"correct|partial|wrong",
 "dx3":"correct|partial|wrong",
 "best":"correct|partial|wrong",
 "reason":"<= 12 words"}
```

### Part 1: the uncapped rank probe

This probe reads the complete answer and records the number of distinct proposed diagnoses and the rank of the first hypothesis satisfying the case-specific aetiological-coverage criteria (paper, Section 3.3). Accepted syndromes and broader aetiological categories qualify; exact identification of the confirmed disease is not required.

```text
A model was shown frames from a video of one patient and asked to describe
what it saw and propose possible diagnoses, with no history or test results.

TRUE DIAGNOSIS: <true diagnosis>
Additional hypotheses accepted as COVERAGE, including qualifying
syndromes and broader aetiological categories: <accept-as-coverage>
Related but insufficient hypotheses, NOT accepted as coverage:
<related-but-not-covered>

THE MODEL'S ANSWER:
<the answer>

Read the whole answer and list, in order of first appearance, every
distinct diagnosis proposed as a possibility. Merge synonymous entries
and exclude diagnoses mentioned only to rule them out.

Return the rank of the first hypothesis that covers the reference case:
either the confirmed disease or an explicitly accepted syndrome or
broader aetiological category. Equivalent clinical terminology counts.
Exact disease identification and equal specificity to the confirmed
diagnosis are NOT required. Do not accept other broad hypotheses unless
equivalent to an explicitly accepted hypothesis. Merely repeating the
visible sign does not qualify unless it names an accepted syndrome.

n_listed is the total number of distinct proposed diagnoses.
rank is the 1-based position of the first qualifying hypothesis.
Use rank = 0 if none qualifies. Consider the entire list, not only
the first three entries.

Reply with ONLY {"n_listed": <int>, "rank": <int>}
```

### Part 2: the committed diagnosis

Only the primary diagnosis is graded; the alternatives the model is allowed to append are recorded but not credited. The two lists are the case's `final_diagnosis.accept_as_accurate` and `final_diagnosis.accept_as_partial` in `data/cases.json`.

```text
You are grading a doctor who watched a video of a patient, took a yes/no history,
ordered investigations, and then named a diagnosis.

GROUND TRUTH
  true diagnosis : <true diagnosis>
  count as accurate (the actual disease entity) : <accept-as-accurate>
  Accepted as partial: <accept-as-partial>

THE DOCTOR'S PRIMARY DIAGNOSIS
<the diagnosis>

Grade the primary diagnosis alone.
  accurate : matches a case-specific accepted correct diagnosis,
             including an accepted broader disease or syndrome
             formulation; equivalent clinical terminology counts
  partial  : matches the case-specific partial-credit criteria,
             including a related syndrome, cause, or broad disease
             family, but does not satisfy the correct-answer criteria
  none     : satisfies neither the correct-answer criteria nor
             the partial-credit criteria

Reply with ONLY {"grade":"accurate|partial|none","reason":"<= 12 words"}
```

## Other prompts used by the released scripts

The sections above are the benchmark prompts of the paper's Appendix H. The prompts below are the
remaining ones the scripts send, copied from the code as written (Python `%s` / `{name}` fields are
runtime substitutions; doubled braces are literal braces). Those marked optional or "not a paper
condition" are off by default.

### Stage 2, own words / reference / window arms / retrieval conditions: turn 1 without frames

`eval/part2_full.py`, `T1_TEXT`

```text
You are a doctor. A new patient has been referred to you. You have not seen or
examined them yourself, but a colleague who did records the following:

%s

You may now take a history, but under one constraint: **Ask yes/no questions. The environment
returns yes, no, or unknown when the record does not establish the answer**, and the patient will
answer only yes, no, or unknown. Anything you do not ask, you do not learn.

Ask as many or as few questions as you judge this patient needs. Stop when you believe another
question would not change what you think is wrong. Put them in the order you would ask them - most
informative first.

One question per line, numbered. Nothing else.
```

### Stage 2, referral-letter variant (CHIEF=1, not a paper condition)

`eval/part2_full.py`, `T1_CHIEF`

```text
You are a doctor. A new patient has been referred to you and you have not yet seen
or examined them. All you have been told is this:

  %s

You may now take a history, but under one constraint: **Ask yes/no questions. The environment
returns yes, no, or unknown when the record does not establish the answer**, and the patient will
answer only yes, no, or unknown. Anything you do not ask, you do not learn.

Ask as many or as few questions as you judge this patient needs. Stop when you believe another
question would not change what you think is wrong. Put them in the order you would ask them - most
informative first.

One question per line, numbered. Nothing else.
```

### Stage 2, hypothesis-first investigation turn (ORDERSTYLE=hypothesis, not a paper condition)

`eval/part2_full.py`, `T2_HYPO`

```text
The patient answered:

%s

Before investigating, state the diagnosis you currently think most likely, and up to three
alternatives you would want to exclude.

Then order investigations. For each one, name the test and the hypothesis it is meant to confirm or
exclude. Order only tests whose result would change what you think; do not order a test whose
result you can already predict. A therapeutic trial is returned only if you name that specific
trial.

Reply in exactly this format, nothing else:
LEADING: <one line>
ALTERNATIVES: <up to three, one per line>
1. <test> --- <the hypothesis it discriminates>
2. <test> --- <the hypothesis it discriminates>
...
```

### Oracle evidence: the diagnosis turn

`eval/part2_full.py`, `T3_ORACLE`

```text
The patient answered:

%s

The investigations that established this patient's diagnosis have been carried out for you. Their
results are:

%s

Now give your diagnosis. State the single diagnosis you believe is correct - the disease entity
and its cause, as specifically as the evidence allows - then, on separate lines, up to three
alternatives you would still consider.

Begin with "DIAGNOSIS:" followed by the single answer on one line.
```

### Multi-turn consultation: opening turn

`eval/part2_seq2.py`, `T1`

```text
%s Above are %d frames sampled across a
%s-second video of the consultation, in order.

You will now work through this patient in rounds. In each round you may do exactly ONE of
these three things, and you will see its result before the next round:

  ASK:
  1. <a question the patient can answer with yes or no>
  2. <another one>
  ... as many or as few as you want in this round

  ORDER:
  1. <an investigation - a bedside examination manoeuvre, a blood test, imaging,
     electrophysiology, an invasive procedure, or a therapeutic trial>
  2. <another one>
  ... as many or as few as you want in this round

  DIAGNOSIS: <your final diagnosis, on one line>

The rules:
  - the patient answers only yes, no, or unknown - unknown when the record does not establish the
    answer - and anything you do not ask you do not learn
  - name the investigation you actually want; a vague request returns nothing, and a therapeutic
    trial is returned only if you name that specific trial
  - you may ask again after seeing results, and order again after asking again, in whatever
    order you like - let each round decide what the next one should be
  - you have at most %d rounds. Stop as soon as another round would not change what you think is
    wrong, and give DIAGNOSIS then - you do not have to use the rounds you do not need
  - in DIAGNOSIS, name the disease entity and its cause, as specifically as the evidence allows

Begin your reply with ASK:, ORDER: or DIAGNOSIS: and write nothing else.
```

### Multi-turn consultation: opening turn, Blind

`eval/part2_seq2.py`, `T1_NOVID`

```text
You are a doctor. A new patient has been referred to you and you have not yet seen
or examined them. You know nothing about them at all.

You will now work through this patient in rounds. In each round you may do exactly ONE of
these three things, and you will see its result before the next round:

  ASK:
  1. <a question the patient can answer with yes or no>
  2. <another one>
  ... as many or as few as you want in this round

  ORDER:
  1. <an investigation - a bedside examination manoeuvre, a blood test, imaging,
     electrophysiology, an invasive procedure, or a therapeutic trial>
  2. <another one>
  ... as many or as few as you want in this round

  DIAGNOSIS: <your final diagnosis, on one line>

The rules:
  - the patient answers only yes, no, or unknown - unknown when the record does not establish the
    answer - and anything you do not ask you do not learn
  - name the investigation you actually want; a vague request returns nothing, and a therapeutic
    trial is returned only if you name that specific trial
  - you may ask again after seeing results, and order again after asking again, in whatever
    order you like - let each round decide what the next one should be
  - you have at most %d rounds. Stop as soon as another round would not change what you think is
    wrong, and give DIAGNOSIS then - you do not have to use the rounds you do not need
  - in DIAGNOSIS, name the disease entity and its cause, as specifically as the evidence allows

Begin your reply with ASK:, ORDER: or DIAGNOSIS: and write nothing else.
```

### Multi-turn consultation: reply that is neither questions, orders nor a diagnosis

`eval/part2_seq2.py`, `NUDGE`

```text
That was not one of the three allowed moves. The first line of your reply must be
exactly "ASK:", exactly "ORDER:", or "DIAGNOSIS: <diagnosis>". Write the word, then the items.
```

### Multi-turn consultation: rounds exhausted

`eval/part2_seq2.py`, `LAST`

```text
You have used all %d rounds. Give your diagnosis now. State the single diagnosis you
believe is correct - the disease entity and its cause, as specifically as the evidence allows.

Begin with "DIAGNOSIS:" followed by the single answer on one line.
```

### Investigation-selection controls (Appendix C.3): budget / checklist / random investigation turn

`eval/controls/part2_orders.py`, `T2_BUDGET`

```text
The patient answered:

%s

You may now investigate. There is no fixed list to choose from - name whatever you would actually
order, in your own words: bedside examination manoeuvres, blood tests, imaging, electrophysiology,
invasive procedures, or a therapeutic trial. A therapeutic trial is returned only if you name that
specific trial; asking to "try treatment" returns nothing.

You have a budget of exactly %d investigations. Each numbered line must name ONE single test and
nothing else. Do not combine several tests on one line, do not join them with "and", "plus", "with"
or a comma-separated list, and do not write a category that stands for many tests, such as "routine
bloods", "metabolic screen" or "full neurological examination". Spend the budget on the tests most
likely to settle the diagnosis.

Exactly %d lines, numbered, one investigation per line. Name the test, not what you expect it to
show. Nothing else.
```

### Investigation-selection controls: one-entry release rule (atomic checklist and single-entry arms)

`eval/controls/part2_orders.py`, `MATCH_ONE`

```text
A doctor ordered these investigations, one test per line.

%s

This chart holds results for exactly these entries:

%s

For each numbered order, give AT MOST ONE chart entry: the entry that most exactly names the test
ordered, matching on what the test is, not on wording. Give none if no entry is that test. Entries
marked [NAMED-ONLY] are therapeutic trials: give one only if that specific trial is named.

Reply with ONLY a JSON object mapping each order number to a list of zero or one chart entry
names, exactly as written above: {"1": ["..."], "2": [], ...}
```

### Investigation-selection controls: three-valued re-answering (THREEVAL=1, optional)

`eval/controls/part2_orders.py`, `MQ3`

```text
A doctor asked a patient these yes/no questions:

%s

The patient record documents these features as PRESENT:

%s

and these features as ABSENT:

%s

The record documents nothing else about this patient.

For each question reply:
- "yes"     if the record explicitly establishes the queried finding is present
- "no"      if the record explicitly establishes the queried finding is absent
- "unknown" if the record does not settle it
A finding that is in neither list is unreported: answer "unknown", never "no".
For a compound question answer "unknown" unless the record settles every part of it.

Reply with ONLY a JSON object: {"<question number>": "yes"|"no"|"unknown", ...}
```

### Stage 1 description without the differential (Own words, retrieval query)

`eval/stage1_description.py`, `P`

```text
A model was shown frames from a video of one patient and asked to describe what it saw
and then name the disease. Its answer is below.

%s

Copy out only the part of the answer that describes what is visible in the video - the body part,
the movement or posture, its timing and side. Leave out every diagnosis, cause, disease name,
syndrome name used as a diagnosis, and any statement of what the patient might have. Keep the
model's own words; do not add, correct or summarise anything. If the answer describes nothing
abnormal, reply NONE.

Reply with the description only.
```

### The model's own differential (Own candidates; head of every retrieval list)

`eval/retrieval/build_union_space.py`, `P`

```text
A model was shown frames from a video of one patient and asked to describe what it saw and
name the disease.

%s

List every distinct diagnosis the answer offers, in the order it presents them. Copy the names it
uses; do not add, rename, or infer any diagnosis it did not state.

Reply with ONLY a JSON array of strings.
```

### Retrieval: optional free-text phrasings of a concept (VARIANTS=1, off by default)

`eval/retrieval/openspace.py`, `VASK`

```text
A clinical author is writing the title of a case report about the sign "%s".

Give 10 lines, nothing else:
- first, 4 ways to write that sign itself, as an author would phrase it
- then 6 named subtypes or named variants of that sign that have their own name in the
  literature.

Use only real published terminology. Do not name any disease or cause.
```

### Retrieval: optional query helper (WIKI=1, off by default)

`eval/retrieval/openspace.py`, `WASK`

```text
Below is the text of an encyclopaedia article about a clinical sign. List every disease,
drug, toxin, deficiency or other cause it names as producing that sign. Four words or fewer each,
one per line, nothing else. Do not add causes the text does not mention.

%s
```

### Chart construction: generic-panel values (derived entries)

`pipeline/fill_generic.py`, `P`

```text
This patient's confirmed diagnosis is:

%s

Their chart already records these findings:

%s

Below is a list of further investigations. For each one, give the result this patient would have.

Rules:
- Answer exactly "normal" unless this diagnosis, or a finding already in the chart, specifically
  makes the test abnormal. Most of these tests are normal in most patients; say so.
- When it is abnormal, give the finding in a few plain words, with a value where a value is
  usual. Do not explain and do not interpret.
- Never contradict the chart above.
- For an examination, describe what the examiner would find, not what they would conclude.

Investigations:
%s

Reply with ONLY a JSON object mapping every investigation, exactly as written above, to its
result: {"<investigation>": "<result>", ...}
```

### Chart construction: generic entries that duplicate a category entry

`pipeline/dedupe_generic.py`, `P`

```text
Below are two lists of investigations from one patient chart.

LIST A (added generically):
%s

LIST B (the chart's own entries):
%s

Find every entry in list A that names the SAME test as some entry in list B - the same specimen
and the same measurement, however differently worded ("serum thiamine (vitamin B1)" and "serum
vitamin B1 (thiamine)" are the same test; "MRI brain with gadolinium" and "brain MRI" are the same
study; "CSF protein" and "lumbar puncture" are NOT, one is a component of the other).

Reply with ONLY a JSON object mapping each duplicated list-A entry to its list-B twin:
{"<list A entry>": "<list B entry>", ...}   Use {} if there are none.
```

### Chart construction: duplicate verification

`pipeline/verify_dupes.py`, `P`

```text
Two entries from a hospital chart:

  A: %s
  B: %s

Is A the same investigation as B - so that a doctor ordering A is ordering exactly B, and reporting
both would report the same result twice?

Answer NO if one is merely a part of the other, or a related but different measurement, or the same
organ system tested a different way.

Reply with ONLY {"same": true} or {"same": false}.
```

### Chart construction: decisive-flag split verification

`pipeline/verify_split.py`, `P`

```text
Two entries from a hospital chart:

  A: %s
  B: %s

Is A the same investigation as B - so that a doctor ordering A is ordering exactly B, and reporting
both would report the same result twice?

Answer NO if one is merely a part of the other, or a related but different measurement, or the same
organ system tested a different way.

Reply with ONLY {"same": true} or {"same": false}.
```

### Temporal-window student: pass-1 window instruction

`window/common.py`, `WINDOW_INSTRUCTION`

```text
These {n} frames are sampled evenly across a silent {duration}-second patient clip; the time
in seconds is stamped on each frame.{shots}

Say which stretch of this clip a viewer should watch more closely to see the abnormality: at most
one window, inside one shot, given by its start time and span in seconds. If these frames already
show it, answer "sufficient"; if no stretch of the recording could show it at this framing,
answer "unobtainable". Do not name a disease, explain, or ask for a crop, zoom or frame rate.

Reply with ONLY one JSON object:
{{"mode": "request", "start": SECONDS, "span": SECONDS}} or {{"mode": "sufficient"}} or {{"mode": "unobtainable"}}
```

### Temporal-window student: pass-2 recognition instruction (Appendix I, verbatim)

`window/common.py`, `RECOGNITION_INSTRUCTION`

```text
These {N} frames are sampled from a silent patient clip. In one sentence,
say what a clinician would see - the abnormality itself, in plain physical
words. Name no disease.
```

### Temporal-window teacher (Appendix I, verbatim)

`window/teacher.py`, `PROMPT`

```text
Above are {n_frames} frames covering the whole {duration}-second clip, in order, with the time
stamped on each. That is {sample_fps} frames per second - {sample_ms} milliseconds pass between one
frame and the next. The recording itself runs at {native_fps} frames per second.{shots_block}

You already know what this clip contains:
  what a clinician sees: {sign}
  what the patient has:  {diagnosis}

That sentence and that diagnosis are given to you and NOT to the person your window is for. Keep
track of which of the two you are using at each step: some of what you know is visible in these
frames, and some of it is not.

Your job is NOT to diagnose. It is to say which seconds of this recording, shown at what frame
rate, would let a viewer who knows nothing about it see the abnormality for themselves.

You choose only WHICH SECONDS and HOW MANY FRAMES PER SECOND. You cannot ask for a crop, a zoom, a
closer view, or any change of framing - the whole frame will be shown as it stands, at the size you
see above. If the thing is too small on screen to read at this framing, no choice of seconds or
rate will fix that, and the honest answer is that it cannot be obtained.

Nothing you ask for will be fetched. You are not being tested on whether you can then see it; you
are being asked to state the best request you can make, and to be explicit about how you arrived
at it.

Work in this order, and let the later steps follow from the earlier ones rather than being chosen
first.

1. What kind of thing is it.
     static_appearance   a feature you could read off a single still - a posture held, a lid
                         position, a pupil, an asymmetry that does not change
     continuous_movement something that goes on throughout, so any long enough stretch contains it
     episodic_event      something that happens at particular moments and not between them
     task_evoked         something that appears only while the patient is doing something, or while
                         being examined

2. Which part of the body, and how large it is on screen. If the part appears more than once in the
   picture - two hands, two eyes, two legs - say which one, by the side of the IMAGE it is on, not
   by the patient's own left and right. Give roughly what fraction of the frame width it occupies,
   and judge honestly whether a change in that part is readable at this size.

3. How long ONE occurrence lasts, in milliseconds - not how often it comes back. These are
   different numbers and only the first sets the frame rate: a movement lasting eighty milliseconds
   that returns every half second needs frames close enough together to catch the eighty, not the
   five hundred. Give both if the thing repeats.

   For a viewer to see an occurrence at all it must fall on at least two frames, so the frames must
   be closer together than HALF its duration:

     required frames per second  =  2000 / (duration of one occurrence in ms)

   Work that number out and compare it with the {sample_fps} frames per second above.

4. Propose at most ONE window: a stretch of seconds and a frame rate, entirely inside ONE shot.
   The windows array must contain zero or one entry, never more than one.

   For the window, say what it rests on:
     read_from_frames        you can point to the stamped frames where it is visible
     stated_in_the_sentence  the sentence you were given already names the moment or the task -
                             "on outstretching the arms", "while walking", "as the patient keeps
                             talking" - and your window follows from those words rather than from
                             anything you saw
     inferred_from_condition neither: you cannot see it here and the sentence does not say when,
                             so you are reasoning about when it is likely to be happening - while
                             the part is being used, while it is being tested, when it is at rest,
                             whatever the condition implies

   All three are legitimate. Answer stated_in_the_sentence whenever it is true, even if the frames
   happen to confirm it; we are counting how often the sentence, rather than the recording, is what
   located the sign.

   Be careful of one trap. A thing fast enough to need a higher rate is, by that very fact, a thing
   these frames are too slow to show, so you cannot expect to watch it happen and point there - and
   the movement that IS plainly visible above is the slow one, which is usually not the thing that
   matters. Do not simply name the seconds where the most conspicuous movement is.

   Give the window a confidence between 0 and 1, meaning how likely you think it is that a viewer
   shown that window, and told nothing, would describe the abnormality correctly.

   Two answers stand outside the window request, and you should give them when they are true:
     survey_sufficient   the frames above already show it; no window is needed
     obtainable = no     no choice of seconds or rate will show it at this framing

   You may still give one optional window when survey_sufficient is yes, but say so in the flag.
   If obtainable is no, return an empty windows array.

Separately, list the stamped times at which the thing can actually be SEEN in the frames above -
the ones you would point to as evidence. If it cannot be made out in any of them, give an empty
list. A run of consecutive frames is not evidence unless each of them shows it.

Your reasons will be read by a human reviewer and never shown to a model being trained. Even so,
write them so that they could be: name the part, the side, the size on screen, the timing, the
direction, and nothing that identifies a condition.

Reply as JSON:
{{"kind": "static_appearance or continuous_movement or episodic_event or task_evoked",
  "body_part": "...",
  "image_side": "left or right or either or not_applicable",
  "size_fraction_of_width": NUMBER between 0 and 1,
  "readable_at_this_size": "yes or no",
  "occurrence_duration_ms": NUMBER or null,
  "repetition_interval_ms": NUMBER or null,
  "required_fps": NUMBER or null,
  "sentence_names_when": "yes or no",
  "survey_sufficient": "yes or no",
  "obtainable": "yes or no",
  "not_obtainable_reason": "too_small or not_in_recording or other or null",
  "windows": [
    {{"shot": SHOT_NUMBER, "at_s": [START_SECONDS, END_SECONDS], "fps": NUMBER,
      "basis": "read_from_frames or stated_in_the_sentence or inferred_from_condition",
      "confidence": NUMBER between 0 and 1,
      "why": "one sentence"}}
  ],
  "evidence_s": [SECONDS, ...],
  "reason": "two or three sentences, following from steps 1 to 3"}}
Nothing else.
```

### Blinded comparison of describers' sentences (Appendix D)

`window/judge_sentences.py`, `P`

```text
A clinician described the visible abnormality in a short patient video as:

REFERENCE: %s

Two other descriptions of the same video:

A: %s
B: %s

For each of A and B, judge each component of the REFERENCE:
- body_part: does it name the same body part?
- laterality: does it name the same side? Use "na" if the REFERENCE states no side.
- movement_character: does it describe the same kind of movement or posture (e.g. jerky,
  flowing, rhythmic, sustained, absent)?
- activation: does it name the same activation condition (at rest, on action, while walking,
  on a task)? Use "na" if the REFERENCE states none.
Then say which description is closer to the REFERENCE overall, or "tie".

Reply with ONLY this JSON:
{"A": {"body_part": "yes|no", "laterality": "yes|no|na", "movement_character": "yes|no",
       "activation": "yes|no|na"},
 "B": {"body_part": "yes|no", "laterality": "yes|no|na", "movement_character": "yes|no",
       "activation": "yes|no|na"},
 "closer": "A|B|tie"}
```
