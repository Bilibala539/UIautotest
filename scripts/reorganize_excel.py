"""
重新整理两个 Excel，分成「已通过 / 已实现 / 未实现」三类 sheet。

会话列表 Excel:
  - 3 个 sheet (已实现/skip待完善/不可执行) 是互斥的；直接全部读取
  - 已实现 sheet 里我已经在第 7 列加了状态前缀，按前缀判定具体属于哪一类

首页 Excel:
  - "全部" sheet 是总表 187 条；其他 4 个 sheet 是子集
  - 用 (功能点, 测试点) 匹配，把"已通过""待更新图片""无编辑入口""不可自动化"的状态打回每行

输出到桌面新文件。不改原文件。
"""
import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

TODAY = datetime.date.today().isoformat()


def normalize(s):
    if s is None:
        return ""
    return str(s).strip()


# ====== 状态判定 ======
def detect_status_from_text(text, source_sheet=""):
    """根据进度文字 + 源 sheet 判定 passed/implemented/todo/blocked。
    - passed: 已跑通
    - implemented: 已写代码但没通过（含失败、待验证）
    - todo: 还没写代码但理论可做（skip/待完善/缺前置/待探索）
    - blocked: App/环境不支持（不可自动化/不可执行/不可逆等）
    """
    p = normalize(text)
    sheet = normalize(source_sheet)

    # 1. 状态前缀优先（我跑批时加的）
    if p.startswith("已通过"):
        return "passed"
    if p.startswith("跳过"):
        # 跳过的具体原因决定是 todo 还是 blocked
        if any(k in p for k in ("不支持", "不可逆", "ADB", "复杂手势", "多端", "环境", "不响应", "App 不支持")):
            return "blocked"
        return "todo"
    if p.startswith("失败"):
        return "implemented"

    # 2. 关键字判定 - blocked（环境不支持的硬限制）
    if any(k in p for k in ("不可自动化", "不可执行", "不可逆", "ADB无法", "ADB 无法", "无法精确模拟", "无法模拟", "无法验证")):
        return "blocked"

    # 3. 关键字判定 - passed
    if "已通过" in p:
        return "passed"

    # 4. 关键字判定 - implemented
    if any(k in p for k in ("已实现", "已生成", "待更新", "待验证")):
        return "implemented"

    # 5. 关键字判定 - todo (理论可做但还没做)
    if p.lower().startswith("skip") or "skip" in p.lower() or "待完善" in p or "待探索" in p or "待实现" in p or "待补" in p:
        return "todo"

    # 6. sheet 名兜底
    if "已通过" in sheet:
        return "passed"
    if "已实现" in sheet or "待更新" in sheet or "无编辑" in sheet:
        return "implemented"
    if "不可自动化" in sheet or "不可执行" in sheet:
        return "blocked"
    if "skip" in sheet.lower() or "待完善" in sheet or "待探索" in sheet:
        return "todo"

    # 7. 文本为空 → todo
    return "todo"


def find_status_col(header_row):
    """优先匹配 进度/状态/result/status；'预期结果' 不算（其中的'结果'是预期不是状态）"""
    # 优先级 1：精确含'进度'或'状态'
    for idx, cell in enumerate(header_row):
        h = normalize(cell).lower()
        if any(k in h for k in ("进度", "状态", "result", "status")):
            return idx
    return len(header_row) - 1


