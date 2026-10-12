"""Diag round 3: (D) English checkpoint cross-test — is the EN noul head stronger?
(E) topic-matching probe + cheap cosine baseline (title vs body embeddings)."""
import json, pathlib, statistics
import numpy as np
import laya, torch

BASE = pathlib.Path.home() / "laya_poc"
MAX_CHARS = 1800

def load_cases():
    cases = json.loads((BASE / "cases.json").read_text(encoding="utf-8"))
    out = []
    for c in cases:
        kept = [l for l in c["content"].splitlines() if not l.startswith(("name:", "domain:"))]
        body = "\n".join(kept).strip()
        if len(body) > MAX_CHARS:
            body = body[: MAX_CHARS // 2] + "\n...(middle omitted)...\n" + body[-MAX_CHARS // 2 :]
        out.append({**c, "body": body})
    return out

cases = load_cases()
n = len(cases)
SUB = list(range(0, n, 4))
EN_INS = "Does the title describe the same test scenario as the content (precondition/steps/expected result)?"

SYNTH = [
    ("Playlist reorder persists after app restart",
     "precondition: user has a playlist with at least 3 tracks\nsteps: 1. open playlist A  2. long-press the second track and drag it to position 1  3. force-kill the app  4. relaunch\nexpected: the reordered sequence is retained after relaunch"),
    ("Wrong-password lockout message after 5 failed attempts",
     "precondition: account exists, device online\nsteps: 1. open login page  2. enter a wrong password 5 times  3. submit again\nexpected: a lockout toast appears and login is disabled for 5 minutes"),
    ("Search suggestions update while typing pinyin",
     "precondition: app on home screen\nsteps: 1. tap the search box  2. type 'liu'  3. continue typing 'liuxing'\nexpected: suggestion list refreshes per keystroke and contains matches for 'liuxing'"),
    ("Offline download finishes in background",
     "precondition: Wi-Fi connected, album page open\nsteps: 1. tap download on an album  2. leave the page  3. open downloads\nexpected: progress continues in background and status becomes completed"),
    ("Bluetooth speaker reconnects after out-of-range",
     "precondition: speaker already paired\nsteps: 1. walk out of Bluetooth range for 30s  2. walk back in\nexpected: the speaker reconnects automatically within 10s and shows connected"),
    ("EQ preset switch changes sound profile",
     "precondition: playing a track\nsteps: 1. open settings  2. switch EQ from Flat to Bass Boost\nexpected: the EQ indicator shows Bass Boost and audio profile changes without playback interruption"),
    ("Cast session survives screen lock",
     "precondition: TV and phone on same network\nsteps: 1. start casting a song  2. lock the phone screen for 1 minute  3. unlock\nexpected: playback on TV continues and the phone shows the cast controls"),
    ("Lyrics line highlight follows playback position",
     "precondition: track with LRC lyrics is playing\nsteps: 1. open the lyrics page  2. wait for chorus\nexpected: the highlighted lyric line advances in sync with the playback position"),
]

def score(agent, st, ins):
    return agent.predict(st, {"t": {"type": "noul", "instructions": ins}})["answers"]["t"]["noul"]

def pair_stats(agent, fmt_state, ins_true, ins_sham, tag):
    tps, sps = [], []
    for i in SUB:
        c, sham = cases[i], cases[(i + 7) % n]
        tps.append(score(agent, fmt_state(c["title"], c["body"]), ins_true(c["title"])))
        sps.append(score(agent, fmt_state(sham["title"], c["body"]), ins_sham(sham["title"])))
    best_acc, best_thr = 0.0, 0.5
    for thr in [x / 100 for x in range(2, 99, 2)]:
        acc = (sum(p > thr for p in tps) + sum(p <= thr for p in sps)) / (2 * len(SUB))
        if acc > best_acc:
            best_acc, best_thr = acc, thr
    print("%-34s true=%.3f p10=%.3f | sham=%.3f p90=%.3f | bestAcc=%.3f @%.2f" % (
        tag, statistics.mean(tps), statistics.quantiles(tps, n=10)[1],
        statistics.mean(sps), statistics.quantiles(sps, n=10)[8], best_acc, best_thr), flush=True)
    return tag, statistics.mean(tps), statistics.mean(sps), best_acc, best_thr

results = {"probe": {}, "pairs": []}

# ---------- E1: cosine baseline on multilingual (no head, just encoder) ----------
print("=== E1: title-vs-body cosine baseline (mmBERT mean-pool, multilingual ckpt) ===", flush=True)
from transformers import AutoTokenizer, AutoModel
SNAP_ML = str(sorted(pathlib.Path.home().glob(".cache/huggingface/hub/models--convaiinnovations--laya-multilingual/snapshots/*"))[0])
tok = AutoTokenizer.from_pretrained(SNAP_ML + "/tokenizer")
enc = AutoModel.from_pretrained(SNAP_ML + "/encoder")
enc.eval()

@torch.no_grad()
def embed(text):
    ids = tok(text, return_tensors="pt", truncation=True, max_length=512)
    h = enc(**ids).last_hidden_state[0]
    mask = ids["attention_mask"][0].unsqueeze(-1)
    return (h * mask).sum(0) / mask.sum()

def cos(a, b):
    a, b = a / a.norm(), b / b.norm()
    return float((a * b).sum())

ct, cs_ = [], []
for i in SUB:
    c, sham = cases[i], cases[(i + 7) % n]
    ct.append(cos(embed(c["title"]), embed(c["body"])))
    cs_.append(cos(embed(sham["title"]), embed(c["body"])))
ct, cs_ = np.array(ct), np.array(cs_)
best_acc, best_thr = 0.0, 0.0
for thr in np.arange(0.30, 0.90, 0.01):
    acc = ((ct > thr).sum() + (cs_ <= thr).sum()) / (2 * len(SUB))
    if acc > best_acc:
        best_acc, best_thr = acc, thr
print("cosine true mean=%.3f sham mean=%.3f | bestAcc=%.3f @%.2f" % (
    ct.mean(), cs_.mean(), best_acc, best_thr), flush=True)
results["probe"]["cosine"] = {"true_mean": round(float(ct.mean()), 4), "sham_mean": round(float(cs_.mean()), 4),
                              "best_acc": round(float(best_acc), 4), "best_thr": round(float(best_thr), 4)}
del enc
torch.unsqueeze  # no-op keep flake quiet

# ---------- D: English checkpoint ----------
SNAP_EN = sorted(pathlib.Path.home().glob(".cache/huggingface/hub/models--convaiinnovations--laya/snapshots/*"))[0]
cfg = json.loads((SNAP_EN / "rl_agent_config.json").read_text())
print(f"\n=== D: EN checkpoint (shipped max_len={cfg.get('max_len')}) ===", flush=True)
agent = laya.load("convaiinnovations/laya")
agent.cfg["max_len"] = 2048

print("-- sanity trivial:", flush=True)
print("EN trivial TRUE/FALSE : %.3f / %.3f" % (
    score(agent, {"body": "The sky is blue."}, "The text states that the sky is blue."),
    score(agent, {"body": "The sky is blue."}, "The text states that the sky is green.")), flush=True)
print("ZH trivial TRUE/FALSE : %.3f / %.3f" % (
    score(agent, {"body": "天空是蓝色的。"}, "文本说天空是蓝色的。"),
    score(agent, {"body": "天空是蓝色的。"}, "文本说天空是绿色的。")), flush=True)

print("-- real ZH cases, EN instruction:", flush=True)
r = pair_stats(agent,
               lambda t, b: {"body": "Title: " + t + "\n\n" + b},
               lambda t: EN_INS, lambda t: EN_INS, "EN-ckpt ZH-state EN-instr")
results["pairs"].append(r)

print("-- synthetic EN cases (8), EN instruction:", flush=True)
tps = [score(agent, {"body": "Title: " + t + "\n\n" + b}, EN_INS) for t, b in SYNTH]
sps = [score(agent, {"body": "Title: " + SYNTH[(k + 3) % len(SYNTH)][0] + "\n\n" + b}, EN_INS)
       for k, (t, b) in enumerate(SYNTH)]
best_acc, best_thr = 0.0, 0.5
for thr in [x / 100 for x in range(2, 99, 2)]:
    acc = (sum(p > thr for p in tps) + sum(p <= thr for p in sps)) / (2 * len(SYNTH))
    if acc > best_acc:
        best_acc, best_thr = acc, thr
print("synthetic-EN          true=%.3f | sham=%.3f | bestAcc=%.3f @%.2f" % (
    statistics.mean(tps), statistics.mean(sps), best_acc, best_thr), flush=True)
results["pairs"].append(["synthetic-EN", statistics.mean(tps), statistics.mean(sps), best_acc, best_thr])

(BASE / "results_diag3.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
print("DIAG3_DONE", flush=True)
