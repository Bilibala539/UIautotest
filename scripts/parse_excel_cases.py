"""
读取两个 Excel 用例文件，列出所有 sheet 中每条用例的状态。
输出格式：
{
  "file": "...",
  "sheet": "...",
  "row": 2,
  "id": "TC-001",
  "title": "...",
  "steps": "...",
  "expected": "...",
  "status": "未通过" | "已通过" | ""
}
"""
import json
import sys
from pathlib import Path

from openpyxl import load_workbook

FILES = [
    r"C:\Users\wb.menglingzhao02\Desktop\首页其他功能_分sheet.xlsx",
    r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx",
]


def normalize(s):
    if s is None:
        return ""
    return str(s).strip()


def detect_columns(header_row):
    """根据表头识别每列的语义。返回列名->列索引（0 起）"""
    mapping = {}
    for idx, cell in enumerate(header_row):
        name = normalize(cell).lower()
        if not name:
            continue
        if name in ("用例编号", "id", "编号", "用例id", "case id", "case_id"):
            mapping.setdefault("id", idx)
        elif name in ("用例名称", "用例标题", "标题", "title", "用例", "用例描述", "测试点"):
            mapping.setdefault("title", idx)
        elif name in ("前置条件", "前置", "precondition"):
            mapping.setdefault("precondition", idx)
        elif name in ("步骤", "操作步骤", "测试步骤", "steps"):
            mapping.setdefault("steps", idx)
        elif name in ("预期", "预期结果", "expected", "expected result"):
            mapping.setdefault("expected", idx)
        elif name in ("结果", "执行结果", "状态", "测试结果", "status", "result", "是否通过", "通过状态"):
            mapping.setdefault("status", idx)
        elif name in ("备注", "remark", "comment"):
            mapping.setdefault("remark", idx)
    return mapping


def find_header_row(ws):
    """找到表头所在行（前 5 行内找包含 '用例' 或 'id' 等关键词的行）"""
    for r in range(1, min(6, ws.max_row + 1)):
        row = [c.value for c in ws[r]]
        joined = "|".join(normalize(c).lower() for c in row)
        if any(k in joined for k in ("用例", "步骤", "预期", "title", "case", "测试点")):
            return r, row
    # 兜底：第一行
    return 1, [c.value for c in ws[1]]


def is_passed(status_str):
    s = normalize(status_str)
    return any(k in s for k in ("通过", "pass", "PASS", "✅", "√", "ok"))


def main():
    out = []
    for file_path in FILES:
        wb = load_workbook(file_path, data_only=True)
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            header_row_idx, header_row = find_header_row(ws)
            colmap = detect_columns(header_row)
            if not colmap:
                continue
            for r in range(header_row_idx + 1, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                # 跳过整行空白
                if not any(normalize(c) for c in row):
                    continue
                rec = {
                    "file": file_path,
                    "sheet": sheet_name,
                    "row": r,
                    "id": normalize(row[colmap["id"]]) if "id" in colmap else "",
                    "title": normalize(row[colmap["title"]]) if "title" in colmap else "",
                    "precondition": normalize(row[colmap["precondition"]]) if "precondition" in colmap else "",
                    "steps": normalize(row[colmap["steps"]]) if "steps" in colmap else "",
                    "expected": normalize(row[colmap["expected"]]) if "expected" in colmap else "",
                    "status": normalize(row[colmap["status"]]) if "status" in colmap else "",
                    "remark": normalize(row[colmap["remark"]]) if "remark" in colmap else "",
                    "status_col": colmap.get("status"),
                }
                rec["passed"] = is_passed(rec["status"])
                # 至少要有 title 或 steps 才视为用例
                if not rec["title"] and not rec["steps"]:
                    continue
                out.append(rec)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    # 同时写到文件
    Path(__file__).parent.parent.joinpath("scripts/all_cases.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # 统计
    total = len(out)
    passed = sum(1 for r in out if r["passed"])
    print(f"\n=== 统计 ===", file=sys.stderr)
    print(f"总用例数: {total}", file=sys.stderr)
    print(f"已通过:   {passed}", file=sys.stderr)
    print(f"未通过:   {total - passed}", file=sys.stderr)


if __name__ == "__main__":
    main()
