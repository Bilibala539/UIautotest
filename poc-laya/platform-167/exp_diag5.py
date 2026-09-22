"""Diag round 5: close the length confound — EN checkpoint at shipped max_len=512 on real ZH cases."""
import json, pathlib, statistics
import laya

BASE = pathlib.Path.home() / "laya_poc"
MAX_CHARS = 1800

cases = json.loads((BASE / "cases.json").read_text(encoding="utf-8"))
def load():
    out = []
    for c in cases:
        kept = [l for l in c["content"].splitlines() if not l.startswith(("name:", "domain:"))]
        body = "\n".join(kept).strip()
        if len(body) > MAX_CHARS:
            body = body[: MAX_CHARS // 2] + "\n...(middle omitted)...\n" + body[-MAX_CHARS // 2 :]
        out.append({**c, "body": body})
    return out
cs = load()
n = len(cs)
SUB = list(range(0, n, 4))
EN_INS = "Does the title describe the same test scenario as the content (precondition/steps/expected result)?"

agent = laya.load("convaiinnovations/laya")  # shipped max_len=512 stays
print("cfg max_len =", agent.cfg.get("max_len"), flush=True)

def score(st, ins):
    return agent.predict(st, {"t": {"type": "noul", "instructions": ins}})["answers"]["t"]["noul"]

tps, sps = [], []
for i in SUB:
    c, sham = cs[i], cs[(i + 7) % n]
    tps.append(score({"body": "Title: " + c["title"] + "\n\n" + c["body"]}, EN_INS))
    sps.append(score({"body": "Title: " + sham["title"] + "\n\n" + c["body"]}, EN_INS))
best_acc, best_thr = 0.0, 0.5
for thr in [x / 100 for x in range(2, 99, 2)]:
    acc = (sum(p > thr for p in tps) + sum(p <= thr for p in sps)) / (2 * len(SUB))
    if acc > best_acc:
        best_acc, best_thr = acc, thr
print("EN-ckpt @512 ZH-state EN-instr  true=%.3f p10=%.3f | sham=%.3f p90=%.3f | bestAcc=%.3f @%.2f" % (
    statistics.mean(tps), statistics.quantiles(tps, n=10)[1],
    statistics.mean(sps), statistics.quantiles(sps, n=10)[8], best_acc, best_thr), flush=True)
print("DIAG5_DONE", flush=True)
