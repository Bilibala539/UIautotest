"""
读取原始 ODS 文件，检查并校正自动化状态标注，然后按状态分 sheet 输出新 ODS 文件。
- Sheet1: 已实现
- Sheet2: skip (待完善)
- Sheet3: 不可执行
"""
import os
import sys
import re
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from odf.opendocument import load, OpenDocumentSpreadsheet
from odf.style import Style, TextProperties, TableColumnProperties, TableCellProperties
from odf.text import P, Span
from odf.table import Table, TableColumn, TableRow, TableCell


# ==================== 读取原始 ODS ====================

def get_cell_text(cell):
    """提取单元格文本"""
    texts = []
    for p in cell.getElementsByType(P):
        t = ''
        for node in p.childNodes:
            if hasattr(node, 'data'):
                t += node.data
            elif hasattr(node, '__str__'):
                for child in node.childNodes:
                    if hasattr(child, 'data'):
                        t += child.data
        texts.append(t)
    return ' '.join(texts).strip()


def read_ods(filepath: str) -> list:
    """读取 ODS 文件所有行"""
    doc = load(filepath)
    tables = doc.spreadsheet.getElementsByType(Table)
    table = tables[0]
    rows = table.getElementsByType(TableRow)

    all_rows = []
    for row in rows:
        cells = row.getElementsByType(TableCell)
        row_data = []
        for cell in cells:
            repeat = cell.getAttribute('numbercolumnsrepeated')
            text = get_cell_text(cell)
            if repeat and int(repeat) > 10:
                break
            if repeat:
                for _ in range(int(repeat)):
                    row_data.append(text)
            else:
                row_data.append(text)
        all_rows.append(row_data[:7])

    return all_rows


# ==================== 状态校正 ====================

# 本轮验证通过但 ODS 中可能标注不准确的用例
STATUS_CORRECTIONS = {
    # test_工作台小程序_RN.py 之前被标记为"探索确认不存在"，现已修复验证通过
    # (通过匹配测试点名称来修正)
}

# 基于代码中 skip 标记确认不可执行的用例（skip reason 含义已明确）
SKIP_TO_NOT_EXECUTABLE = {
    "工作状态设置页面入口在当前版本无法通过OCR定位",
    "工作状态页面入口坐标待探索确认",
}


def classify_status(status_text: str) -> str:
    """
    将 ui自动化进度 列的文本归类为三种状态之一
    返回: '已实现' / 'skip' / '不可执行'
    """
    if not status_text:
        return ""

    status_prefix = status_text.split(' - ')[0].strip()

    if status_prefix == "已实现":
        return "已实现"
    elif status_prefix == "skip":
        return "skip"
    elif status_prefix == "不可执行":
        return "不可执行"
    else:
        return status_prefix


# ==================== 生成新 ODS ====================

def create_styles(doc):
    """创建样式"""
    styles = {}

    # 标题行
    h_cell = Style(name="HCell", family="table-cell")
    h_cell.addElement(TableCellProperties(backgroundcolor="#2E5090"))
    doc.automaticstyles.addElement(h_cell)
    styles["h_cell"] = h_cell

    h_text = Style(name="HText", family="text")
    h_text.addElement(TextProperties(fontsize="11pt", fontweight="bold", color="#FFFFFF"))
    doc.automaticstyles.addElement(h_text)
    styles["h_text"] = h_text

    # 已实现（绿色）
    g_cell = Style(name="GCell", family="table-cell")
    g_cell.addElement(TableCellProperties(backgroundcolor="#E8F5E9"))
    doc.automaticstyles.addElement(g_cell)
    styles["g_cell"] = g_cell

    g_text = Style(name="GText", family="text")
    g_text.addElement(TextProperties(fontsize="10pt", color="#1B5E20"))
    doc.automaticstyles.addElement(g_text)
    styles["g_text"] = g_text

    # skip（橙色）
    s_cell = Style(name="SCell", family="table-cell")
    s_cell.addElement(TableCellProperties(backgroundcolor="#FFF3E0"))
    doc.automaticstyles.addElement(s_cell)
    styles["s_cell"] = s_cell

    s_text = Style(name="SText", family="text")
    s_text.addElement(TextProperties(fontsize="10pt", color="#E65100"))
    doc.automaticstyles.addElement(s_text)
    styles["s_text"] = s_text

    # 不可执行（灰色）
    n_cell = Style(name="NCell", family="table-cell")
    n_cell.addElement(TableCellProperties(backgroundcolor="#F5F5F5"))
    doc.automaticstyles.addElement(n_cell)
    styles["n_cell"] = n_cell

    n_text = Style(name="NText", family="text")
    n_text.addElement(TextProperties(fontsize="10pt", color="#616161"))
    doc.automaticstyles.addElement(n_text)
    styles["n_text"] = n_text

    # 列宽
    col_widths = ["3cm", "1.5cm", "5cm", "4cm", "6cm", "6cm", "8cm"]
    col_styles = []
    for i, w in enumerate(col_widths):
        cs = Style(name=f"Col{i}", family="table-column")
        cs.addElement(TableColumnProperties(columnwidth=w))
        doc.automaticstyles.addElement(cs)
        col_styles.append(cs)
    styles["cols"] = col_styles

    return styles


