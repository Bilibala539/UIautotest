"""Diagnose the noul saturation seen in run 1: language, max_len, instruction style."""
import json, pathlib
import laya

cases = json.loads((pathlib.Path.home() / "laya_poc" / "cases.json").read_text(encoding="utf-8"))

def body(c):
    b = "\n".join(l for l in c["content"].splitlines() if not l.startswith(("name:", "domain:")))
    return b[:900]

agent = laya.load("convaiinnovations/laya-multilingual")
A, B = cases[0], cases[50]
true_state = {"body": "标题: " + A["title"] + "\n\n" + body(A)}
sham_state = {"body": "标题: " + B["title"] + "\n\n" + body(A)}

def noul(instr):
    return {"type": "noul", "instructions": instr}

CHOICE = {"t": {"type": "choice", "instructions": "这个页面是什么?",
                "criteria": {"login": "登录页", "settings": "设置页"}}}
tests = [
    ("EN trivial TRUE ", {"body": "The sky is blue."}, noul("The text states that the sky is blue."), 1024),
    ("EN trivial FALSE", {"body": "The sky is blue."}, noul("The text states that the sky is green."), 1024),
    ("ZH trivial TRUE ", {"body": "天空是蓝色的。"}, noul("文本说天空是蓝色的。"), 1024),
    ("ZH trivial FALSE", {"body": "天空是蓝色的。"}, noul("文本说天空是绿色的。"), 1024),
    ("EN-instr ZH TRUE ", {"body": "天空是蓝色的。"}, noul("The text states that the sky is blue."), 1024),
    ("case TRUE  ml1024", true_state, noul("标题与用例内容描述的是同一个测试场景吗？"), 1024),
    ("case SHAM  ml1024", sham_state, noul("标题与用例内容描述的是同一个测试场景吗？"), 1024),
    ("case TRUE  ml2048", true_state, noul("标题与用例内容描述的是同一个测试场景吗？"), 2048),
    ("case SHAM  ml2048", sham_state, noul("标题与用例内容描述的是同一个测试场景吗？"), 2048),
]
res = agent.predict({"body": "页面显示: 用户名输入框 密码输入框 登录按钮"}, CHOICE)["answers"]["t"]
print("choice sanity: pred=%s conf=%s" % (res["choice"], res.get("confidence")), flush=True)
for name, st, q, ml in tests:
    agent.cfg["max_len"] = ml
    v = agent.predict(st, {"t": q})["answers"]["t"]["noul"]
    print("%-19s noul=%.3f  max_len=%d" % (name, v, ml), flush=True)
print("DIAG_DONE")
