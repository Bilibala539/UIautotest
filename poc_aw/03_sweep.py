# -*- coding: utf-8 -*-
"""POC step3: prompting sweep on a per-class subset.

变体:
  A choice22_short : 22类 choice, 短 criteria（旧POC: 长候选塌缩 → 验证）
  B choice6_short  : 6类 choice, 短 criteria（旧POC建议 k≤5 强区分）
  C noul_attr      : 属性级 noul（旧POC保留场景"短文本属性级noul断言"）
  D noul_short     : 短问句页面级 noul（排除"长描述导致饱和"假设）
  E choice6_prefix : B + body 加 OCR 上下文前缀
  S substring      : 纯子串匹配基线（C 的对照，零模型成本）
"""
import csv, json, pathlib, time, urllib.request
from collections import Counter

from labels import PAGES, LABELS, PAGE_GROUP

HERE = pathlib.Path(__file__).parent
JUDGE_URL = "http://192.168.12.176:8089/predict"
TOKEN = "3f3aeecabda37a7de85393b9113b126b"

SHORT = {
    "home_recommend": "首页推荐页", "home_music": "首页音乐页", "home_radio": "首页电台页",
    "home_vision": "首页可视音箱页", "home_ai": "首页AI对话页", "me": "我的页面",
    "device": "设备页", "platform": "平台页", "player": "全屏播放页",
    "playlist_page": "歌单库页", "playlist_detail": "歌单详情页", "collection": "SWAN收藏页",
    "history": "播放历史页", "sheet_device": "设备切换弹层", "volume_popup": "音量弹层",
    "login": "登录页", "auth_dialog": "授权通知弹层", "ai_role_settings": "AI角色设置页",
    "person_info": "个人信息修改页", "avatar_popup": "基本信息修改弹窗",
    "profile_edit": "修改昵称页", "area_code": "区号选择页",
}
# 属性级特征：该页面上应稳定出现、且尽量少出现在别处的 OCR 文本片段
ATTR = {
    "home_recommend": ["我喜欢", "最近播放"],
    "home_music": ["QQ音乐", "网易云音乐"],
    "home_radio": ["全国电台", "交通广播"],
    "home_vision": ["视觉窗口", "手电筒"],
    "home_ai": ["开场白", "历史对话记录"],
    "me": ["我的权益", "充值与消费记录"],
    "device": ["音源选择", "同步设备"],
    "platform": ["充值明细", "数字资产"],
    "player": ["00:00"],
    "playlist_page": ["已加载全部", "聚合"],
    "playlist_detail": ["收藏全部", "快去添加"],
    "collection": ["SWAN收藏", "添加新的收藏歌单"],
    "history": ["播放历史"],
    "sheet_device": ["切换设备", "手机蓝牙"],
    "volume_popup": ["Speaker"],
    "login": ["验证码登录", "下一步"],
    "auth_dialog": ["授权通知", "更多平台"],
    "ai_role_settings": ["所有角色"],
    "person_info": ["个人信息修改", "注销账号"],
    "avatar_popup": ["基本信息修改"],
    "profile_edit": ["修改昵称"],
    "area_code": ["选择国家地区"],
}
CLASSES = list(SHORT.keys())
K6 = ["home_recommend", "me", "device", "platform", "player", "login"]

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

def load_dataset():
    ocr = json.loads((HERE / "ocr_texts.json").read_text(encoding="utf-8"))
    data = []
    for rel, label, basis in LABELS:
        text = ocr[rel]["text"].strip()
        data.append({"sample": rel, "label": label, "text": text})
    return data

def pick_subset(data, per_class=2):
    by = {}
    for d in data:
        by.setdefault(d["label"], []).append(d)
    sub = []
    for c, items in sorted(by.items()):
        # 同类里取 OCR 文本来源目录不同的前2个
        seen_dirs = set()
        cnt = 0
        for it in items:
            d = it["sample"].split("/")[0] + ("/" + it["sample"].split("/")[1] if it["sample"].count("/") > 1 else "")
            if d in seen_dirs and cnt:
                continue
            seen_dirs.add(d)
            sub.append(it); cnt += 1
            if cnt >= per_class:
                break
    return sub

def acc(rows):
    return sum(r["correct"] for r in rows) / len(rows) if rows else 0.0