# ====== 样式 ======
HEADER_FILL = PatternFill(start_color="305496", end_color="305496", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
PASSED_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
IMPL_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
TODO_FILL = PatternFill(start_color="FFD9B3", end_color="FFD9B3", fill_type="solid")
BLOCKED_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

OUT_COLS = [
    "功能点", "用例级别", "测试点/测试目的", "前置条件",
    "操作步骤", "预期结果", "ui自动化ios进度", "ui自动化进度", "_source_sheet"
]

OUT_WIDTHS = [16, 8, 28, 22, 30, 30, 14, 30, 14]


def write_sheet(ws, title, cases, fill=None):
    ws.title = title
    for ci, name in enumerate(OUT_COLS, 1):
        c = ws.cell(1, ci, name)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
    for ri, case in enumerate(cases, 2):
        for ci, key in enumerate(OUT_COLS, 1):
            cell = ws.cell(ri, ci, case.get(key, ""))
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if fill:
                cell.fill = fill
    for i, w in enumerate(OUT_WIDTHS, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 32
    ws.freeze_panes = "A2"


# ====== 会话列表 Excel：3 个 sheet 直接读取 ======
def organize_huihua():
    src = r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx"
    dst = rf"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子_分类整理_{TODAY}.xlsx"

    wb = load_workbook(src, data_only=True)
    cases = []
    for sname in wb.sheetnames:
        ws = wb[sname]
        if ws.max_row < 2:
            continue
        header = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
        status_col_idx = find_status_col(header)

        for r in range(2, ws.max_row + 1):
            row = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
            if not any(normalize(c) for c in row):
                continue
            功能点 = normalize(row[0]) if len(row) > 0 else ""
            级别 = normalize(row[1]) if len(row) > 1 else ""
            测试点 = normalize(row[2]) if len(row) > 2 else ""
            前置 = normalize(row[3]) if len(row) > 3 else ""
            步骤 = normalize(row[4]) if len(row) > 4 else ""
            预期 = normalize(row[5]) if len(row) > 5 else ""
            ios = normalize(row[6]) if len(row) > 6 else ""
            进度 = normalize(row[status_col_idx]) if status_col_idx < len(row) else ""

            if not 测试点 and not 步骤:
                continue

            status = detect_status_from_text(进度, sname)
            cases.append({
                "功能点": 功能点, "用例级别": 级别, "测试点/测试目的": 测试点,
                "前置条件": 前置, "操作步骤": 步骤, "预期结果": 预期,
                "ui自动化ios进度": ios, "ui自动化进度": 进度,
                "_source_sheet": sname, "_status": status,
            })

    return src, dst, cases


# ====== 首页 Excel：以"全部" sheet 为主，用其他 sheet 标状态 ======
def organize_shouye():
    src = r"C:\Users\wb.menglingzhao02\Desktop\首页其他功能_分sheet.xlsx"
    dst = rf"C:\Users\wb.menglingzhao02\Desktop\首页其他功能_分sheet_分类整理_{TODAY}.xlsx"

    wb = load_workbook(src, data_only=True)

    # 1) 把每个非"全部" sheet 的 (功能点, 测试点) 收集起来 → 该子集的状态
    subset_status = {}  # (功能点, 测试点) → status_label
    for sname in wb.sheetnames:
        if sname == "全部":
            continue
        # 该 sheet 整体决定 status
        if "已通过" in sname:
            label = "passed"
        elif "不可自动化" in sname or "不可执行" in sname:
            label = "blocked"
        else:
            # 待更新图片 / 无编辑入口 → 已实现待验证
            label = "implemented"
        ws = wb[sname]
        for r in range(2, ws.max_row + 1):
            功能点 = normalize(ws.cell(r, 1).value)
            测试点 = normalize(ws.cell(r, 3).value)
            if not 测试点:
                continue
            key = (功能点, 测试点)
            subset_status[key] = label

    # 2) 读"全部" sheet
    ws = wb["全部"]
    cases = []
    for r in range(2, ws.max_row + 1):
        功能点 = normalize(ws.cell(r, 1).value)
        级别 = normalize(ws.cell(r, 2).value)
        测试点 = normalize(ws.cell(r, 3).value)
        前置 = normalize(ws.cell(r, 4).value)
        步骤 = normalize(ws.cell(r, 5).value)
        预期 = normalize(ws.cell(r, 6).value)
        ios = normalize(ws.cell(r, 7).value)
        # 状态列：第 8 列 "安卓进度"
        进度 = normalize(ws.cell(r, 8).value)

        if not 测试点 and not 步骤:
            continue

        # 3) 优先用进度文字判，否则查 subset_status
        status = detect_status_from_text(进度, "")
        if status == "todo" and 进度 == "":
            # 进度空 → 用 subset_status 兜底
            sub = subset_status.get((功能点, 测试点))
            if sub:
                status = sub

        cases.append({
            "功能点": 功能点, "用例级别": 级别, "测试点/测试目的": 测试点,
            "前置条件": 前置, "操作步骤": 步骤, "预期结果": 预期,
            "ui自动化ios进度": ios, "ui自动化进度": 进度,
            "_source_sheet": "全部", "_status": status,
        })

    return src, dst, cases


# ====== 写出汇总 Excel ======
def write_grouped_excel(dst, cases):
    by = {"passed": [], "implemented": [], "todo": [], "blocked": []}
    for c in cases:
        by[c["_status"]].append(c)

    wb = Workbook()
    wb.remove(wb.active)

    s = wb.create_sheet()
    write_sheet(s, f"已通过 ({len(by['passed'])})", by["passed"], PASSED_FILL)
    s = wb.create_sheet()
    write_sheet(s, f"已实现 ({len(by['implemented'])})", by["implemented"], IMPL_FILL)
    s = wb.create_sheet()
    write_sheet(s, f"待实现 ({len(by['todo'])})", by["todo"], TODO_FILL)
    s = wb.create_sheet()
    write_sheet(s, f"不可实现 ({len(by['blocked'])})", by["blocked"], BLOCKED_FILL)

    s = wb.create_sheet()
    write_sheet(s, f"全部 ({len(cases)})", cases, None)
    fill_map = {
        "passed": PASSED_FILL, "implemented": IMPL_FILL,
        "todo": TODO_FILL, "blocked": BLOCKED_FILL,
    }
    for ri, c in enumerate(cases, 2):
        for ci in range(1, len(OUT_COLS) + 1):
            s.cell(ri, ci).fill = fill_map[c["_status"]]

    wb.save(dst)
    return by


def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    for fn in (organize_huihua, organize_shouye):
        src, dst, cases = fn()
        by = write_grouped_excel(dst, cases)
        print(f"\n=== {Path(src).name}")
        print(f"  共 {len(cases)} 条用例")
        print(f"  ✅ 已通过 {len(by['passed'])}")
        print(f"  🟡 已实现 {len(by['implemented'])}")
        print(f"  🟠 待实现 {len(by['todo'])}")
        print(f"  🔴 不可实现 {len(by['blocked'])}")
        print(f"  → {Path(dst).name}")


if __name__ == "__main__":
    main()
