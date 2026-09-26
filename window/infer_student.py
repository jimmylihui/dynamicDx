"""Out-of-fold two-pass inference for the temporal-window arms (paper Sections 3.5.1 and 4.3).

  ARM=window     pass 1 predicts the window; pass 2 describes K frames from it
  ARM=random     same adapter, survey, window duration and K, position drawn at random (seeded
                 per clip); fallbacks are identical to the Window arm
  ARM=sign_only  the sign-only adapter on 32+K frames spread evenly over the clip, one pass
  ARM=untrained  unadapted Qwen3.5-4B on the same survey-plus-window input as the window-trained
                 adapter (the adapter's pass-1 replies are read from WINDOWS_FROM)

Every clip is described by the adapter of the fold that held it out. Pass 1 decodes greedily with at
most 1100 new tokens, pass 2 with at most 64. A response without a valid window falls back to the
survey without presenting it again. Neither pass receives the reference sentence, the diagnosis or
any other clinical field.

The output {video: sentence} initialises the GPT-5.6-luna consultations:
    SIGNTEXT=self SELFFILE=<out> MODEL=openai/gpt-5.6-luna python eval/part2_full.py

usage: python window/infer_student.py ARM K [OUT_JSON]
env:   WINDOWS_FROM (ARM=untrained: output of ARM=window at the same K)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as W                                                    # noqa: E402
import student as S                                                   # noqa: E402

ARM, K = sys.argv[1], int(sys.argv[2])
assert ARM in ("window", "random", "sign_only", "untrained") and K in W.BUDGETS
OUT = sys.argv[3] if len(sys.argv) > 3 else "%s/results/window/describe_%s_k%d.json" % (W.B, ARM, K)
W.ensure_clips()
fold = W.folds()
prev = json.load(open(os.environ["WINDOWS_FROM"])) if ARM == "untrained" else {}
out = {}

for f in range(5):
    held = [v for v in W.all_videos() if fold[v] == f]
    adapter = None if ARM == "untrained" else "%s/results/window/adapters/%s_k%d_fold%d" % (
        W.B, "sign_only" if ARM == "sign_only" else "window", K, f)
    proc, model = S.load(adapter=adapter)
    for v in held:
        if ARM == "sign_only":
            fr = W.spread_frames(v, W.N_SURVEY + K)
            m = [S.user(fr, W.RECOGNITION_INSTRUCTION.format(N=len(fr)))]
            out[v] = dict(sentence=S.generate(proc, model, m, fr, 64), n_frames=len(fr))
            continue
        surv = W.survey(v)
        m1 = [S.user(surv, W.window_prompt(v))]
        reply = prev[v]["pass1"] if ARM == "untrained" else S.generate(proc, model, m1, surv, 1100)
        w = W.parse_window(reply, v)
        used = w
        if ARM == "random" and w and w[0] == "request":
            used = W.random_window(v, w[2])
        turn, extra = S.pass2_turn(v, used, K, surv)
        m2 = m1 + [S.assistant(reply if used == w else W.target_text(used)), turn]
        sent = S.generate(proc, model, m2, surv + extra, 64)
        out[v] = dict(sentence=sent, pass1=reply, window=list(used) if used else None,
                      fallback=not (used and used[0] == "request"), n_frames=len(extra) or len(surv))
    del model
    import torch
    torch.cuda.empty_cache()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
json.dump({v: r["sentence"] for v, r in out.items()},
          open(OUT.replace(".json", "_selffile.json"), "w"), indent=1, ensure_ascii=False)
n_win = sum(1 for r in out.values() if r.get("window") and r["window"][0] == "request")
print("%s K=%d: %d clips described, %d with a valid window -> %s" % (ARM, K, len(out), n_win, OUT))
