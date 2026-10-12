"""EXP2 fix validation: does shrinking the label space help? 18 top-level vs 6 grouped."""
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
dom_cases = [c for c in cs if c["domain"]]
top_of = lambda d: d.split("/")[0].strip()

GROUPS = {
    "账号与启动": ["启动与隐私", "会话与登录"],
    "播放与内容": ["播放器", "电台", "收藏与曲库", "音乐平台聚合"],
    "导航与入口": ["首页", "主框架与导航", "搜索"],
    "设备与设置": ["设备管理与配网", "可视音箱 Vision", "视频与投屏", "设置"],
    "个人与运营": ["个人中心", "支付与会员", "帮助", "推送"],
    "智能功能": ["AI 助手"],
}
top2group = {t: g for g, ts in GROUPS.items() for t in ts}

def run(agent, labels, true_of, ins, tag):
    q = {"c": {"type": "choice", "instructions": ins, "criteria": {d: d for d in labels}}}
    acc, conf_wrong = 0, []
    for c in dom_cases:
        r = agent.predict({"body": "标题: " + c["title"] + "\n\n" + c["body"]}, q)["answers"]["c"]
        hit = r["choice"] == true_of(c["domain"])
        acc += hit
        if not hit:
            conf_wrong.append(r["confidence"])
    n = len(dom_cases)
    print("%-14s k=%2d  acc=%.3f  conf|wrong mean=%.2f max=%.2f" % (
        tag, len(labels), acc / n, statistics.mean(conf_wrong), max(conf_wrong)), flush=True)

agent = laya.load("convaiinnovations/laya-multilingual")
agent.cfg["max_len"] = 2048
INS = "这条测试用例属于哪个功能域？"
run(agent, sorted({top_of(c["domain"]) for c in dom_cases}), top_of, INS, "top-level")
run(agent, list(GROUPS), lambda d: top2group[top_of(d)], INS, "grouped")
print("DIAG6_DONE", flush=True)
