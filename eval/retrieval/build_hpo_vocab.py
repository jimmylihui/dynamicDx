"""Build a phenomenology vocabulary from HPO instead of hand-writing eleven regexes.

The hand-made table had one entry per disease line, so a description could only ever land in one
of eleven buckets. Anything else - spasticity, tics, athetosis, akathisia, stereotypy,
fasciculation, apraxia - collapsed into "no match", which made "said something specific but wrong"
indistinguishable from "said nothing". HPO gives the full space: every movement, eye-movement and
gait abnormality the field has a term for, with synonyms and an is-a hierarchy, so a wrong answer
can be located rather than discarded.
"""
import os
import json
import re
from collections import defaultdict, deque

HP = json.load(open(os.environ.get("DDX_WORK", "/tmp") + "/hp.json"))["graphs"][0]

# Ptosis sits under "Abnormal eye physiology", not under any nervous-system root - HPO files it
# as an eye phenotype. A vocabulary built only from the neurological roots therefore has no entry
# for one of the eleven disease lines, which is how "ptosis" kept failing to match. Eyelid and
# facial phenotypes have to be pulled in explicitly.
ROOTS = {
    "HP:0100022": "Abnormality of movement",
    "HP:0000496": "Abnormality of eye movement",
    "HP:0001288": "Gait disturbance",
    "HP:0011804": "Abnormal muscle physiology",
    "HP:0012638": "Abnormal nervous system physiology",
    "HP:0012373": "Abnormal eye physiology",
    "HP:0000508": "Ptosis",
    "HP:0010528": "Abnormal eyelid physiology",
    "HP:0010628": "Facial palsy",
    "HP:0000317": "Facial asymmetry",
}
# "Abnormality of the face" was tried as a root to reach Facial palsy and pulled in 1128
# descendants, nearly all craniofacial MORPHOLOGY - the normaliser then matched "Underdeveloped
# supraorbital ridges" to a description of eye movements. Morphology is not a sign here; the
# specific physiological branches are taken instead.

label, syn, parents = {}, defaultdict(set), defaultdict(set)
for n in HP["nodes"]:
    i = n["id"].replace("http://purl.obolibrary.org/obo/HP_", "HP:")
    if not i.startswith("HP:"):
        continue
    m = n.get("meta", {})
    if m.get("deprecated"):
        continue
    if n.get("lbl"):
        label[i] = n["lbl"]
    for s in m.get("synonyms", []):
        if s.get("pred") in ("hasExactSynonym", "hasNarrowSynonym") and s.get("val"):
            syn[i].add(s["val"])

for e in HP["edges"]:
    if e.get("pred") != "is_a":
        continue
    c = e["sub"].replace("http://purl.obolibrary.org/obo/HP_", "HP:")
    p = e["obj"].replace("http://purl.obolibrary.org/obo/HP_", "HP:")
    parents[c].add(p)

children = defaultdict(set)
for c, ps in parents.items():
    for p in ps:
        children[p].add(c)

seen = set()
q = deque(ROOTS)
while q:
    x = q.popleft()
    if x in seen:
        continue
    seen.add(x)
    q.extend(children.get(x, ()))
seen &= set(label)

print("HPO terms under the movement / eye-movement / gait / muscle roots: %d" % len(seen))
for r, name in ROOTS.items():
    sub = set()
    q = deque([r])
    while q:
        x = q.popleft()
        if x in sub:
            continue
        sub.add(x)
        q.extend(children.get(x, ()))
    print("   %-12s %-38s %5d descendants" % (r, name, len(sub & set(label))))


def norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return " ".join(s.split())


vocab = {}
for t in seen:
    names = {label[t]} | syn[t]
    keep = {norm(x) for x in names}
    keep = {x for x in keep if len(x) >= 4 and len(x.split()) <= 6}
    if keep:
        vocab[t] = dict(label=label[t], terms=sorted(keep),
                        parents=sorted(parents.get(t, ())))

json.dump(vocab, open(os.environ.get("DDX_WORK", "/tmp") + "/hpo_vocab.json", "w"), indent=1)
print("\nusable terms (label + exact/narrow synonyms, 5..6 words): %d concepts, %d surface forms"
      % (len(vocab), sum(len(v["terms"]) for v in vocab.values())))

print("\nexamples of concepts the eleven-line table had no bucket for:")
for probe in ("tic", "athetosis", "akathisia", "stereotypy", "spasticity", "fasciculation",
              "apraxia", "hemiballismus", "bradykinesia", "rigidity", "hypomimia",
              "dysdiadochokinesis", "hemifacial spasm", "asterixis", "catalepsy"):
    got = [(t, v["label"]) for t, v in vocab.items() if probe in " ".join(v["terms"])]
    if got:
        print("   %-20s %s" % (probe, ", ".join("%s (%s)" % (l, t) for t, l in got[:3])))
