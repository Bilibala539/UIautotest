"""重新分析所有用例的可行性 - 基于最新探索结果"""
import sys, os, logging, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
sys.stdout.reconfigure(encoding='utf-8')

import openpyxl
wb = openpyxl.load_workbook(r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx")
ws = wb.active

# Read all cases
print("=== 所有用例重新分析 ===\n")
cases = []
for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    row_data = list(row)
    if row_data[0]:
        cases.append({
            'row': row_idx,
            'module': row_data[0],
            'level': row_data[1],
            'name': row_data[2],
            'precond': row_data[3],
            'steps': row_data[4],
            'expected': row_data[5],
            'ios_status': row_data[6],
            'android_status': row_data[7]
        })

# Group cases by module
from collections import defaultdict
modules = defaultdict(list)
for c in cases:
    modules[c['module']].append(c)

# Print modules summary
print(f"Total cases: {len(cases)}")
print(f"Modules: {list(modules.keys())}")
print()

for mod, mod_cases in modules.items():
    print(f"\n{'='*60}")
    print(f"MODULE: {mod} ({len(mod_cases)} cases)")
    print(f"{'='*60}")
    for c in mod_cases:
        status = c.get('android_status', '')
        print(f"  Row {c['row']:2d}: [{c['level']}] {c['name']}")
        if status:
            print(f"         Status: {status}")
        print(f"         Steps: {c['steps']}")
        print(f"         Expected: {c['expected']}")
