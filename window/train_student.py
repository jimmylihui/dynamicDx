"""Train the student adapters (paper Section 3.5.1; Appendix I, "Training schedule and parameters").

Window adapter (ARM=window): L = 0.3 L_win + 0.7 L_phen, both mean token cross-entropies on the
target text only. Epoch 1 is teacher-forced: recognition uses the teacher's window. In epoch 2 the
probability of using the student's own pass-1 prediction instead rises linearly from 0 to 0.5.
No-window answers and invalid JSON fall back to the survey, as at inference.

Sign-only adapter (ARM=sign_only): the same clips, folds, target sentence and prompt, one epoch per
fold, recognition loss only, on 32+K frames spread evenly over the whole clip; no window enters
training or inference.

Five folds grouped by source article (window/common.py:folds); each adapter is trained on four folds
and later evaluated on the held-out one. Only clips with a usable teacher record are trained on.

usage: python window/train_student.py ARM K FOLD [TEACHER_JSON]
       ARM in {window, sign_only}, K in {8, 16, 32}, FOLD in {0..4}
out:   results/window/adapters/<ARM>_k<K>_fold<FOLD>/
"""
import os
import random
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as W                                                    # noqa: E402
import student as S                                                   # noqa: E402

ARM, K, FOLD = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
TEACHER = sys.argv[4] if len(sys.argv) > 4 else W.B + "/results/window/teacher.json"
assert ARM in ("window", "sign_only") and K in W.BUDGETS and 0 <= FOLD < 5
LAMBDA = 0.3
LR, ACCUM, CLIP = 1e-4, 4, 1.0
EPOCHS = 2 if ARM == "window" else 1
OUT = "%s/results/window/adapters/%s_k%d_fold%d" % (W.B, ARM, K, FOLD)

torch.manual_seed(0)
random.seed(0)
W.ensure_clips()
targets = W.load_targets(TEACHER)
fold = W.folds()
train = sorted(v for v in targets if fold[v] != FOLD)
print("%s K=%d fold %d: %d training clips" % (ARM, K, FOLD, len(train)))

proc, model = S.load(train=True)
opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=LR, weight_decay=0.0)
steps = EPOCHS * ((len(train) + ACCUM - 1) // ACCUM)
sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=LR, total_steps=steps, pct_start=0.1)
cache = {}


def inputs(v):
    if v not in cache:
        cache[v] = W.survey(v) if ARM == "window" else W.spread_frames(v, W.N_SURVEY + K)
    return cache[v]


def loss_window(v, sampled_prob):
    surv = inputs(v)
    m1 = [S.user(surv, W.window_prompt(v))]
    tw = targets[v]
    l_win = model(**S.encode(proc, m1, surv, W.target_text(tw))).loss
    w = tw
    if sampled_prob > 0 and random.random() < sampled_prob:      # scheduled sampling
        model.eval()
        w = W.parse_window(S.generate(proc, model, m1, surv, 1100), v)
        model.train()
    turn, extra = S.pass2_turn(v, w, K, surv)
    m2 = m1 + [S.assistant(W.target_text(tw) if w == tw else S.window_text(w)), turn]
    l_phen = model(**S.encode(proc, m2, surv + extra, W.reference_sign(v))).loss
    return LAMBDA * l_win + (1 - LAMBDA) * l_phen


def loss_sign_only(v):
    fr = inputs(v)
    m = [S.user(fr, W.RECOGNITION_INSTRUCTION.format(N=len(fr)))]
    return model(**S.encode(proc, m, fr, W.reference_sign(v))).loss


model.train()
step = 0
per_epoch = len(train)
for ep in range(EPOCHS):
    order = list(train)
    random.Random("%s|%d|%d|%d" % (ARM, K, FOLD, ep)).shuffle(order)
    for i, v in enumerate(order):
        p = 0.5 * i / max(per_epoch - 1, 1) if (ARM == "window" and ep == 1) else 0.0
        loss = loss_window(v, p) if ARM == "window" else loss_sign_only(v)
        (loss / ACCUM).backward()
        if (i + 1) % ACCUM == 0 or i + 1 == len(order):
            torch.nn.utils.clip_grad_norm_([q for q in model.parameters() if q.requires_grad], CLIP)
            opt.step()
            sched.step()
            opt.zero_grad()
            step += 1
        if i % 10 == 0:
            print("epoch %d  %3d/%d  loss %.4f  p_student %.2f" % (ep + 1, i, len(order), loss.item(), p),
                  flush=True)

os.makedirs(OUT, exist_ok=True)
model.save_pretrained(OUT)
print("saved %s (%d optimiser steps)" % (OUT, step))
