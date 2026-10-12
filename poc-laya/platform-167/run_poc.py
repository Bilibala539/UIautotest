"""Laya POC: is Laya's judgment on text cases reliable? 3 experiments on Swan platform cases.
Exp1 title-content consistency (noul, true vs shuffled pairs)
Exp2 domain classification (choice, 43 cases with domain label)
Exp3 verifiability (noul, exported for manual review)
"""
import csv, json, pathlib, random, statistics, time

import laya

BASE = pathlib.Path.home() / "laya_poc"
SEED = 20260922
MAX_CHARS = 1800

def load_cases():
    cases = json.loads((BASE / "cases.json").read_text(encoding="utf-8"))
    out = []
    for c in cases:
        kept = []
        for ln in c["content"].splitlines():
            if ln.startswith(("name:", "domain:")):
                continue  # name duplicates title (cheat channel); domain is exp2's answer
            kept.append(ln)
        body = "\n".join(kept).strip()
        if len(body) > MAX_CHARS:
            body = body[: MAX_CHARS // 2] + "\n...(middle omitted)...\n" + body[-MAX_CHARS // 2 :]
        out.append({**c, "body": body})
    return out

def state_of(case):
    return {"body": "标题: " + case["title"] + "\n\n" + case["body"]}

Q_PAIR = {
    "consistent": {
        "type": "noul",
        "instructions": "标题与用例内容(前置条件/步骤/预期)描述的是同一个测试场景吗？判断标题与内容的语义一致性。",
    },
    "verifiable": {
        "type": "noul",
        "instructions": "这条测试用例是否有明确可观察的预期结果，能直接作为通过/失败判据？",
    },
}

def run():
    cases = load_cases()
    n = len(cases)
    print(f"cases={n}", flush=True)
    t0 = time.time()
    try:
        agent = laya.load("convaiinnovations/laya-multilingual")
    except Exception as e:
        print("direct load failed:", repr(e), "-> retry as subfolder", flush=True)
        agent = laya.load("convaiinnovations/laya", subfolder="multilingual")
    agent.cfg["max_len"] = 2048
    print(f"model loaded in {time.time()-t0:.0f}s", flush=True)

    # ---- exp1 + exp3: consistency (true/sham) + verifiability ----
    sham = [cases[(i + 7) % n] for i in range(n)]
    rows, t0 = [], time.time()
    for i, c in enumerate(cases):
        ans_t = agent.predict(state_of(c), Q_PAIR)["answers"]
        sham_case = {**c, "title": sham[i]["title"]}
        ans_s = agent.predict(state_of(sham_case), Q_PAIR)["answers"]
        rows.append({
            "case_id": c["case_id"],
            "title": c["title"],
            "p_consistent_true": round(ans_t["consistent"]["noul"], 4),
            "p_consistent_sham": round(ans_s["consistent"]["noul"], 4),
            "p_verifiable": round(ans_t["verifiable"]["noul"], 4),
        })
        if (i + 1) % 20 == 0:
            print(f"  exp1/3 progress {i+1}/{n} ({time.time()-t0:.0f}s)", flush=True)

    true_p = [r["p_consistent_true"] for r in rows]
    sham_p = [r["p_consistent_sham"] for r in rows]
    ver_p = [r["p_verifiable"] for r in rows]

    def stats(v):
        q = statistics.quantiles(v, n=100)
        return f"mean={statistics.mean(v):.3f} p10={q[9]:.3f} p50={q[49]:.3f} p90={q[89]:.3f}"

    best_acc, best_thr = 0.0, 0.5
    for thr in [x / 100 for x in range(5, 100, 5)]:
        acc = (sum(p > thr for p in true_p) + sum(p <= thr for p in sham_p)) / (2 * n)
        if acc > best_acc:
            best_acc, best_thr = acc, thr

    print("\n=== EXP1 标题-内容一致性 (noul) ===", flush=True)
    print("真配对: " + stats(true_p))
    print("假配对: " + stats(sham_p))
    print(f"最佳阈值={best_thr:.2f}  区分准确率={best_acc:.3f}")

    print("\n=== EXP3 可验证性 (noul, 待人工抽查) ===")
    print(f"mean={statistics.mean(ver_p):.3f}  打分<0.5 的条数={sum(p < 0.5 for p in ver_p)}")

    with open(BASE / "results_consistency.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- exp2: domain classification ----
    dom_cases = [c for c in cases if c["domain"]]
    domains = sorted({c["domain"] for c in dom_cases})
    print(f"\n=== EXP2 domain 归类 (choice) === cases={len(dom_cases)} labels={len(domains)}", flush=True)
    q_dom = {"domain": {"type": "choice",
                        "instructions": "这条测试用例属于哪个功能域？",
                        "criteria": {d: d for d in domains}}}
    dom_rows, t0 = [], time.time()
    for c in dom_cases:
        res = agent.predict(state_of(c), q_dom)["answers"]["domain"]
        pred = res["choice"]
        parts = [p.strip() for p in c["domain"].split("/")]
        dom_rows.append({"case_id": c["case_id"], "true": c["domain"], "pred": pred,
                         "confidence": round(res.get("confidence", 0), 4),
                         "exact": int(pred == c["domain"]),
                         "lenient": int(any(pred == p for p in parts))})
        if len(dom_rows) % 10 == 0:
            print(f"  exp2 progress {len(dom_rows)}/{len(dom_cases)} ({time.time()-t0:.0f}s)", flush=True)

    exact = sum(r["exact"] for r in dom_rows) / len(dom_rows)
    lenient = sum(r["lenient"] for r in dom_rows) / len(dom_rows)
    print(f"严格命中={exact:.3f}  宽松命中(复合域部分匹配)={lenient:.3f}")
    with open(BASE / "results_domain.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(dom_rows[0].keys()))
        w.writeheader()
        w.writerows(dom_rows)

    meta = {"model": "convaiinnovations/laya-multilingual", "seed": SEED,
            "cases": n, "finished": time.strftime("%Y-%m-%d %H:%M:%S")}
    (BASE / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nDONE", flush=True)

if __name__ == "__main__":
    run()
