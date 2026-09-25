"""Fill the generic panel with a per-case expected value.

The generic entries are the tests doctors order unprompted that no case menu carried. They cannot
all be answered "normal": in a Wernicke case serum thiamine is low, in Miller Fisher the CSF shows
albuminocytologic dissociation, in a myasthenia case repetitive nerve stimulation decrements. A
blanket normal would be a false negative handed to the doctor exactly when it matters.

So each value is generated per case from the true diagnosis, with the standing instruction to
answer "normal" unless the diagnosis specifically changes that test. Everything written here is
p="derived" - expected for this presentation, not read off the source article - and is held to the
same standard as the derived entries the line files already carry.

The case's existing investigations are shown to the model so the new entries cannot contradict
what the article actually reported.

usage: fill_generic.py [NTHREADS]   ->  pipeline/generic_values.json
"""
import json
import os
import re
import sys
import threading
import time
import urllib.request

B = os.environ.get("DDX_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORKEY = os.environ["ORKEY"]
MODEL = os.environ.get("MODEL", "openai/gpt-5.6-luna")
PANEL = json.load(open(B + "/pipeline/generic_panel.json"))["entries"]
cases = json.load(open(B + "/data/cases.json"))

P = """This patient's confirmed diagnosis is:

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
result: {"<investigation>": "<result>", ...}"""

out, lock = {}, threading.Lock()
q = list(cases)


def ask(p):
    body = json.dumps({"model": MODEL, "temperature": 0, "max_tokens": 3000,
                       "messages": [{"role": "user", "content": p}],
                       "provider": {"order": ["OpenAI"], "allow_fallbacks": False,
                                    "sort": "price"},
                       "reasoning": {"enabled": False}}).encode()
    for _ in range(5):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": "Bearer " + ORKEY,
                         "Content-Type": "application/json"}), timeout=300).read().decode())
            m = re.search(r"\{.*\}", r["choices"][0]["message"]["content"] or "", re.S)
            if m:
                return json.loads(m.group(0))
        except Exception:                                          # noqa: BLE001
            time.sleep(5)
    return None


def work():
    while True:
        with lock:
            if not q:
                return
            c = q.pop()
        chart = "\n".join("- %s: %s" % (k, v["v"]) for k, v in c["investigations"].items()
                          if v.get("p") == "reported")
        r = ask(P % (c["true_diagnosis"], chart or "- (nothing recorded)",
                     "\n".join("- " + k for k in PANEL)))
        with lock:
            out[c["video"]] = r
            n_abn = sum(1 for v in (r or {}).values()
                        if v.strip().lower() not in ("normal", "normal.")) if r else -1
            print("%-52s %s  abnormal=%s" % (c["video"][:52],
                                             "%d/%d" % (len(r or {}), len(PANEL)), n_abn),
                  flush=True)


ts = [threading.Thread(target=work) for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6)]
[t.start() for t in ts]
[t.join() for t in ts]

bad = [v for v, r in out.items() if not r or len(r) < len(PANEL) * 0.9]
print("\n%d cases filled, %d incomplete: %s" % (len(out), len(bad), bad[:5]))
json.dump(out, open(B + "/pipeline/generic_values.json", "w"), indent=1, ensure_ascii=False)
