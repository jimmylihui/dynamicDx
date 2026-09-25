# DynamicDx

**DynamicDx: a process-level benchmark of neurological consultation from patient video.**
Paper: *[link to be added]* · 71 consultations · 11 phenomenological lines · 66 open-access source reports

Each case pairs a short patient video with a case-grounded history, an investigation chart and a
confirmed diagnosis, all taken from the same published case report. A model is evaluated in two
stages: **Stage 1**, describe the sign and name a differential from the frames alone; **Stage 2**,
take a yes/no history, order investigations against the chart, and commit to a diagnosis. Nothing
in the environment is improvised: the patient answers only from the record, the chart returns only
what the source report performed, and an LLM is used solely to *match* free text to record entries,
never to write a finding.

## Repository layout

| path | what it is |
|---|---|
| `data/cases.json` | the 71 cases: source PMCID and licence, confirmed diagnosis, visible sign, Stage 1 lists (`accept_as_coverage`, `related_but_not_covered`) and the final-diagnosis acceptance lists (`final_diagnosis`), documented symptom table with its yes/no/unknown answering rule, investigation chart on the shared menu of the case's disease line: results reported in the source article (`p: reported`) and values expected for the presentation (`p: derived`), with `decisive` flags and `explicit_only` therapeutic trials |
| `data/clips.json` | per clip: source article, licence, duration, frame rate, resolution, scene cuts |
| `data/source_licences.json` | the 66 source articles with title, journal, year and licence |
| `data/equivalent_entries.json` | the 90 verified equivalences between chart entries of the same case that report the same finding from the same kind of investigation, used when scoring τ (§3.3, Appendix C) |
| `data/decidability.json` | the 22 clips the neurologist judged unidentifiable from video alone and the 49 judged identifiable (paper Appendix B) |
| `data/reference_audit.json` | the visual-grounding audit of all 71 reference descriptions: 286 atomic claims, each classed observable / not observable (Appendix B) |
| `pipeline/` | how a case report becomes a case (below) |
| `prompts/PROMPTS.md` | every prompt, verbatim: the model under test, the patient and chart matchers, retrieval, grading |
| `eval/` | the evaluation harness: Stage 1 sweep and judge; Stage 2 batch and multi-round consultations; grader; paired bootstrap; `tau.py` (source-workup coverage τ with equivalent entries); `part2_lie2.py` (corrupted-history stress test, Appendix G) |
| `eval/retrieval/` | literature retrieval and decontamination (§3.5.2, Appendix F; prompts in Appendix H): HPO normalisation, Europe PMC query and cause extraction, the source-PMCID / DOI / near-duplicate / answer-string filters |
| `eval/controls/` | investigation-selection controls (Appendix C.2): ten-item budget, fixed checklist and random arms replayed on the released consultations, and the τ decomposition of Appendix C |
| `eval/analysis/` | `decidability.py`: results by clinician-judged decidability (Appendix B, Tables 8 and 9), read from `data/decidability.json`, the Stage 1 judge output and the Stage 2 grades |
| `scripts/fetch_videos.py` | downloads the source videos from Europe PMC and re-encodes them |

## Videos

The clips are not redistributed: 18 of the 66 source articles are published under CC BY-NC-ND,
which does not permit derivative works. `scripts/fetch_videos.py` fetches each article's
supplementary files and re-encodes the videos as H.264 for local use only (see Licence). Each benchmark clip is an excerpt of under
30 s around the interval in which the sign is expressed; `data/clips.json` records the excerpt's
duration and frame rate and `data/cases.json` the sign it shows. Every clip must be H.264 and
under 30 s before it is used with the harness.

```bash
python scripts/fetch_videos.py            # all 66 articles -> videos_raw/<PMCID>/
python scripts/fetch_videos.py PMC10051035
```

## From case report to case (`pipeline/`)

1. **Dossier** (`build_dossier.py`). For every clip, the source article's full text is pulled from
   Europe PMC and split into the sections a case report uses (presentation, examination,
   investigations, diagnosis, treatment, outcome), keeping every sentence that carries a numeric
   result. Nothing here decides anything; it is the evidence base the case is written from.
2. **Brief** (`brief.py`). A compact per-case summary of what the article records about *this*
   patient, used by the annotator.
3. **Per-line generation** (`genlib.py`, `gen_<line>.py`). Every case of a disease line offers the
   same investigation menu, so which entries hold a result cannot identify the case. Each case
   overrides the entries its own article reports (`p: reported`); the remaining menu entries carry
   a value expected for the presentation (`p: derived`), written by the annotators in the line
   files. A generic panel of commonly ordered tests (`generic_panel.json`) is filled per case by
   `fill_generic.py` (GPT-5.6-luna, given the confirmed diagnosis and the reported chart, answering
   normal unless the diagnosis specifically changes the test; output `generic_values.json`), with
   `dedupe_generic.py` / `verify_dupes.py` removing generic entries that duplicate a line entry
   (`generic_drop.json`). The generator flags the entries that decide the diagnosis as `decisive`,
   gates therapeutic trials behind `explicit_only`, and writes the symptom table and the
   acceptance lists used for grading. The module docstrings record every relabelling made
   against the original clip labels, with the sentence in the source that justified it.
   `verify_split.py` checks pairwise that no two chart entries of a case name the same test.
4. **Assembly** (`assemble.py`). Concatenates the per-line files and checks the invariants: one
   case per video, an identical menu across each line, no investigation key unique to one case of
   its line, therapeutic trials still gated.

Eight visible-sign descriptions were edited after a visual-grounding audit (see the paper's
appendix); `visible_sign_original` keeps the pre-audit text for those cases.

## Running the benchmark

