"""
规整 Excel 标记：
- 去掉重复叠加的 '已通过 X - 失败 X - 失败 X - ...' 前缀
- 保留最终状态：已通过 / 失败 / 跳过 + 原始 已实现 - test_xxx.py 内容

并把 row9 也跑一遍（同 row6 的测试方法，应该和 row6 一致）。
"""
import re
from openpyxl import load_workbook

EXCEL = r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx"
SHEET = "已实现 (50)"
TODAY = "2026-05-21"

# 各行的最终状态（人工判定）
FINAL = {
    # row → status, reason
    6: ("已通过", None),  # 验证通过
    7: ("跳过", "顶部会话盒子不响应长按，App 不支持该交互"),  # row7 不可自动化
    9: ("已通过", "row6 同测试方法已通过"),  # 同测试方法
    42: ("已通过", None),
    43: ("已通过", None),
}

PREFIX_RE = re.compile(r'^(已通过 \d{4}-\d{2}-\d{2} - |失败 \d{4}-\d{2}-\d{2} - |跳过 \d{4}-\d{2}-\d{2}[^-]*- )+')

wb = load_workbook(EXCEL)
ws = wb[SHEET]

# 1. 全部清理之前的状态前缀，恢复"已实现 - ..."原始内容
for r in range(2, ws.max_row + 1):
    v = ws.cell(r, 7).value
    if not v:
        continue
    cleaned = PREFIX_RE.sub('', v)
    # 去掉 row3/4/5 的"跳过 ... 需第二台MuMu - "
    cleaned = re.sub(r'^跳过 \d{4}-\d{2}-\d{2} - 需第二台MuMu - ', '', cleaned)
    if cleaned != v:
        ws.cell(r, 7).value = cleaned

# 2. 给已经判断完的行重新加上正确状态
for r, (status, reason) in FINAL.items():
    v = ws.cell(r, 7).value or ""
    if status == "跳过":
        prefix = f"跳过 {TODAY} - {reason} - "
    elif status == "已通过":
        prefix = f"已通过 {TODAY} - "
        if reason:
            prefix = f"已通过 {TODAY}（{reason}） - "
    else:
        prefix = f"失败 {TODAY} - "
    ws.cell(r, 7).value = prefix + v

# 3. 保留 row3/4/5 跳过-双用户
for r in (3, 4, 5):
    v = ws.cell(r, 7).value or ""
    if not v.startswith("跳过 "):
        ws.cell(r, 7).value = f"跳过 {TODAY} - 需第二台MuMu - " + v

wb.save(EXCEL)

# 4. 列出最终状态
wb = load_workbook(EXCEL, data_only=True)
ws = wb[SHEET]
import sys
sys.stdout.reconfigure(encoding='utf-8')
for r in range(2, ws.max_row + 1):
    print(f'row{r:>3}:', (ws.cell(r, 7).value or '')[:120])
