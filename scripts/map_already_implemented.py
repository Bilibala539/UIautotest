"""
针对 '会话列表及会话盒子.xlsx' 的 '已实现 (50)' sheet：
1. 解析每条用例 + ui自动化进度 字段提取出对应的 test_xxx.py 文件名
2. 在 tests/mumu/checklist/ 找到对应文件
3. 输出一份 mapping 表 + 找不到的告警
"""
import json
import re
from pathlib import Path
from openpyxl import load_workbook

EXCEL = r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx"
SHEET = "已实现 (50)"
TEST_ROOT = Path(r"E:\UIAutotest\tests\mumu")

# 收集所有 test 文件 (递归)
all_py = list(TEST_ROOT.rglob("test_*.py"))
name_to_path = {p.name: p for p in all_py}

wb = load_workbook(EXCEL, data_only=True)
ws = wb[SHEET]

rows = []
for r in range(2, ws.max_row + 1):
    rec = {
        "row": r,
        "功能点": ws.cell(r, 1).value,
        "用例级别": ws.cell(r, 2).value,
        "测试点": ws.cell(r, 3).value,
        "前置条件": ws.cell(r, 4).value,
        "操作步骤": ws.cell(r, 5).value,
        "预期结果": ws.cell(r, 6).value,
        "ui自动化进度": ws.cell(r, 7).value,
    }
    # 跳过整行空
    if not any(rec[k] for k in rec if k != "row"):
        continue
    # 提取 test_xxx.py
    text = str(rec.get("ui自动化进度") or "")
    m = re.search(r"(test_[^\s\(\)（）]+\.py)", text)
    rec["test_file"] = m.group(1) if m else None
    if rec["test_file"]:
        match = name_to_path.get(rec["test_file"])
        rec["test_path"] = str(match) if match else None
    else:
        rec["test_path"] = None
    rows.append(rec)

out_path = Path(r"E:\UIAutotest\scripts\already_implemented_50.json")
out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"total rows: {len(rows)}")
print(f"rows with test_file: {sum(1 for r in rows if r['test_file'])}")
print(f"rows file located: {sum(1 for r in rows if r['test_path'])}")
print(f"rows file MISSING: {sum(1 for r in rows if r['test_file'] and not r['test_path'])}")
print(f"rows no test_file in progress text: {sum(1 for r in rows if not r['test_file'])}")