The harness calls models through [OpenRouter](https://openrouter.ai). Put your key in the
environment; it is never written to disk.

```bash
export ORKEY=...            # OpenRouter API key
export DDX_ROOT=$(pwd)      # repository root; clips are expected under dataset/videos/<line>/<video>

# Stage 1: describe the sign from K frames (paper budgets K = 1,2,4,8,16,32,64,128), then grade
MODEL=openai/gpt-5.6-luna PROVIDER=OpenAI OUTROOT=part1_luna python eval/part1_sweep.py 1,2,4,8,16,32,64,128 4
python eval/part1_judge.py luna=part1_luna    # sign, differential and uncapped rank probe (Appendix H)

# Stage 2: batch consultation (video condition: K = 32 ordered frames), then grade
MODEL=openai/gpt-5.6-luna PROVIDER=OpenAI REASONING='{"enabled": true}' KFRAMES=32 \
  OUTROOT=part2_luna_vid python eval/part2_full.py 6
ROOT=part2_luna_vid python eval/part2_full_judge3.py 6

# Multi-round consultation (blocks of questions / orders per round, at most ten rounds)
MODEL=openai/gpt-5.6-luna PROVIDER=OpenAI MAXROUND=10 OUTROOT=part2_luna_seq python eval/part2_seq2.py 6

# Paired case-level bootstrap between two graded runs (10,000 percentile resamples)
python eval/bootstrap_ci.py
```

The seven conditions of the paper's Table 2 (§3.4) are flags of `eval/part2_full.py`; everything
else about the consultation stays fixed. Defaults are the paper's: `ROLE=doctor`, `KFRAMES=32`,
temperature 0, one pinned provider per model.

| condition | flags |
|---|---|
| blind | `NOVIDEO=1` |
| single frame | `KFRAMES=1` |
| shuffled | `SHUFFLE=1 SHUFFLE_SEED=0`, `1`, `2` (three independent per-clip permutations; the paper averages the three runs) |
| video | none |
| own words | `SIGNTEXT=self SELFFILE=<the model's Stage-1 descriptions>` |
| reference | `SIGNTEXT=gt` (the audited clinician description in `data/cases.json`) |
| oracle evidence | `ORACLE=1` |
| retrieval arms (§3.5.2) | `SPACE=union_own UNIONFILE=<candidate file from eval/retrieval/>` |
| multi-turn | `eval/part2_seq2.py` |

Stage 1 uses the paper's prompt by default (`PROMPT=old` in `eval/part1_probe.py`); a structured
JSON variant is kept under `PROMPT=new` but is not what the paper reports.

**Grades.** `eval/part2_full_judge3.py` grades the primary diagnosis against the case's
final-diagnosis acceptance lists (`final_diagnosis`) and returns `accurate` / `partial` / `none`,
the three grades of the paper (Appendix H); accuracy is the `accurate` rate with 71 as denominator
(a case without a usable answer counts as wrong).
Source-workup coverage τ (`eval/tau.py`) is the share of `decisive` chart entries acquired, pooled over the 71 cases; a decisive entry counts as acquired when it or a verified equivalent entry of the same chart (`data/equivalent_entries.json`) is returned, entries are deduplicated within a case, and a case without a usable consultation contributes zero. Every
contrast between conditions is a paired case-level percentile bootstrap with 10,000 resamples.

**The chart.** 6,398 entries over the 71 cases: 426 read from the source article
(`p: reported`) and 5,972 values expected for the presentation on the shared line menu
(`p: derived`; 2,473 from the line files, 3,499 from the generic panel), most of them normal, not
performed or not recorded. 301 entries are `decisive` (256 reported, 45 derived), and every case
keeps at least one decisive entry. All values are fixed before evaluation; the matcher only maps
an order to entry names, and an order the chart does not hold returns
"not performed / not available".

**The patient's answers.** The environment returns `yes` / `no` only for features the record
documents as present / absent and `unknown` otherwise; a feature the record does not mention is never
answered `no`, and a compound question is settled only when the record settles every part
(prompt in `prompts/PROMPTS.md`).

## Results

The harness writes each run under `results/<OUTROOT>/` and the grader writes
`results/stage2_<OUTROOT>.json`; `eval/bootstrap_ci.py` reads two such files for a paired contrast.

## Licence and citation

**Code** (`eval/`, `pipeline/`, `scripts/`): MIT. The pipeline scripts contain the
annotators' own wording (chart values, acceptance lists, relabelling notes) and no sentences copied
from the source articles.

**Annotations** (`data/`) inherit the licence of the article each case was built from, recorded per
case in `source.licence` / `source.annotation_licence` of `data/cases.json` and per article in
`data/source_licences.json`. Every use must attribute the source article by PMCID.

| source licence | articles | cases | terms for the annotations |
|---|---|---|---|
| CC BY 4.0 | 37 | 37 | CC BY 4.0 |
| CC BY-NC 4.0 | 9 | 9 | CC BY-NC 4.0, non-commercial use only |
| CC BY-NC-SA 4.0 | 2 | 2 | CC BY-NC-SA 4.0, non-commercial, share alike |
| CC BY-NC-ND 4.0 | 18 | 23 | research evaluation only; do not redistribute these cases or any adaptation of them |

The clips are never redistributed. `scripts/fetch_videos.py` downloads each article's own
supplementary files for local use; the trimmed and re-encoded excerpts it produces are adaptations
and must not be shared, whatever the source licence, and for the CC BY-NC-ND sources
they may be made only for private research use.

```bibtex
@article{dynamicdx2026,
  title  = {DynamicDx: a process-level benchmark of neurological consultation from patient video},
  author = {[authors]},
  year   = {2026},
  note   = {[venue / link]}
}
```
