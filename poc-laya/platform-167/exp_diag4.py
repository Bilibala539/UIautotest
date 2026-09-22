"""EXP2 deep-dive: rerun 43 domain cases saving full 25-option probabilities."""
import json, pathlib, csv
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
dom_cases = [c for c in cs if c["domain"]]
domains = sorted({c["domain"] for c in dom_cases})
q_dom = {"domain": {"type": "choice", "instructions": "这条测试用例属于哪个功能域？",
                    "criteria": {d: d for d in domains}}}

agent = laya.load("convaiinnovations/laya-multilingual")
agent.cfg["max_len"] = 2048

rows, topk_hits = [], {1: 0, 3: 0, 5: 0}
for c in dom_cases:
    res = agent.predict({"body": "标题: " + c["title"] + "\n\n" + c["body"]}, q_dom)["answers"]["domain"]
    probs = res["probabilities"]
    ranked = sorted(probs.items(), key=lambda kv: -kv[1])
    parts = [p.strip() for p in c["domain"].split("/")]
    for k in topk_hits:
        topk_hits[k] += int(any(r[0] == c["domain"] for r in ranked[:k]))
    rows.append({"case_id": c["case_id"], "true": c["domain"], "pred": res["choice"],
                 "p_pred": probs[res["choice"]], "p_true": probs.get(c["domain"], 0),
                 "rank_of_true": next((i + 1 for i, r in enumerate(ranked) if r[0] == c["domain"]), None),
                 "top2_gap": round(ranked[0][1] - ranked[1][1], 4)})

n = len(dom_cases)
print("top1=%d/%d (%.3f)  top3=%.3f  top5=%.3f" % (
    topk_hits[1], n, topk_hits[1] / n, topk_hits[3] / n, topk_hits[5] / n), flush=True)
pred_counts = {}
for r in rows:
    pred_counts[r["pred"]] = pred_counts.get(r["pred"], 0) + 1
print("pred distribution:", sorted(pred_counts.items(), key=lambda kv: -kv[1]), flush=True)
rank_of_true = [r["rank_of_true"] for r in rows if r["rank_of_true"]]
import statistics
print("rank_of_true mean=%.1f median=%s  never-in-candidates=%d/%d" % (
    statistics.mean(rank_of_true), statistics.median(rank_of_true),
    sum(1 for r in rows if r["rank_of_true"] is None), n), flush=True)

with open(BASE / "results_domain_probs.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print("DIAG4_DONE", flush=True)
