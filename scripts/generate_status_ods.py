"""
按测试状态分 Sheet 生成 ODS 文件
- Sheet1: ✅ 通过 (PASSED)
- Sheet2: ❌ 失败 (FAILED)
- Sheet3: ⏭️ 跳过 (SKIPPED)

根据最近一次执行报告 + 代码中 skip 标记 + 本轮修复结果，综合判断状态。
"""
import os
import sys
import ast
import re
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TextProperties, TableColumnProperties, TableCellProperties
from odf.text import P, Span
from odf.table import Table, TableColumn, TableRow, TableCell


# ==================== 用例状态判断 ====================

def get_skip_reason(filepath: str) -> str:
    """检查文件中是否有 pytest.mark.skip 或 pytest.skip，返回 reason"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查 module-level skip
    match = re.search(r'pytest\.skip\(["\'](.+?)["\']', content)
    if match:
        return match.group(1)

    # 检查 @pytest.mark.skip(reason="...")
    match = re.search(r'@pytest\.mark\.skip\(reason=["\'](.+?)["\']', content)
    if match:
        return match.group(1)

    return ""


def get_test_docstring(filepath: str) -> str:
    """获取测试文件的模块级 docstring"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取模块 docstring
    match = re.match(r'^"""(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1).strip().split('\n')[0]

    match = re.match(r"^'''(.*?)'''", content, re.DOTALL)
    if match:
        return match.group(1).strip().split('\n')[0]

    return ""


def get_test_class_name(filepath: str) -> str:
    """获取测试类名"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'class (Test\w+)', content)
    return match.group(1) if match else ""


def get_test_methods(filepath: str) -> list:
    """获取测试文件中所有 test_ 方法名"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return re.findall(r'def (test_\w+)\(', content)


# ==================== 状态分类数据 ====================

# 基于最近运行报告确认的通过用例
PASSED_CASES = {
    # 原报告中通过的用例
    "test_会话最新消息透出.py",
    "test_使用工具编辑图片后发送.py",
    "test_关闭展开的分组栏.py",
    "test_发送P2P消息.py",
    "test_图片复制到输入框.py",
    "test_大搜_搜索已关注服务号.py",
    "test_大搜_搜索未关注服务号.py",
    "test_大搜_搜索消息123.py",
    "test_大搜_搜索群组测试测试.py",
    "test_大搜_搜索联系人王英.py",
    "test_富文本_下划线.py",
    "test_富文本_删除线.py",
    "test_富文本_加粗.py",
    "test_富文本_字体颜色.py",
    "test_应用外分享.py",
    "test_底部导航栏_工作台.py",
    "test_截图分享.py",
    "test_扫一扫入口.py",
    "test_搜索RN小程序.py",
    "test_搜索入口_云空间选项.py",
    "test_易生活加入浮窗.py",
    "test_查看工位信息.py",
    "test_查看我的界面.py",
    "test_消息_赞.py",
    "test_消息设置_分享转发时需再次确认.py",
    "test_消息设置_消息气泡聚合显示.py",
    "test_消息设置_语音转文字AI整理.py",
    "test_消息设置_连续播放语音消息.py",
    "test_相册选图编辑后发送.py",
    # 本轮修复后验证通过的用例
    "test_group_panel_max_display.py",
    "test_conversation_avatar.py",
    "test_long_conversation_name.py",
    "test_pinned_name_truncate.py",
    "test_工作台小程序_RN.py",
}

# 基于最近运行报告确认的失败用例
FAILED_CASES = {
    "test_P2P添加自定义标签页.py",
    "test_创建2人群组.py",
    "test_删除消息.py",
    "test_合并消息.py",
    "test_合并消息图片滑动.py",
    "test_回复消息.py",
    "test_复制消息.py",
    "test_多选消息.py",
    "test_大搜_搜索H5小程序.py",
    "test_富文本_代码块.py",
    "test_富文本_引用块.py",
    "test_富文本_背景色.py",
    "test_富文本_行内代码.py",
    "test_富文本_超链接.py",
    "test_搜索群聊天内容.py",
    "test_撤回P2P消息.py",
    "test_收藏消息.py",
    "test_查看个人资料.py",
    "test_查看设备存储占用图表.py",
    "test_消息_普通链接.py",
    "test_消息历史_云文档.py",
    "test_消息历史_搜索.py",
    "test_消息设置_AI智能识别任务.py",
    "test_消息设置_AI智能识别快捷指令.py",
    "test_消息设置_双击会话背景发送语音.py",
    "test_消息设置_启用表情联想.py",
    "test_消息设置_文件自动下载.py",
    "test_消息设置_表情添加至默认分组.py",
    "test_消息设置_语音消息自动转换出文字.py",
    "test_群下载文件.py",
    "test_群会话查看pin入口.py",
    "test_翻译消息.py",
    "test_设置群公告.py",
    "test_转发文本消息.py",
    "test_长按会话预览.py",
    "test_长按图片消息编辑.py",
}


def classify_case(filename: str, filepath: str) -> str:
    """
    判断用例状态：passed / failed / skipped
    优先级：skip标记 > 已知通过列表 > 已知失败列表 > 未知(归为failed)
    """
    # 1. 检查 skip 标记
    skip_reason = get_skip_reason(filepath)
    if skip_reason:
        return "skipped"

    # 2. 检查已知通过
    if filename in PASSED_CASES:
        return "passed"

    # 3. 检查已知失败
    if filename in FAILED_CASES:
        return "failed"

    # 4. 默认归为未验证（放到 failed sheet）
    return "failed"


# ==================== ODS 生成 ====================

def create_styles(doc):
    """创建所有样式"""
    styles = {}

    # 标题行样式
    header_cell = Style(name="HeaderCell", family="table-cell")
    header_cell.addElement(TableCellProperties(backgroundcolor="#2E5090"))
    doc.automaticstyles.addElement(header_cell)
    styles["header_cell"] = header_cell

    header_text = Style(name="HeaderText", family="text")
    header_text.addElement(TextProperties(fontsize="11pt", fontweight="bold", color="#FFFFFF"))
    doc.automaticstyles.addElement(header_text)
    styles["header_text"] = header_text

    # 通过样式（绿色背景）
    passed_cell = Style(name="PassedCell", family="table-cell")
    passed_cell.addElement(TableCellProperties(backgroundcolor="#E8F5E9"))
    doc.automaticstyles.addElement(passed_cell)
    styles["passed_cell"] = passed_cell

    passed_text = Style(name="PassedText", family="text")
    passed_text.addElement(TextProperties(fontsize="10pt", color="#1B5E20"))
    doc.automaticstyles.addElement(passed_text)
    styles["passed_text"] = passed_text

    # 失败样式（红色背景）
    failed_cell = Style(name="FailedCell", family="table-cell")
    failed_cell.addElement(TableCellProperties(backgroundcolor="#FFEBEE"))
    doc.automaticstyles.addElement(failed_cell)
    styles["failed_cell"] = failed_cell

    failed_text = Style(name="FailedText", family="text")
    failed_text.addElement(TextProperties(fontsize="10pt", color="#B71C1C"))
    doc.automaticstyles.addElement(failed_text)
    styles["failed_text"] = failed_text

    # 跳过样式（灰色背景）
    skipped_cell = Style(name="SkippedCell", family="table-cell")
    skipped_cell.addElement(TableCellProperties(backgroundcolor="#F5F5F5"))
    doc.automaticstyles.addElement(skipped_cell)
    styles["skipped_cell"] = skipped_cell

    skipped_text = Style(name="SkippedText", family="text")
    skipped_text.addElement(TextProperties(fontsize="10pt", color="#616161"))
    doc.automaticstyles.addElement(skipped_text)
    styles["skipped_text"] = skipped_text

    # 列宽
    col_widths = ["1.2cm", "6cm", "8cm", "6cm", "5cm", "8cm"]
    col_styles = []
    for i, w in enumerate(col_widths):
        cs = Style(name=f"Col{i}", family="table-column")
        cs.addElement(TableColumnProperties(columnwidth=w))
        doc.automaticstyles.addElement(cs)
        col_styles.append(cs)
    styles["col_styles"] = col_styles

    return styles


def add_cell(row, text, cell_style, text_style):
    """添加带样式的单元格"""
    cell = TableCell(stylename=cell_style, valuetype="string")
    p = P()
    span = Span(stylename=text_style, text=str(text))
    p.addElement(span)
    cell.addElement(p)
    row.addElement(cell)


def create_sheet(doc, sheet_name, cases, styles, status_key):
    """创建一个 Sheet"""
    table = Table(name=sheet_name)

    # 添加列
    for cs in styles["col_styles"]:
        table.addElement(TableColumn(stylename=cs))

    # 表头
    headers = ["序号", "测试文件", "用例描述", "测试类", "测试方法", "备注"]
    header_row = TableRow()
    for h in headers:
        add_cell(header_row, h, styles["header_cell"], styles["header_text"])
    table.addElement(header_row)

    # 数据行
    cell_style = styles[f"{status_key}_cell"]
    text_style = styles[f"{status_key}_text"]

    for idx, case in enumerate(cases, 1):
        row = TableRow()
        add_cell(row, str(idx), cell_style, text_style)
        add_cell(row, case["filename"], cell_style, text_style)
        add_cell(row, case["description"], cell_style, text_style)
        add_cell(row, case["class_name"], cell_style, text_style)
        add_cell(row, ", ".join(case["methods"]), cell_style, text_style)
        add_cell(row, case.get("note", ""), cell_style, text_style)
        table.addElement(row)

    doc.spreadsheet.addElement(table)
    return len(cases)


def main():
    checklist_dir = os.path.join(PROJECT_ROOT, "tests", "mumu", "checklist")

    # 收集所有测试文件
    test_files = []
    for f in sorted(os.listdir(checklist_dir)):
        if f.startswith("test_") and f.endswith(".py"):
            test_files.append(f)

    print(f"共找到 {len(test_files)} 个测试文件")

    # 分类
    passed_list = []
    failed_list = []
    skipped_list = []

    for filename in test_files:
        filepath = os.path.join(checklist_dir, filename)
        status = classify_case(filename, filepath)

        case_info = {
            "filename": filename,
            "description": get_test_docstring(filepath),
            "class_name": get_test_class_name(filepath),
            "methods": get_test_methods(filepath),
            "note": "",
        }

        if status == "skipped":
            case_info["note"] = get_skip_reason(filepath)
            skipped_list.append(case_info)
        elif status == "passed":
            passed_list.append(case_info)
        else:
            failed_list.append(case_info)

    print(f"  ✅ 通过: {len(passed_list)}")
    print(f"  ❌ 失败: {len(failed_list)}")
    print(f"  ⏭️ 跳过: {len(skipped_list)}")

    # 生成 ODS
    doc = OpenDocumentSpreadsheet()
    styles = create_styles(doc)

    n_passed = create_sheet(doc, f"✅ 通过 ({len(passed_list)})", passed_list, styles, "passed")
    n_failed = create_sheet(doc, f"❌ 失败 ({len(failed_list)})", failed_list, styles, "failed")
    n_skipped = create_sheet(doc, f"⏭️ 跳过 ({len(skipped_list)})", skipped_list, styles, "skipped")

    output_path = os.path.join(PROJECT_ROOT, "会话列表及会话盒子_按状态分类.ods")
    doc.save(output_path)
    print(f"\n✅ ODS 文件已生成: {output_path}")
    print(f"   Sheet1: 通过 {n_passed} 条")
    print(f"   Sheet2: 失败 {n_failed} 条")
    print(f"   Sheet3: 跳过 {n_skipped} 条")


if __name__ == "__main__":
    main()
