"""
读取用户已经手工调整过的分类 Excel，按当前 4 个分类 sheet 的实际内容
重新整理输出（更新计数 + 重新生成"全部" sheet）。

输入：
  C:\\Users\\wb.menglingzhao02\\Desktop\\会话列表及会话盒子_分类整理_2026-05-21.xlsx
（同名输出，覆盖）

注意：用户可能在 不可实现/待实现 之间手工挪动了行 → 直接以当前 4 个分类 sheet 的内容为准，
不再去原 Excel 重新解析。
"""
import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

TODAY = datetime.date.today().isoformat()
TARGET = rf"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子_分类整理_{TODAY}.xlsx"

CATEGORIES = [
    ("已通过", "passed"),
    ("已实现", "implemented"),
    ("待实现", "todo"),
    ("不可实现", "blocked"),
]

OUT_COLS = [
    "功能点", "用例级别", "测试点/测试目的", "前置条件",
    "操作步骤", "预期结果", "ui自动化ios进度", "ui自动化进度", "_source_sheet"
]

OUT_WIDTHS = [16, 8, 28, 22, 30, 30, 14, 30, 14]

HEADER_FILL = PatternFill(start_color="305496", end_color="305496", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
PASSED_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
IMPL_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
TODO_FILL = PatternFill(start_color="FFD9B3", end_color="FFD9B3", fill_type="solid")
BLOCKED_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

FILL_MAP = {
    "passed": PASSED_FILL,
    "implemented": IMPL_FILL,
    "todo": TODO_FILL,
    "blocked": BLOCKED_FILL,
}


def normalize(s):
    if s is None:
        return ""
    return str(s).strip()


def find_category_sheet(wb, prefix):
    """根据前缀（如 '已通过'）找匹配的 sheet 名"""
    for s in wb.sheetnames:
        if s.startswith(prefix):
            return s
    return None


def read_cases_from_sheet(ws, status):
    cases = []
    for r in range(2, ws.max_row + 1):
        row = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
        if not any(normalize(c) for c in row):
            continue
        # 必须有功能点或测试点
        if not normalize(row[0]) and (len(row) < 3 or not normalize(row[2])):
            continue
        case = {OUT_COLS[i]: normalize(row[i]) if i < len(row) else "" for i in range(len(OUT_COLS))}
        case["_status"] = status
        cases.append(case)
    return cases


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


def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    src_wb = load_workbook(TARGET, data_only=True)

    grouped = {}
    for prefix, key in CATEGORIES:
        sname = find_category_sheet(src_wb, prefix)
        if sname is None:
            print(f"⚠️ 未找到 sheet 前缀 '{prefix}'，跳过")
            grouped[key] = []
            continue
        ws = src_wb[sname]
        cases = read_cases_from_sheet(ws, key)
        grouped[key] = cases
        print(f"  {prefix}: 读到 {len(cases)} 条")

    total_cases = []
    for _, key in CATEGORIES:
        total_cases.extend(grouped[key])

    # 写新文件
    out_wb = Workbook()
    out_wb.remove(out_wb.active)

    for prefix, key in CATEGORIES:
        n = len(grouped[key])
        s = out_wb.create_sheet()
        write_sheet(s, f"{prefix} ({n})", grouped[key], FILL_MAP[key])

    s = out_wb.create_sheet()
    write_sheet(s, f"全部 ({len(total_cases)})", total_cases, None)
    for ri, c in enumerate(total_cases, 2):
        for ci in range(1, len(OUT_COLS) + 1):
            s.cell(ri, ci).fill = FILL_MAP[c["_status"]]

    out_wb.save(TARGET)
    print(f"\n✅ 已重写 {Path(TARGET).name}")
    print(f"   共 {len(total_cases)} 条")
    for prefix, key in CATEGORIES:
        print(f"   - {prefix}: {len(grouped[key])}")


if __name__ == "__main__":
    main()
