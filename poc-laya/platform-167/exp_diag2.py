"""Diag round 2: is noul saturation caused by claim format (title hidden in state) or by
long structured test-case text itself? Variants on a 41-case subset, true vs sham pairs."""
import json, pathlib, statistics
import laya

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
SUB = list(range(0, n, 4))  # 41 cases spread over the whole set

def noul(ins):
    return {"t": {"type": "noul", "instructions": ins}}

V0 = lambda title, body: (
    {"body": "标题: " + title + "\n\n" + body},
    "标题与用例内容(前置条件/步骤/预期)描述的是同一个测试场景吗？判断标题与内容的语义一致性。")
V1 = lambda title, body: (
    {"body": body},
    "这段内容的标题是：" + title)
V2 = lambda title, body: (
    {"body": "标题: " + title + "\n\n" + body},
    "标题「" + title + "」与这段内容描述的是同一个测试场景。")

variants = [("V0 baseline(run1)", V0), ("V1 claim-in-instr", V1), ("V2 claim+state-title", V2)]

agent = laya.load("convaiinnovations/laya-multilingual")
agent.cfg["max_len"] = 2048  # same as run 1 (no-op: sequences are <=946 tok)

# probe: can the head say FALSE on a long structured text at all?
long_body = cases[0]["body"]
p_irrelevant_true = agent.predict({"body": long_body}, noul("文本说天空是绿色的。"))["answers"]["t"]["noul"]
p_irrelevant_false_ref = agent.predict({"body": "天空是绿色的。"}, noul("文本说天空是绿色的。"))["answers"]["t"]["noul"]
print(f"PROBE long-structured-body + irrelevant-false-claim: noul={p_irrelevant_true:.3f}  (short-text ref={p_irrelevant_false_ref:.3f})", flush=True)

rows = []
for vname, fmt in variants:
    tps, sps = [], []
    for i in SUB:
        c, sham = cases[i], cases[(i + 7) % n]
        st_t, ins_t = fmt(c["title"], c["body"])
        st_s, ins_s = fmt(sham["title"], c["body"])
        pt = agent.predict(st_t, noul(ins_t))["answers"]["t"]["noul"]
        ps = agent.predict(st_s, noul(ins_s))["answers"]["t"]["noul"]
        tps.append(pt); sps.append(ps)
    best_acc, best_thr = 0.0, 0.5
    for thr in [x / 100 for x in range(2, 99, 2)]:
        acc = (sum(p > thr for p in tps) + sum(p <= thr for p in sps)) / (2 * len(SUB))
        if acc > best_acc:
            best_acc, best_thr = acc, thr
    print("%-22s true mean=%.3f p10=%.3f | sham mean=%.3f p90=%.3f | bestAcc=%.3f @thr=%.2f" % (
        vname, statistics.mean(tps), statistics.quantiles(tps, n=10)[1],
        statistics.mean(sps), statistics.quantiles(sps, n=10)[8], best_acc, best_thr), flush=True)
    rows.append({"variant": vname, "true_mean": round(statistics.mean(tps), 4),
                 "sham_mean": round(statistics.mean(sps), 4), "best_acc": round(best_acc, 4),
                 "best_thr": best_thr, "n": len(SUB)})
    if vname == "V1 claim-in-instr":
        with open(BASE / "results_diag2_v1.csv", "w", encoding="utf-8-sig") as f:
            f.write("case_id,true_p,sham_p\n")
            for k, i in enumerate(SUB):
                f.write(f"{cases[i]['case_id']},{tps[k]:.4f},{sps[k]:.4f}\n")

with open(BASE / "results_diag2.json", "w", encoding="utf-8") as f:
    json.dump({"probe_long_false_claim": p_irrelevant_true, "probe_short_false_claim": p_irrelevant_false_ref,
               "variants": rows}, f, ensure_ascii=False, indent=1)
print("DIAG2_DONE", flush=True)