def main():
    data = load_dataset()
    sub = pick_subset(data)
    print(f"subset={len(sub)} of {len(data)}", flush=True)

    rows = {k: [] for k in "ABCDES"}
    q_A = {"page": {"type": "choice", "instructions": "根据这段界面文字判断当前是哪个页面", "criteria": {c: SHORT[c] for c in CLASSES}}}
    q_B = {"page": {"type": "choice", "instructions": "根据这段界面文字判断当前是哪个页面", "criteria": {c: SHORT[c] for c in K6}}}
    q_C = {c: {"type": "noul", "instructions": f"界面文字中出现了{('、'.join(ATTR[c]))}这些内容吗？"} for c in CLASSES}
    q_D = {c: {"type": "noul", "instructions": f"当前界面是{SHORT[c]}吗？"} for c in CLASSES}
    q_E = {"page": {"type": "choice", "instructions": "根据这段界面文字判断当前是哪个页面", "criteria": {c: SHORT[c] for c in K6}}}

    for i, d in enumerate(sub):
        body = d["text"]
        res = judge({"body": body}, q_A)
        a = res["answers"][next(iter(res["answers"]))]
        pred = a["choice"]
        rows["A"].append({**d, "pred": pred, "correct": int(pred == d["label"]),
                          "conf": round(float(a.get("confidence", 0)), 3)})

        # B: 6类 —— 只对标签在K6中的样本有意义，其余样本记为"应拒答"实验外
        if d["label"] in K6:
            a = judge({"body": body}, q_B)["answers"]["page"]
            rows["B"].append({**d, "pred": a["choice"], "correct": int(a["choice"] == d["label"]),
                              "conf": round(float(a.get("confidence", 0)), 3)})

        res = judge({"body": body}, q_C)
        sc = {c: float(res["answers"][c]["noul"]) for c in CLASSES}
        pred = max(sc, key=sc.get)
        rows["C"].append({**d, "pred": pred, "correct": int(pred == d["label"]),
                          "margin": round(sorted(sc.values())[-1] - sorted(sc.values())[-2], 3),
                          **{f"p_{c}": round(v, 3) for c, v in sc.items()}})

        res = judge({"body": body}, q_D)
        sc = {c: float(res["answers"][c]["noul"]) for c in CLASSES}
        pred = max(sc, key=sc.get)
        rows["D"].append({**d, "pred": pred, "correct": int(pred == d["label"]),
                          "margin": round(sorted(sc.values())[-1] - sorted(sc.values())[-2], 3)})

        if d["label"] in K6:
            a = judge({"body": "以下是手机屏幕OCR识别出的界面文字：\n" + body}, q_E)["answers"]["page"]
            rows["E"].append({**d, "pred": a["choice"], "correct": int(a["choice"] == d["label"]),
                              "conf": round(float(a.get("confidence", 0)), 3)})

        # S: substring baseline（22类，同一属性表）
        sc = {c: sum(1 for kw in ATTR[c] if kw in body) for c in CLASSES}
        pred = max(sc, key=sc.get)
        rows["S"].append({**d, "pred": pred, "correct": int(pred == d["label"])})
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(sub)}", flush=True)

    print()
    for k, name in [("A", "A choice22_short"), ("B", "B choice6_short(k=6)"),
                    ("C", "C noul_attr(22)"), ("D", "D noul_short(22)"),
                    ("E", "E choice6_prefix"), ("S", "S substring_baseline(22)")]:
        r = rows[k]
        print(f"{name:28s} n={len(r):2d} acc={acc(r):.1%}")
    for k in "CD":
        margins = [x["margin"] for x in rows[k]]
        print(f"  {k} margin mean={sum(margins)/len(margins):.3f} max={max(margins):.3f}")
    print("\nC(属性noul) 混淆:", Counter((x['label'], x['pred']) for x in rows['C'] if not x['correct']).most_common(6))
    print("A(choice22) 混淆:", Counter((x['label'], x['pred']) for x in rows['A'] if not x['correct']).most_common(6))
    print("S(substring) 混淆:", Counter((x['label'], x['pred']) for x in rows['S'] if not x['correct']).most_common(6))

    # 属性命中率表（用于修订 ATTR）
    print("\n属性命中率 (类内样本命中率):")
    for c in CLASSES:
        items = [d for d in data if d["label"] == c]
        for kw in ATTR[c]:
            hit = sum(1 for it in items if kw in it["text"])
            other = sum(1 for it in data if it["label"] != c and kw in it["text"])
            flag = "OK " if hit / len(items) >= 0.8 and other == 0 else ("?? " if hit else "XX ")
            print(f"  {flag} {c:16s} [{kw}] in-class {hit}/{len(items)}  cross {other}")

    (HERE / "sweep_results.json").write_text(json.dumps(
        {k: rows[k] for k in rows}, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main()