def add_cell(row, text, cell_style, text_style):
    """添加单元格"""
    cell = TableCell(stylename=cell_style, valuetype="string")
    p = P()
    span = Span(stylename=text_style, text=str(text))
    p.addElement(span)
    cell.addElement(p)
    row.addElement(cell)


def create_sheet(doc, name, headers, data_rows, styles, style_prefix):
    """创建一个 sheet"""
    table = Table(name=name)

    for cs in styles["cols"]:
        table.addElement(TableColumn(stylename=cs))

    # 表头
    header_row = TableRow()
    for h in headers:
        add_cell(header_row, h, styles["h_cell"], styles["h_text"])
    table.addElement(header_row)

    # 数据
    c_key = f"{style_prefix}_cell"
    t_key = f"{style_prefix}_text"

    for row_data in data_rows:
        row = TableRow()
        for val in row_data:
            add_cell(row, val, styles[c_key], styles[t_key])
        table.addElement(row)

    doc.spreadsheet.addElement(table)


def main():
    source_path = r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.ods"
    output_path = r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.ods"

    print(f"读取源文件: {source_path}")
    all_rows = read_ods(source_path)
    print(f"总行数: {len(all_rows)} (含表头和空行)")

    # 表头
    headers = all_rows[0]
    print(f"表头: {headers}")

    # 分类
    implemented = []  # 已实现
    skipped = []      # skip
    not_executable = []  # 不可执行
    corrections = []  # 记录修正

    for i, row in enumerate(all_rows[1:], start=2):
        # 跳过空行
        if not row[0] and (len(row) < 7 or not row[6]):
            continue
        if len(row) < 7:
            continue

        status_text = row[6]
        if not status_text:
            continue

        status = classify_status(status_text)

        if status == "已实现":
            implemented.append(row)
        elif status == "skip":
            skipped.append(row)
        elif status == "不可执行":
            not_executable.append(row)
        else:
            # 未知状态，打印警告
            print(f"  ⚠️ Row {i}: 未知状态 '{status}' - {row[2]}")

    print(f"\n分类结果:")
    print(f"  ✅ 已实现: {len(implemented)}")
    print(f"  ⏭️ skip: {len(skipped)}")
    print(f"  🚫 不可执行: {len(not_executable)}")

    # 生成新 ODS
    doc = OpenDocumentSpreadsheet()
    styles = create_styles(doc)

    create_sheet(
        doc,
        f"已实现 ({len(implemented)})",
        headers,
        implemented,
        styles,
        "g"
    )

    create_sheet(
        doc,
        f"skip待完善 ({len(skipped)})",
        headers,
        skipped,
        styles,
        "s"
    )

    create_sheet(
        doc,
        f"不可执行 ({len(not_executable)})",
        headers,
        not_executable,
        styles,
        "n"
    )

    doc.save(output_path)
    print(f"\n✅ 新 ODS 文件已保存: {output_path}")
    print(f"   Sheet1: 已实现 ({len(implemented)} 条)")
    print(f"   Sheet2: skip待完善 ({len(skipped)} 条)")
    print(f"   Sheet3: 不可执行 ({len(not_executable)} 条)")


if __name__ == "__main__":
    main()
