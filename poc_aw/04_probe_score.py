# -*- coding: utf-8 -*-
"""Probe: does the 'score' question type discriminate pages at all?
Also: substring baseline ceiling with auto-extracted discriminative attributes.
"""
import json, pathlib, time, urllib.request
from collections import Counter, defaultdict

from labels import LABELS

HERE = pathlib.Path(__file__).parent
JUDGE_URL = "http://192.168.12.176:8089/predict"
TOKEN = "3f3aeecabda37a7de85393b9113b126b"

def judge(state, questions):
    payload = json.dumps({"state": state, "questions": questions}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(JUDGE_URL, data=payload, headers={
        "Content-Type": "application/json", "X-Judge-Token": TOKEN})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            time.sleep(1.0)
    raise RuntimeError("judge failed")

ocr = json.loads((HERE / "ocr_texts.json").read_text(encoding="utf-8"))
data = [{"sample": rel, "label": lab, "text": ocr[rel]["text"].strip()} for rel, lab, _ in LABELS]

# ---------- 1) score head probe: 4 classes x 8 samples ----------
K4 = ["home_recommend", "me", "device", "login"]
def pick(data, cls, n=8):
    out, seen = [], set()
    for d in data:
        if d["label"] == cls and d["sample"] not in seen:
            out.append(d); seen.add(d["sample"])
        if len(out) >= n: break
    return out
probe = sum((pick(data, c) for c in K4), [])
print(f"score-head probe: {len(probe)} samples x 4 statements")
q = {f"s_{c}": {"type": "score", "instructions": f"这段界面文字来自{c}页面。请打分。"} for c in K4}
ok = fail = 0
for d in probe:
    try:
        res = judge({"body": d["text"]}, q)
        sc = {c: res["answers"][f"s_{c}"] for c in K4}
        print(" ", d["label"], "->", json.dumps(sc, ensure_ascii=False)[:200])
        ok += 1
    except Exception as e:
        print(" ", d["label"], "score FAILED:", repr(e)[:120]); fail += 1
print(f"score probe: ok={ok} fail={fail}")

# ---------- 2) substring ceiling with auto-extracted attributes ----------
# 取每类 1-gram/2-gram 词片，按"类内命中率×他类不出现"挑 top3（留一法防泄漏：从同类一半样本提取，另一半验证）
def grams(text, lo=2, hi=6):
    s = text.replace("\n", "").replace(" ", "")
    out = set()
    for n in range(lo, hi + 1):
        for i in range(len(s) - n + 1):
            out.add(s[i:i + n])
    return out

by = defaultdict(list)
for d in data:
    by[d["label"]].append(d)

correct = 0
detail = []
for cls, items in sorted(by.items()):
    half = items[: len(items) // 2 + 1]     # 提取半
    val = items[len(items) // 2 + 1:] or items[:1]  # 验证半
    cand = Counter()
    for it in half:
        cand |= Counter(grams(it["text"]))
    # 过滤：在提取半中命中率≥0.9，在其他类全部样本中不出现
    cands = []
    for g, _ in cand.most_common(4000):
        hit = sum(1 for it in half if g in it["text"].replace("\n", "").replace(" ", ""))
        if hit / len(half) < 0.9:
            continue
        cross = sum(1 for it in data if it["label"] != cls and g in it["text"].replace("\n", "").replace(" ", ""))
        if cross == 0:
            cands.append((g, len(g)))
        if len(cands) >= 5:
            break
    attrs = [g for g, _ in cands[:3]]
    v_ok = sum(1 for it in val if any(a in it["text"].replace("\n", "").replace(" ", "") for a in attrs))
    detail.append((cls, attrs, f"{v_ok}/{len(val)}"))
    print(f"  {cls:16s} attrs={attrs} val={v_ok}/{len(val)}")

hit = sum(int(d['label'] == cls) for cls, attrs, _ in detail for d in by[cls] if any(a in d['text'].replace('\n','').replace(' ','') for a in attrs))
print(f"substring(auto-attr, oracle-half extraction) full-set hit = {hit}/{len(data)} = {hit/len(data):.1%}")
