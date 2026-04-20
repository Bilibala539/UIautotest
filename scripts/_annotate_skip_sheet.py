"""
标注跳过用例Sheet：
1. 读取桌面ODS文件中两个Sheet的数据
2. 在跳过用例sheet中，对已有自动化覆盖的行标绿色 + 附上AW方法名
3. 使用text:span级别样式确保颜色兼容性
4. 重新生成ODS保存回桌面
"""
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from odf.opendocument import load, OpenDocumentSpreadsheet
from odf.style import Style, TextProperties, TableColumnProperties, TableCellProperties
from odf.text import P, Span
from odf.table import Table, TableColumn, TableRow, TableCell
from odf import teletype

ODS_PATH = r"C:\Users\wb.menglingzhao02\Desktop\UI自动化用例.ods"

# ============================================================
# 匹配规则：跳过用例行号(从1开始) → (测试文件, AW方法, 覆盖度说明)
# ============================================================
MATCH_MAP = {
    2:  ("test_转发文本消息.py", "forward_message(长按→转发→验证选人)", "完全覆盖"),
    3:  ("test_多选消息.py", "multi_select_message()", "部分覆盖: 多选已实现，创建群组步骤未包含"),
    5:  ("test_工作台小程序_RN.py", "pytest.skip(功能不存在)", "探索确认: 当前版本底部导航无工作台Tab"),
    6:  ("test_大搜_搜索H5小程序.py", "search(H5小程序)", "部分覆盖: 搜索功能已实现"),
    14: ("test_群会话查看pin入口.py", "pin_message()", "完全覆盖"),
    16: ("test_查看设备存储占用图表.py", "侧边栏→设置→通用→存储空间", "完全覆盖"),
    22: ("test_群下载文件.py", "send_file()", "部分覆盖: 发送文件已实现，下载验证部分"),
    34: ("test_群会话查看pin入口.py", "pin_message()", "部分覆盖: pin入口已验证，跳转定位未实现"),
    35: ("test_群会话查看pin入口.py", "pin_message()", "部分覆盖: pin已验证，操作菜单未验证"),
}


def extract_sheet_data(table):
    """从ODF Table对象提取所有行数据"""
    rows_data = []
    for row in table.getElementsByType(TableRow):
        cells = row.getElementsByType(TableCell)
        row_data = []
        for cell in cells:
            repeat = cell.getAttribute("numbercolumnsrepeated")
            text = teletype.extractText(cell).strip()
            if repeat:
                r = int(repeat)
                if r > 20 and not text:
                    # 末尾的大量空列，只保留一个空值标记
                    row_data.append(text)
                    continue
                for _ in range(r):
                    row_data.append(text)
            else:
                row_data.append(text)
        rows_data.append(row_data)
    return rows_data


def _add_cell(row, text, cell_style, text_style):
    """添加带样式的单元格（使用text:span确保颜色渲染）"""
    cell = TableCell(stylename=cell_style, valuetype="string")
    p = P()
    span = Span(stylename=text_style, text=str(text) if text else "")
    p.addElement(span)
    cell.addElement(p)
    row.addElement(cell)


