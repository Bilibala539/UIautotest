"""
自动化处理会话列表及会话盒子用例
根据Excel用例内容，逐模块处理：探索→生成AW→生成用例→验证→转正

处理策略:
1. 分析每条用例的可行性
2. 按功能模块分组
3. 对可行用例生成AW和测试文件
4. 执行验证
5. 回写Excel标注结果
"""
import sys
import os
import json
import time
import logging

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import openpyxl


def load_cases(xlsx_path):
    """加载Excel用例"""
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    cases = []
    last_func = ''
    last_level = ''
    last_test = ''
    for i in range(2, ws.max_row + 1):
        func = ws.cell(i, 1).value or last_func
        level = ws.cell(i, 2).value or last_level
        title = ws.cell(i, 3).value or last_test
        pre = ws.cell(i, 4).value
        step = ws.cell(i, 5).value
        expect = ws.cell(i, 6).value

        if ws.cell(i, 1).value:
            last_func = ws.cell(i, 1).value
        if ws.cell(i, 2).value:
            last_level = ws.cell(i, 2).value
        if ws.cell(i, 3).value:
            last_test = ws.cell(i, 3).value

        # 只取有效用例（有标题且有步骤）
        if title and step:
            cases.append({
                'row': i,
                'func': func,
                'level': level,
                'title': title,
                'pre': pre,
                'step': step,
                'expect': expect
            })
    return cases, wb, ws


def analyze_case_feasibility(case):
    """
    分析用例是否可自动化

    返回:
        ('feasible', reason) - 可以自动化
        ('skip', reason) - 不可执行，需跳过
        ('existing', test_file) - 已有实现
    """
    title = case['title']
    step = case['step']
    func = case['func']
    pre = case.get('pre', '') or ''

    # 🔴 不可执行的用例
    skip_reasons = []

    # 需要多设备同步
    if '同步' in (step or '') and '其他设备' in (case.get('expect', '') or ''):
        return ('skip', '需要多设备同步验证，单设备无法实现')

    # 需要特殊账号
    if '有道外包用户' in pre or '外包' in pre:
        return ('skip', '需要特殊账号（有道外包用户），当前无此账号')

    # 需要特殊状态（请假/出差）
    if '请假' in pre or '出差' in pre:
        return ('skip', '需要账号处于特定HR状态（请假/出差），无法模拟')

    # iOS专属操作
    if 'iOS' in func and '左滑' in step:
        # Android是长按，这些用例标题包含"iOS左滑"但步骤说Android长按
        if 'Android长按' in step:
            return ('feasible', 'Android端使用长按操作替代iOS左滑')
        else:
            return ('skip', 'iOS专属左滑操作，Android端不适用')

    # 需要从好友收到消息（需要多用户协作发消息）
    if '收到' in step and ('好友' in step or '群聊' in step):
        if '消息盒子' in step:
            return ('skip', '需要从其他用户发送消息到会话盒子，需多用户协作')

    # 拖动操作（精确拖拽难以自动化验证）
    if '拖动' in step or '拖拽' in step:
        return ('skip', '拖动/拖拽操作在模拟器上难以精确控制和验证')

    # 需要大量自定义分组（需要PC端预设置）
    if '超级多的自定义分组' in (pre or ''):
        return ('skip', '需要PC端预先设置大量自定义分组，前置条件无法满足')

    # 需要群主身份
    if '群主' in (pre or '') and '自己是群主' in (pre or ''):
        return ('feasible', '需要使用群主账号操作')

    # 默认可行
    return ('feasible', '')


def get_existing_test_files():
    """获取已有的测试文件列表"""
    test_dir = r"E:\UIAutotest\tests\mumu\checklist"
    if not os.path.exists(test_dir):
        return {}
    files = {}
    for f in os.listdir(test_dir):
        if f.startswith('test_') and f.endswith('.py'):
            files[f] = os.path.join(test_dir, f)
    return files


def match_existing_test(case, existing_tests):
    """检查用例是否已有对应的测试文件"""
    title = case['title']
    # 已知映射
    mappings = {
        '关闭展开的分组栏': 'test_关闭展开的分组栏.py',
        '隐藏栏-启用未读分组': 'test_隐藏栏_启用未读分组.py',
    }
    if title in mappings and mappings[title] in existing_tests:
        return mappings[title]
    return None


def write_result_to_excel(ws, row, col, value):
    """写入结果到Excel"""
    ws.cell(row, col, value)


def main():
    xlsx_path = r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx"
    cases, wb, ws = load_cases(xlsx_path)
    existing_tests = get_existing_test_files()

    logger.info(f"共加载 {len(cases)} 条有效用例")
    logger.info(f"已有 {len(existing_tests)} 个测试文件")

    # 分析结果
    results = {
        'feasible': [],
        'skip': [],
        'existing': []
    }

    for case in cases:
        # 先检查是否已有实现
        existing = match_existing_test(case, existing_tests)
        if existing:
            results['existing'].append((case, existing))
            continue

        # 分析可行性
        status, reason = analyze_case_feasibility(case)
        if status == 'skip':
            results['skip'].append((case, reason))
        else:
            results['feasible'].append((case, reason))

    # 输出分析结果
    print("\n" + "=" * 60)
    print("用例分析结果")
    print("=" * 60)

    print(f"\n✅ 已有实现: {len(results['existing'])} 条")
    for case, test_file in results['existing']:
        print(f"  Row{case['row']}: {case['title']} -> {test_file}")

    print(f"\n🟢 可自动化: {len(results['feasible'])} 条")
    for case, reason in results['feasible']:
        note = f" ({reason})" if reason else ""
        print(f"  Row{case['row']}: [{case['func']}] {case['title']}{note}")

    print(f"\n🔴 需跳过: {len(results['skip'])} 条")
    for case, reason in results['skip']:
        print(f"  Row{case['row']}: [{case['func']}] {case['title']}")
        print(f"         原因: {reason}")

    # 将结果写入Excel第8列（安卓进度列）
    for case, test_file in results['existing']:
        write_result_to_excel(ws, case['row'], 8, f"已实现: {test_file}")

    for case, reason in results['skip']:
        write_result_to_excel(ws, case['row'], 8, f"跳过: {reason}")

    # 保存Excel（先保存分析结果，后续验证通过后再更新）
    wb.save(xlsx_path)
    logger.info(f"分析结果已写入Excel")

    return results


if __name__ == '__main__':
    results = main()
