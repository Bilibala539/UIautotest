"""
生成UI自动化用例.ods文件
- 从知识库 app_map.json 读取已实现/未实现的功能列表
- 从 tests/mumu/checklist/ 读取已有测试文件
- 标记已实现自动化的用例为绿色字体（使用段落+span级别样式确保兼容性）
- 已自动化用例附上AW方法名称
"""
import os
import sys
import json
import glob
import io

# 修复Windows GBK编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到 sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TextProperties, TableColumnProperties, TableCellProperties, ParagraphProperties
from odf.text import P, Span
from odf.table import Table, TableColumn, TableRow, TableCell


def load_knowledge_base():
    """加载知识库 app_map.json"""
    kb_path = os.path.join(PROJECT_ROOT, "explorer_output", "knowledge", "app_map.json")
    with open(kb_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_test_files():
    """获取所有测试文件列表"""
    pattern = os.path.join(PROJECT_ROOT, "tests", "mumu", "checklist", "test_*.py")
    files = glob.glob(pattern)
    return [os.path.basename(f) for f in files]


def build_case_list(kb, test_files):
    """
    从知识库构建用例列表
    返回: [
        {
            "module": "模块名",
            "case_name": "用例名称",
            "aw_method": "AW方法",
            "aw_status": "已实现/未实现",
            "test_file": "测试文件名",
            "is_automated": True/False,
            "notes": "备注"
        },
        ...
    ]
    """
    cases = []
    features = kb.get("features", {})

    for feature_id, feature_info in features.items():
        name = feature_info.get("name", feature_id)
        aw_method = feature_info.get("aw_method", "")
        aw_status = feature_info.get("aw_status", "未实现")
        test_file = feature_info.get("test_file", "")
        notes = feature_info.get("notes", "")
        tags = feature_info.get("tags", [])
        description = feature_info.get("description", "")

        # 判断模块
        module = categorize_feature(feature_id, tags, name)

        # 判断是否已自动化
        is_automated = False
        if aw_status == "已实现" and test_file:
            tf_basename = os.path.basename(test_file)
            if tf_basename in test_files:
                is_automated = True

        cases.append({
            "module": module,
            "feature_id": feature_id,
            "case_name": name,
            "description": description,
            "aw_method": aw_method or "",
            "aw_status": aw_status,
            "test_file": test_file or "",
            "is_automated": is_automated,
            "notes": notes or ""
        })

    # 排序: 先按模块，再按是否已实现
    cases.sort(key=lambda x: (x["module"], 0 if x["is_automated"] else 1, x["case_name"]))
    return cases


def categorize_feature(feature_id, tags, name):
    """根据特征ID、标签和名称分类模块"""
    # 登录/退登
    if feature_id in ("login", "logout"):
        return "01-登录退登"

    # 侧边栏/个人资料
    if feature_id in ("open_sidebar", "view_my_profile"):
        return "02-侧边栏/个人资料"

    # 搜索
    if "搜索" in name or "search" in feature_id.lower():
        if "聊天" in name or "chat_content" in feature_id:
            return "07-群组管理"
        return "03-搜索功能"

    # 消息相关
    if any(t in str(tags) for t in ["发消息", "发送", "聊天", "撤回", "回复", "复制",
                                     "多选", "翻译", "收藏", "转发", "删除", "pin"]):
        return "04-消息操作"
    if "message" in feature_id.lower() and feature_id not in ("send_message",):
        if "rich_text" in feature_id or "hyperlink" in feature_id or "quote" in feature_id or "code" in feature_id:
            return "05-富文本编辑"
        if "settings" in feature_id.lower():
            return "06-消息设置"
        return "04-消息操作"

    # 富文本
    if "rich_text" in feature_id or "background_color" in feature_id or "font_color" in feature_id:
        return "05-富文本编辑"
    if "hyperlink" in feature_id or "quote" in feature_id or "code" in feature_id:
        return "05-富文本编辑"

    # 群组管理
    if any(k in feature_id for k in ["group", "team", "announcement", "exit_group"]):
        return "07-群组管理"

    # 日历
    if "calendar" in feature_id:
        return "08-日历/日程"

    # 图片相关
    if "image" in feature_id or "album" in feature_id:
        return "09-图片编辑"

    # 消息设置
    if "settings" in feature_id.lower():
        return "06-消息设置"

    return "10-其他功能"


def _add_styled_cell(row, text, style_name, doc_styles):
    """
    向行中添加一个带样式的单元格。
    使用 text:span 内联样式确保所有电子表格软件都能正确渲染字体颜色。

    Args:
        row: TableRow对象
        text: 单元格文本
        style_name: 样式名称键 ('header'/'green'/'normal'/'module')
        doc_styles: 包含所有样式引用的字典
    """
    cell_style = doc_styles[f"{style_name}_cell"]
    text_style = doc_styles[f"{style_name}_text"]

    cell = TableCell(stylename=cell_style, valuetype="string")
    p = P()
    span = Span(stylename=text_style, text=str(text))
    p.addElement(span)
    cell.addElement(p)
    row.addElement(cell)
    return cell


def create_ods(cases, output_path):
    """创建 ODS 文件 — 使用 text:span 内联样式保证颜色渲染兼容性"""
    doc = OpenDocumentSpreadsheet()

    # ========= 定义样式 =========
    # 策略: 每种视觉效果同时定义 cell 样式(管背景色) + text 样式(管字体颜色/粗细)
    # 在单元格内使用 <text:span> 引用 text 样式，确保 WPS/Excel/LibreOffice 都能渲染

    doc_styles = {}

    # --- 标题行 ---
    header_cell = Style(name="HeaderCell", family="table-cell")
    header_cell.addElement(TableCellProperties(backgroundcolor="#2E5090"))
    doc.automaticstyles.addElement(header_cell)
    doc_styles["header_cell"] = header_cell

    header_text = Style(name="HeaderText", family="text")
    header_text.addElement(TextProperties(
        fontsize="12pt",
        fontweight="bold",
        color="#FFFFFF"
    ))
    doc.automaticstyles.addElement(header_text)
    doc_styles["header_text"] = header_text

    # --- 已自动化(绿色) ---
    green_cell = Style(name="GreenCell", family="table-cell")
    green_cell.addElement(TableCellProperties(backgroundcolor="#E8F5E9"))
    doc.automaticstyles.addElement(green_cell)
    doc_styles["green_cell"] = green_cell

    green_text = Style(name="GreenText", family="text")
    green_text.addElement(TextProperties(
        fontsize="10pt",
        fontweight="bold",
        color="#008000"
    ))
    doc.automaticstyles.addElement(green_text)
    doc_styles["green_text"] = green_text

    # --- 未自动化(普通) ---
    normal_cell = Style(name="NormalCell", family="table-cell")
    doc.automaticstyles.addElement(normal_cell)
    doc_styles["normal_cell"] = normal_cell

    normal_text = Style(name="NormalText", family="text")
    normal_text.addElement(TextProperties(
        fontsize="10pt",
        color="#333333"
    ))
    doc.automaticstyles.addElement(normal_text)
    doc_styles["normal_text"] = normal_text

    # --- 模块分隔行 ---
    module_cell = Style(name="ModuleCell", family="table-cell")
    module_cell.addElement(TableCellProperties(backgroundcolor="#C5CAE9"))
    doc.automaticstyles.addElement(module_cell)
    doc_styles["module_cell"] = module_cell

    module_text = Style(name="ModuleText", family="text")
    module_text.addElement(TextProperties(
        fontsize="11pt",
        fontweight="bold",
        color="#1A237E"
    ))
    doc.automaticstyles.addElement(module_text)
    doc_styles["module_text"] = module_text

    # --- 列宽 ---
    col_styles = []
    col_widths = ["1.5cm", "3.5cm", "5cm", "8cm", "6cm", "2.5cm", "6cm", "2.5cm", "8cm"]
    for i, w in enumerate(col_widths):
        cs = Style(name=f"Col{i}", family="table-column")
        cs.addElement(TableColumnProperties(columnwidth=w))
        doc.automaticstyles.addElement(cs)
        col_styles.append(cs)

    # ========= 创建表格 =========
    table = Table(name="UI自动化用例清单")

    # 添加列
    for cs in col_styles:
        table.addElement(TableColumn(stylename=cs))

    # 表头行
    headers = ["序号", "模块", "用例名称", "描述", "AW方法", "状态", "测试文件", "已自动化", "备注"]
    header_row = TableRow()
    for h in headers:
        _add_styled_cell(header_row, h, "header", doc_styles)
    table.addElement(header_row)

    # 数据行
    current_module = ""
    idx = 0
    automated_count = 0
    total_count = 0

    for case in cases:
        total_count += 1

        # 模块分隔行
        if case["module"] != current_module:
            current_module = case["module"]
            module_row = TableRow()
            cell = TableCell(
                stylename=module_cell,
                valuetype="string",
                numbercolumnsspanned=str(len(headers))
            )
            p = P()
            span = Span(stylename=module_text, text=f"◆ {current_module}")
            p.addElement(span)
            cell.addElement(p)
            module_row.addElement(cell)
            for _ in range(len(headers) - 1):
                module_row.addElement(TableCell())
            table.addElement(module_row)

        idx += 1
        style_key = "green" if case["is_automated"] else "normal"
        if case["is_automated"]:
            automated_count += 1

        row = TableRow()

        # 序号
        _add_styled_cell(row, str(idx), style_key, doc_styles)
        # 模块
        _add_styled_cell(row, case["module"], style_key, doc_styles)
        # 用例名称
        _add_styled_cell(row, case["case_name"], style_key, doc_styles)
        # 描述
        _add_styled_cell(row, case["description"], style_key, doc_styles)
        # AW方法
        _add_styled_cell(row, case["aw_method"], style_key, doc_styles)
        # 状态
        _add_styled_cell(row, case["aw_status"], style_key, doc_styles)
        # 测试文件
        _add_styled_cell(row, case["test_file"], style_key, doc_styles)
        # 已自动化
        auto_text = "✅ 是" if case["is_automated"] else "❌ 否"
        _add_styled_cell(row, auto_text, style_key, doc_styles)
        # 备注
        _add_styled_cell(row, case["notes"], style_key, doc_styles)

        table.addElement(row)

    # 汇总行
    summary_row = TableRow()
    cell = TableCell(
        stylename=header_cell,
        valuetype="string",
        numbercolumnsspanned=str(len(headers))
    )
    rate = automated_count / total_count * 100 if total_count > 0 else 0
    summary_text = f"汇总: 共 {total_count} 条用例, 已自动化 {automated_count} 条, 自动化覆盖率 {rate:.1f}%"
    p = P()
    span = Span(stylename=header_text, text=summary_text)
    p.addElement(span)
    cell.addElement(p)
    summary_row.addElement(cell)
    for _ in range(len(headers) - 1):
        summary_row.addElement(TableCell())
    table.addElement(summary_row)

    doc.spreadsheet.addElement(table)

    # 保存
    doc.save(output_path)
    print(f"ODS文件已生成: {output_path}")
    print(f"共 {total_count} 条用例, 已自动化 {automated_count} 条, 覆盖率 {rate:.1f}%")


def main():
    print("正在加载知识库...")
    kb = load_knowledge_base()

    print("正在扫描测试文件...")
    test_files = get_test_files()
    print(f"   找到 {len(test_files)} 个测试文件")

    print("正在构建用例列表...")
    cases = build_case_list(kb, test_files)
    print(f"   构建了 {len(cases)} 条用例记录")

    output_path = os.path.join(PROJECT_ROOT, "UI自动化用例.ods")
    print(f"正在生成ODS文件: {output_path}")
    create_ods(cases, output_path)


if __name__ == "__main__":
    main()