def create_annotated_ods(sheet1_data, sheet2_data, sheet1_name, sheet2_name, output_path):
    """创建标注后的ODS文件"""
    doc = OpenDocumentSpreadsheet()

    # ========= 样式定义 =========

    # 标题行 - 白字深蓝底
    header_cell_style = Style(name="HdrCell", family="table-cell")
    header_cell_style.addElement(TableCellProperties(backgroundcolor="#2E5090"))
    doc.automaticstyles.addElement(header_cell_style)

    header_text_style = Style(name="HdrText", family="text")
    header_text_style.addElement(TextProperties(fontsize="11pt", fontweight="bold", color="#FFFFFF"))
    doc.automaticstyles.addElement(header_text_style)

    # 已覆盖行 - 绿色加粗字 + 浅绿底
    green_cell_style = Style(name="GrnCell", family="table-cell")
    green_cell_style.addElement(TableCellProperties(backgroundcolor="#E8F5E9"))
    doc.automaticstyles.addElement(green_cell_style)

    green_text_style = Style(name="GrnText", family="text")
    green_text_style.addElement(TextProperties(fontsize="10pt", fontweight="bold", color="#008000"))
    doc.automaticstyles.addElement(green_text_style)

    # 普通行
    normal_cell_style = Style(name="NrmCell", family="table-cell")
    doc.automaticstyles.addElement(normal_cell_style)

    normal_text_style = Style(name="NrmText", family="text")
    normal_text_style.addElement(TextProperties(fontsize="10pt", color="#333333"))
    doc.automaticstyles.addElement(normal_text_style)

    # ========= Sheet 1：原始数据原样复制 =========
    table1 = Table(name=sheet1_name)

    # 列宽
    for i in range(max(len(r) for r in sheet1_data if r)):
        cs = Style(name=f"S1Col{i}", family="table-column")
        cs.addElement(TableColumnProperties(columnwidth="5cm"))
        doc.automaticstyles.addElement(cs)
        table1.addElement(TableColumn(stylename=cs))

    for row_idx, row_data in enumerate(sheet1_data):
        tr = TableRow()
        cs = header_cell_style if row_idx == 0 else normal_cell_style
        ts = header_text_style if row_idx == 0 else normal_text_style
        for text in row_data:
            if text is not None:
                _add_cell(tr, text, cs, ts)
        table1.addElement(tr)

    doc.spreadsheet.addElement(table1)

    # ========= Sheet 2：跳过用例 + 标注 =========
    table2 = Table(name=sheet2_name)

    # 原始7列 + 新增2列(测试文件、AW方法/覆盖说明) = 9列
    col_widths_2 = ["5cm", "5cm", "8cm", "6cm", "3cm", "2.5cm", "8cm", "5cm", "6cm"]
    for i, w in enumerate(col_widths_2):
        cs = Style(name=f"S2Col{i}", family="table-column")
        cs.addElement(TableColumnProperties(columnwidth=w))
        doc.automaticstyles.addElement(cs)
        table2.addElement(TableColumn(stylename=cs))

    for row_idx, row_data in enumerate(sheet2_data):
        tr = TableRow()

        if row_idx == 0:
            # 表头行：原始7列 + 2列新表头
            cs, ts = header_cell_style, header_text_style
            # 截取前7列（原始表头）
            orig_cols = row_data[:7] if len(row_data) >= 7 else row_data
            for text in orig_cols:
                _add_cell(tr, text, cs, ts)
            # 新增表头
            _add_cell(tr, "对应测试文件", cs, ts)
            _add_cell(tr, "AW方法/覆盖说明", cs, ts)
        else:
            # 数据行
            is_matched = row_idx in MATCH_MAP
            if is_matched:
                cs, ts = green_cell_style, green_text_style
                test_file, aw_method, coverage = MATCH_MAP[row_idx]
            else:
                cs, ts = normal_cell_style, normal_text_style

            # 原始7列数据
            orig_cols = row_data[:7] if len(row_data) >= 7 else row_data
            for text in orig_cols:
                _add_cell(tr, text, cs, ts)
            # 补齐不足7列的
            for _ in range(7 - len(orig_cols)):
                _add_cell(tr, "", cs, ts)

            # 新增列
            if is_matched:
                _add_cell(tr, test_file, cs, ts)
                _add_cell(tr, f"{aw_method} [{coverage}]", cs, ts)
            else:
                _add_cell(tr, "", cs, ts)
                _add_cell(tr, "", cs, ts)

        table2.addElement(tr)

    # 汇总行
    matched_count = len(MATCH_MAP)
    total_count = len(sheet2_data) - 1  # 减去表头
    summary_tr = TableRow()
    cell = TableCell(
        stylename=header_cell_style,
        valuetype="string",
        numbercolumnsspanned=str(len(col_widths_2))
    )
    summary_text = f"汇总: 共 {total_count} 条跳过用例, 已有自动化覆盖 {matched_count} 条, 覆盖率 {matched_count/total_count*100:.1f}%"
    p = P()
    span = Span(stylename=header_text_style, text=summary_text)
    p.addElement(span)
    cell.addElement(p)
    summary_tr.addElement(cell)
    for _ in range(len(col_widths_2) - 1):
        summary_tr.addElement(TableCell())
    table2.addElement(summary_tr)

    doc.spreadsheet.addElement(table2)

    # 保存
    doc.save(output_path)
    print(f"已保存标注后的ODS文件: {output_path}")
    print(f"跳过用例共 {total_count} 条, 已标注覆盖 {matched_count} 条, 覆盖率 {matched_count/total_count*100:.1f}%")


def main():
    print("正在读取原始ODS文件...")
    doc = load(ODS_PATH)
    tables = doc.spreadsheet.getElementsByType(Table)

    sheet1_data = []
    sheet2_data = []
    sheet1_name = ""
    sheet2_name = ""

    for table in tables:
        name = table.getAttribute("name")
        data = extract_sheet_data(table)
        if "跳过" in name:
            sheet2_data = data
            sheet2_name = name
        else:
            sheet1_data = data
            sheet1_name = name

    print(f"Sheet1 [{sheet1_name}]: {len(sheet1_data)} 行")
    print(f"Sheet2 [{sheet2_name}]: {len(sheet2_data)} 行")

    # 验证匹配行号有效性
    for row_idx in MATCH_MAP:
        if row_idx >= len(sheet2_data):
            print(f"警告: Row {row_idx} 超出跳过用例范围({len(sheet2_data)})")
        else:
            title = sheet2_data[row_idx][0] if sheet2_data[row_idx] else "空行"
            test_file = MATCH_MAP[row_idx][0]
            print(f"  匹配确认 Row {row_idx}: [{title}] => {test_file}")

    print("\n正在生成标注后的ODS文件...")
    create_annotated_ods(sheet1_data, sheet2_data, sheet1_name, sheet2_name, ODS_PATH)


if __name__ == "__main__":
    main()
