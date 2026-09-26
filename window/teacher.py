"""Offline teacher: one window label per clip (paper Section 3.5.1; Appendix I, "Teacher").

GPT-5.6-luna sees the 32-frame timestamped survey (images first, then text), the verbatim reference
phenomenology sentence and the confirmed diagnosis, and returns at most one window or a no-window
decision. It runs once per clip (temperature 0, top-p 0.9, at most 1100 output tokens), before the
five-fold split. Only the parsed target is used for training; the student never sees the teacher's
reasoning, the sentence or the diagnosis as input.

Target rules: the last JSON object of the reply is parsed; survey_sufficient=yes gives a
`sufficient` target (any optional window is ignored), obtainable=no gives `unobtainable`,
contradictory flags are invalid, and otherwise the first window becomes a request with its start and
span (end minus start) in seconds. Frame rates, shots, confidence and explanations are dropped.

usage: python window/teacher.py [OUT_JSON]        (default results/window/teacher.json)
env:   ORKEY, TEACHER (default openai/gpt-5.6-luna), TEACHER_PROVIDER (default OpenAI)
"""
import base64
import io
import json
import os
import sys
import threading
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as W                                                    # noqa: E402

ORKEY = os.environ["ORKEY"]
TEACHER = os.environ.get("TEACHER", "openai/gpt-5.6-luna")
PROV = os.environ.get("TEACHER_PROVIDER", "OpenAI")
OUT = sys.argv[1] if len(sys.argv) > 1 else W.B + "/results/window/teacher.json"

# the versioned template of Appendix I, verbatim; doubled braces are literal braces
PROMPT = """Above are {n_frames} frames covering the whole {duration}-second clip, in order, with the time
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
Nothing else."""


def teacher_prompt(video):
    d = W.duration(video)
    rate = W.N_SURVEY / d
    sb = W.shots_block(video)
    return PROMPT.format(n_frames=W.N_SURVEY, duration="%.1f" % d, sample_fps="%.2f" % rate,
                         sample_ms="%.0f" % (1000.0 / rate), native_fps="%g" % W.native_fps(video),
                         shots_block=(" " + sb.strip()) if sb else "",
                         sign=W.reference_sign(video), diagnosis=W.CASES[video]["true_diagnosis"])


def b64(im):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def call(video):
    frames = W.survey(video)
    content = ([{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64(f)}}
                for f in frames] + [{"type": "text", "text": teacher_prompt(video)}])
    body = json.dumps({"model": TEACHER, "temperature": 0, "top_p": 0.9, "max_tokens": 1100,
                       "messages": [{"role": "user", "content": content}],
                       **({"provider": {"order": [PROV], "allow_fallbacks": False}} if PROV else {})}).encode()
    for _ in range(5):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY, "Content-Type": "application/json"}),
                timeout=300).read().decode())
            return r["choices"][0]["message"]["content"] or ""
        except Exception:                                              # noqa: BLE001
            time.sleep(5)
    return ""


def to_target(reply, video):
    j = W.last_json(reply)
    if not isinstance(j, dict):
        return None
    suff = str(j.get("survey_sufficient", "")).lower() == "yes"
    unob = str(j.get("obtainable", "")).lower() == "no"
    if suff and unob:                                   # contradictory flags: invalid
        return None
    if suff:
        return {"mode": "sufficient"}
    if unob:
        return {"mode": "unobtainable"}
    ws = j.get("windows") or []
    if len(ws) != 1:
        return None
    try:
        a, b = (float(x) for x in ws[0]["at_s"])
    except (KeyError, TypeError, ValueError):
        return None
    w = W.parse_window(json.dumps({"mode": "request", "start": a, "span": b - a}), video)
    return {"mode": "request", "start": round(w[1], 2), "span": round(w[2], 2)} if w else None


if __name__ == "__main__":
    W.ensure_clips()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [v for v in W.all_videos() if v not in out]
    lock = threading.Lock()

    def work():
        while True:
            with lock:
                if not todo:
                    return
                v = todo.pop()
            rep = call(v)
            with lock:
                out[v] = dict(reply=rep, target=to_target(rep, v))
                json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)

    ts = [threading.Thread(target=work) for _ in range(4)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    ok = [r["target"] for r in out.values() if r.get("target")]
    print("usable records %d/%d: request %d, sufficient %d, unobtainable %d" % (
        len(ok), len(out), sum(t["mode"] == "request" for t in ok),
        sum(t["mode"] == "sufficient" for t in ok), sum(t["mode"] == "unobtainable" for t in ok)))
