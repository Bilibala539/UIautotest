# -*- coding: utf-8 -*-
"""POC step2: Laya page-state classification experiment.

Exp A (noul 逐页判断): 每个样本一次调用，内含全部 22 个 noul 问题
    （"当前界面是XX吗"），取得分最高的类作为预测。
Exp B (choice 单问): 每个样本一次调用，单个 choice 问题 + 22 个 criteria，
    取 choice 字段作为预测。

输出: results_noul.csv / results_choice.csv / summary.txt
"""
import csv, json, pathlib, time, urllib.request

from labels import PAGES, LABELS, PAGE_GROUP

HERE = pathlib.Path(__file__).parent
JUDGE_URL = "http://192.168.12.176:8089/predict"
TOKEN = "3f3aeecabda37a7de85393b9113b126b"
MAX_CHARS = 600
RETRY = 3

def judge(state, questions):
    payload = json.dumps({"state": state, "questions": questions}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(JUDGE_URL, data=payload, headers={
        "Content-Type": "application/json", "X-Judge-Token": TOKEN})
    last = None
    for _ in range(RETRY):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(1.0)
    raise RuntimeError(f"judge failed after {RETRY} tries: {last!r}")

def load_dataset():
    ocr = json.loads((HERE / "ocr_texts.json").read_text(encoding="utf-8"))
    data = []
    for rel, label, basis in LABELS:
        if rel not in ocr:
            print("WARN missing ocr:", rel); continue
        text = ocr[rel]["text"].strip()
        if len(text) > MAX_CHARS:
            text = text[: MAX_CHARS // 2] + "\n...(中间省略)...\n" + text[-MAX_CHARS // 2 :]
        data.append({"sample": rel, "label": label, "basis": basis, "text": text})
    return data

def main():
    data = load_dataset()
    n = len(data)
    classes = list(PAGES.keys())
    print(f"samples={n} classes={len(classes)}", flush=True)

    # ---------- Exp A: noul ----------
    q_noul = {c: {"type": "noul",
                  "instructions": f"当前手机界面是{PAGES[c]}吗？"} for c in classes}
    rows_a, t0 = [], time.time()
    for i, d in enumerate(data):
        res = judge({"body": d["text"]}, q_noul)
        ans = res["answers"]
        scores = {c: float(ans[c]["noul"]) for c in classes}
        pred = max(scores, key=scores.get)
        rows_a.append({**{k: d[k] for k in ("sample", "label", "basis")},
                       "pred": pred, "correct": int(pred == d["label"]),
                       "latency_ms": res["meta"]["latency_ms"],
                       **{f"p_{c}": round(scores[c], 4) for c in classes}})
        if (i + 1) % 15 == 0:
            print(f"  noul {i+1}/{n} ({time.time()-t0:.0f}s)", flush=True)
    with open(HERE / "results_noul.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_a[0].keys()))
        w.writeheader(); w.writerows(rows_a)

    # ---------- Exp B: choice ----------
    q_choice = {"page": {"type": "choice",
                         "instructions": "根据这段OCR识别出的界面文字，判断当前手机界面是哪个页面？",
                         "criteria": {c: PAGES[c] for c in classes}}}
    rows_b, t0 = [], time.time()
    for i, d in enumerate(data):
        res = judge({"body": d["text"]}, q_choice)
        a = res["answers"]["page"]
        pred = a["choice"]
        probs = {k: round(float(v), 4) for k, v in a.get("probabilities", {}).items()}
        rows_b.append({**{k: d[k] for k in ("sample", "label", "basis")},
                       "pred": pred, "correct": int(pred == d["label"]),
                       "confidence": round(float(a.get("confidence", 0)), 4),
                       "latency_ms": res["meta"]["latency_ms"],
                       **{f"p_{k}": probs.get(k, 0) for k in classes}})
        if (i + 1) % 15 == 0:
            print(f"  choice {i+1}/{n} ({time.time()-t0:.0f}s)", flush=True)
    with open(HERE / "results_choice.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_b[0].keys()))
        w.writeheader(); w.writerows(rows_b)

    # ---------- summary ----------
    def summarize(rows, name):
        top1 = sum(r["correct"] for r in rows) / len(rows)
        # page-level (tab 归并)
        pg = sum(int(PAGE_GROUP.get(r["pred"], r["pred"]) == PAGE_GROUP.get(r["label"], r["label"]))
                 for r in rows) / len(rows)
        print(f"\n=== {name} ===")
        print(f"top-1 (22类, tab级) = {top1:.1%}   page级(home tabs归并) = {pg:.1%}")
        from collections import Counter
        per = Counter()
        tot = Counter()
        conf = Counter()
        for r in rows:
            tot[r["label"]] += 1
            per[r["label"]] += r["correct"]
            if not r["correct"]:
                conf[(r["label"], r["pred"])] += 1
        print("per-class:")
        for c in sorted(tot):
            print(f"  {c:16s} {per[c]:2d}/{tot[c]:2d}")
        print("top confusion pairs (true -> pred):")
        for (t, p), k in conf.most_common(8):
            print(f"  {t} -> {p}: {k}")
        return top1, pg, conf

    ta, pa, conf_a = summarize(rows_a, "Exp A: noul 逐页判断")
    tb, pb, conf_b = summarize(rows_b, "Exp B: choice 单问")

    # choice calibration (粗评)
    print("\n=== choice 校准粗评 (按 confidence 分桶) ===")
    buckets = [(0, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)]
    for lo, hi in buckets:
        grp = [r for r in rows_b if lo <= r["confidence"] < hi]
        if grp:
            print(f"  conf [{lo:.1f},{hi:.1f}): n={len(grp):2d} acc={sum(r['correct'] for r in grp)/len(grp):.1%}")

    # noul margin 校准
    print("\n=== noul 校准粗评 (按 top1-top2 分差分桶) ===")
    for r in rows_a:
        ps = sorted((r[f"p_{c}"] for c in classes), reverse=True)
        r["margin"] = round(ps[0] - ps[1], 4)
    buckets = [(0, .1), (.1, .3), (.3, .6), (.6, 2)]
    for lo, hi in buckets:
        grp = [r for r in rows_a if lo <= r["margin"] < hi]
        if grp:
            print(f"  margin [{lo:.1f},{hi:.1f}): n={len(grp):2d} acc={sum(r['correct'] for r in grp)/len(grp):.1%}")

    summary = {
        "n_samples": n, "n_classes": len(classes),
        "noul_top1": round(ta, 4), "noul_top1_pagegroup": round(pa, 4),
        "choice_top1": round(tb, 4), "choice_top1_pagegroup": round(pb, 4),
        "noul_confusions": [[t, p, k] for (t, p), k in conf_a.most_common()],
        "choice_confusions": [[t, p, k] for (t, p), k in conf_b.most_common()],
    }
    (HERE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nsaved results_noul.csv / results_choice.csv / summary.json")

if __name__ == "__main__":
    main()
