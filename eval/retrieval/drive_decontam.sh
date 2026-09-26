#!/bin/sh
# Retrieval decontamination: one search per case, cached, then the same corpus filtered three ways.
#   orig    Original: every record kept
#   clean   Source-clean: source PMCID, shared DOI, near-duplicate title removed  -> primary condition
#   strict  Strict no-answer: clean plus any record naming the confirmed diagnosis or an equivalent
# Queries are built from the model's predicted sign (paper, Section 3.5.2):
#   usage: drive_decontam.sh STAGE1_ROOT      e.g. part1_oldp_luna (its ans_hpo file must exist)
# "oracle" instead queries from the clinician's reference sign (a diagnostic, not a paper condition).
# The Source-clean records are also written to $W/retained_<ROOT>/ and audited for same-patient
# reports (same_patient_audit.py).
Q=${1:?usage: drive_decontam.sh STAGE1_ROOT}
cd "${DDX_ROOT:-$(dirname "$0")/../..}" || exit 1
PY=${PY:-python3}
: "${ORKEY:?set ORKEY to your OpenRouter key}"
W=${DDX_WORK:-/tmp}
export RECDIR=${RECDIR:-$W/epmc_records}
mkdir -p "$W" results

for C in orig clean strict; do
  R=""; [ "$C" = clean ] && R=$W/retained_$Q
  CLEAN=$C RETAINDIR=$R OUTFILE=$W/openspace_${Q}_$C.json $PY eval/retrieval/openspace.py "$Q" \
      > results/decon_$C.log 2>&1 || { echo "$C failed"; tail -5 results/decon_$C.log; exit 1; }
  echo "[$(date +%H:%M)] CLEAN=$C done  (raw records cached for $(ls $RECDIR | wc -l) cases)"
done

W="$W" Q="$Q" $PY - <<'PY'
import json, collections, os
import numpy as np
D = {c: json.load(open(os.environ['W'] + '/openspace_%s_%s.json' % (os.environ['Q'], c))) for c in ('orig','clean','strict')}
rules = ['source_pmcid','shared_doi','near_duplicate','answer_string']
print('\n%-22s %10s %14s' % ('filter rule','records removed','cases affected'))
tot = collections.Counter(); aff = collections.Counter()
for v, x in D['strict'].items():
    for r in rules:
        n = x['removed'][r]
        tot[r] += n
        if n: aff[r] += 1
for r in rules:
    print('%-22s %10d %10d/%d' % (r, tot[r], aff[r], len(D['strict'])))
print('\n%-8s %12s %12s' % ('condition','mean corpus','mean causes'))
for c in ('orig','clean','strict'):
    print('%-8s %12.0f %12.0f' % (c,
        np.mean([x['n_papers'] for x in D[c].values()]),
        np.mean([len(x['causes']) for x in D[c].values()])))
PY

$PY eval/retrieval/same_patient_audit.py "$W/retained_$Q" "results/same_patient_audit_$Q.json"
